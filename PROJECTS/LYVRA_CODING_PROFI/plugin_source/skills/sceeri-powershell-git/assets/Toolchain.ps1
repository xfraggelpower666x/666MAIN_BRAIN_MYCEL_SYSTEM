#requires -Version 5.1
[CmdletBinding()]
param(
    [ValidateSet('CheckTools','InstallTool','UpdateTool','AnalyzePowerShell')]
    [string]$Action = 'CheckTools',
    [ValidateSet('All','Git','Node','Docker','PSScriptAnalyzer')]
    [string]$Tool = 'All',
    [ValidateSet('LTS','Current')]
    [string]$NodeChannel = 'LTS',
    [ValidatePattern('^[0-9]+(?:\.[0-9]+){0,3}\z')]
    [string]$ToolVersion,
    [string]$ScriptPath,
    [switch]$Apply
)

Set-StrictMode -Version 2
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
$script:ResultCode = 1
$nodePackage = if ($NodeChannel -eq 'Current') { 'OpenJS.NodeJS' } else { 'OpenJS.NodeJS.LTS' }
$packages = @{ Git='Git.Git'; Node=$nodePackage; Docker='Docker.DockerDesktop' }

function Get-Application {
    param([string]$Name)
    Get-Command $Name -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
}

function Get-Analyzer {
    Get-Module -ListAvailable -Name PSScriptAnalyzer |
        Sort-Object Version -Descending | Select-Object -First 1
}

function Test-Tool {
    param([string]$Name, [switch]$Details)
    if ($Name -eq 'PSScriptAnalyzer') {
        $module = Get-Analyzer
        if ($module) { Write-Host "PSScriptAnalyzer: $($module.Version)"; return $true }
        Write-Host 'PSScriptAnalyzer: missing in this PowerShell host.'
        return $false
    }
    $ErrorActionPreference = 'Continue'
    $command = Get-Application ($Name.ToLowerInvariant())
    if (-not $command) { Write-Host "${Name}: not on PATH."; return $false }
    $output = & $command.Source --version
    $code = $LASTEXITCODE
    if ($code -ne 0) { Write-Host "${Name}: version probe failed ($code)."; return $false }
    Write-Host "${Name}: $($output -join ' ')"
    if ($Details -and $Name -eq 'Node') {
        $npm = Get-Application 'npm.cmd'
        if ($npm) {
            $version = & $npm.Source --version
            if ($LASTEXITCODE -eq 0) { Write-Host "npm: $version" } else { Write-Host 'npm: version probe failed.' }
        } else { Write-Host 'npm: not on PATH.' }
    }
    if ($Details -and $Name -eq 'Docker') {
        $endpoint = & $command.Source context inspect --format '{{.Endpoints.docker.Host}}' 2>$null
        if ($LASTEXITCODE -ne 0 -or $env:DOCKER_HOST -or $endpoint -notlike 'npipe://*') {
            Write-Host 'Docker engine: local Windows endpoint not verified.'
        } else {
            $server = & $command.Source version --format '{{.Server.Version}}' 2>$null
            if ($LASTEXITCODE -eq 0 -and $server) {
                Write-Host "Docker engine: $server"
            } else { Write-Host 'Docker engine: local endpoint unavailable. Check Docker Desktop or its backend.' }
        }
    }
    $true
}

function Update-PathFromWindows {
    $known = @($env:Path -split ';')
    foreach ($scope in @('Machine','User')) {
        $registered = [Environment]::GetEnvironmentVariable('Path',$scope)
        if (-not $registered) { continue }
        foreach ($part in ($registered -split ';')) {
            $path = [Environment]::ExpandEnvironmentVariables($part.Trim())
            if ($path -and $path -notin $known) { $known += $path }
        }
    }
    $env:Path = $known -join ';'
}

function Invoke-WingetTool {
    $id = $packages[$Tool]
    $winget = Get-Application 'winget.exe'
    if (-not $winget) { throw 'WinGet is unavailable. Check the Windows App Installer first.' }
    Update-PathFromWindows
    if ($Tool -eq 'Node') {
        $node = Get-Application 'node'
        foreach ($location in @($env:NVM_SYMLINK,$env:VOLTA_HOME,$env:FNM_MULTISHELL_PATH)) {
            if ($node -and $location -and $node.Source.StartsWith(
                $location.TrimEnd('\','/') + '\', [StringComparison]::OrdinalIgnoreCase)) {
                throw 'Node is selected by a version manager. Use that manager for this checkout.'
            }
        }
    }
    $listed = & $winget.Source list --id $id --exact --source winget
    $code = $LASTEXITCODE
    if ($code -notin @(0,-1978335212)) {
        $script:ResultCode = $code
        $listed | Write-Host
        throw 'WinGet could not verify the installed package.'
    }
    $present = Test-Tool $Tool
    if ($code -ne 0 -and $present) {
        throw 'The active tool is not matched to the selected WinGet package. Use its existing installer or version manager.'
    }
    if ($Action -eq 'UpdateTool' -and $code -ne 0) {
        throw 'The selected package is not installed. Use InstallTool first.'
    }
    if ($Action -eq 'InstallTool' -and $code -eq 0) {
        if ($ToolVersion) { throw 'The package is installed. Use UpdateTool to request a specific version.' }
        Write-Host "$id is already installed."
        if (-not $present) { $script:ResultCode = 3; throw 'The installed executable is not usable in this shell.' }
        return
    }
    $operation = if ($Action -eq 'InstallTool') { 'install' } else { 'upgrade' }
    $arguments = @($operation,'--id',$id,'--exact','--source','winget')
    if ($ToolVersion) { $arguments += @('--version',$ToolVersion) }
    if (-not $Apply) { Write-Host "Preview: winget $($arguments -join ' '). Re-run with -Apply."; return }

    & $winget.Source @arguments
    $code = $LASTEXITCODE
    if ($operation -eq 'upgrade' -and $code -eq -1978335189 -and -not $ToolVersion) {
        Write-Host 'WinGet reported no applicable update.'
    } elseif ($code -ne 0) {
        $script:ResultCode = $code
        throw 'WinGet did not complete the requested operation.'
    }
    & $winget.Source list --id $id --exact --source winget
    if ($LASTEXITCODE -ne 0) { throw 'WinGet package readback failed.' }
    Update-PathFromWindows
    if (-not (Test-Tool $Tool -Details)) {
        $script:ResultCode = 3
        throw 'Package reported by WinGet. Open a new terminal and rerun CheckTools to verify the executable.'
    }
}

function Install-Analyzer {
    $installed = Get-Analyzer
    if ($Action -eq 'UpdateTool' -and -not $installed) { throw 'PSScriptAnalyzer is missing. Use InstallTool first.' }
    if ($Action -eq 'InstallTool' -and $installed -and -not $ToolVersion) {
        Write-Host "PSScriptAnalyzer is already available ($($installed.Version))."
        return
    }
    if (-not $Apply) { Write-Host "Preview: $Action PSScriptAnalyzer via PSGallery for CurrentUser. Re-run with -Apply."; return }
    $repository = Get-PSRepository -Name PSGallery
    if ($repository.SourceLocation -notmatch '^https://www\.powershellgallery\.com/api/v2/?\z') {
        throw 'The registered PSGallery URL does not match the official source.'
    }
    $parameters = @{Name='PSScriptAnalyzer'; Repository='PSGallery'}
    if ($ToolVersion) { $parameters.RequiredVersion = $ToolVersion }
    $target = Find-Module @parameters
    if ($installed -and [version]$installed.Version -ge [version]$target.Version) {
        if ($ToolVersion -and [version]$installed.Version -gt [version]$target.Version) {
            throw 'The requested version is older than the active analyzer.'
        }
        Write-Host "PSScriptAnalyzer already satisfies the request ($($installed.Version))."
        return
    }
    $parameters.RequiredVersion = $target.Version.ToString()
    Install-Module @parameters -Scope CurrentUser
    $actual = Get-Analyzer
    if (-not $actual -or [version]$actual.Version -ne [version]$target.Version) {
        throw 'Installed analyzer version could not be confirmed in this PowerShell host.'
    }
    Write-Host "PSScriptAnalyzer verified: $($actual.Version)"
}

try {
    switch ($Action) {
        'CheckTools' {
            $targets = if ($Tool -eq 'All') { 'Git','Node','Docker','PSScriptAnalyzer' } else { @($Tool) }
            $healthy = $true
            foreach ($target in $targets) { if (-not (Test-Tool $target -Details)) { $healthy = $false } }
            if (-not $healthy) { exit 3 }
        }
        'AnalyzePowerShell' {
            if (-not $ScriptPath) { throw 'Supply -ScriptPath for the PowerShell file.' }
            $file = Get-Item -LiteralPath $ScriptPath
            if ($file.PSIsContainer -or $file.Extension -notin @('.ps1','.psm1','.psd1')) {
                throw 'Use a .ps1, .psm1 or .psd1 file.'
            }
            $tokens = $null
            $parseErrors = $null
            $null = [System.Management.Automation.Language.Parser]::ParseFile($file.FullName,[ref]$tokens,[ref]$parseErrors)
            if ($parseErrors.Count) { $parseErrors | Format-Table -AutoSize; exit 1 }
            $module = Get-Analyzer
            if (-not $module) { throw 'Syntax parsed. Install PSScriptAnalyzer before running static analysis.' }
            Import-Module -Name $module.Path -ErrorAction Stop
            $source = Get-Content -LiteralPath $file.FullName -Raw
            if ([string]::IsNullOrWhiteSpace($source)) {
                Write-Host 'PowerShell syntax passed. The file has no content to analyze.'
                break
            }
            $findings = @(Invoke-ScriptAnalyzer -ScriptDefinition $source -Severity @('Error','Warning','Information'))
            if ($findings.Count) { $findings | Format-Table RuleName,Severity,Line,Message -Wrap }
            else { Write-Host 'PowerShell syntax and static analysis passed without findings.' }
            if (@($findings | Where-Object { $_.Severity -eq 'Error' }).Count) { exit 1 }
        }
        default {
            if ($Tool -eq 'All') { throw 'Choose one tool for installation or update.' }
            if ($Tool -eq 'PSScriptAnalyzer') { Install-Analyzer } else { Invoke-WingetTool }
        }
    }
    exit 0
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit $script:ResultCode
}
