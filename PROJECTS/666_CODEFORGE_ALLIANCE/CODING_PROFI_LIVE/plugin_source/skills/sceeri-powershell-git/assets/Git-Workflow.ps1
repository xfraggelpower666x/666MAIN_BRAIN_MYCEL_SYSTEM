#requires -Version 5.1
[CmdletBinding()]
param(
    [ValidateSet('Status','VerifyRemote','Fetch','VerifyBundle','ImportBundle','Push',
        'CheckTools','InstallTool','UpdateTool','AnalyzePowerShell')]
    [string]$Action = 'Status',
    [string]$Repository = $PSScriptRoot,
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9._-]*$')]
    [string]$Remote = 'origin',
    [string]$ExpectedUrl,
    [string]$Branch,
    [string]$ExpectedCommit,
    [string]$ExpectedRemoteCommit,
    [string]$Bundle,
    [string]$BundleBranch,
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
# Native Git exit codes are handled explicitly in PowerShell 5.1 and 7.
$PSNativeCommandUseErrorActionPreference = $false
$script:GitExit = 1

if ($Action -in 'CheckTools','InstallTool','UpdateTool','AnalyzePowerShell') {
    $toolchain = Join-Path $PSScriptRoot 'Toolchain.ps1'
    if (-not (Test-Path -LiteralPath $toolchain -PathType Leaf)) {
        [Console]::Error.WriteLine('Toolchain.ps1 was not found next to Git-Workflow.ps1.')
        exit 2
    }
    $parameters = @{Action=$Action; Tool=$Tool; NodeChannel=$NodeChannel; Apply=$Apply}
    if ($ToolVersion) { $parameters.ToolVersion = $ToolVersion }
    if ($ScriptPath) { $parameters.ScriptPath = $ScriptPath }
    & $toolchain @parameters
    exit $LASTEXITCODE
}

function Invoke-Git {
    param([string[]]$Arguments, [int[]]$AllowedExit = @(0))
    $output = & $script:Git -C $script:Root @Arguments
    $code = $LASTEXITCODE
    if ($code -notin $AllowedExit) {
        $script:GitExit = $code
        throw "Git command '$($Arguments[0])' failed (exit $code)."
    }
    $script:LastGitExit = $code
    $output
}

function Get-BranchRef {
    param([string]$Name)
    if ([string]::IsNullOrWhiteSpace($Name) -or $Name.StartsWith('-') -or $Name.StartsWith('refs/')) {
        throw 'Supply a short branch name, such as integration/release.'
    }
    $ref = 'refs/heads/' + $Name
    Invoke-Git -Arguments @('check-ref-format', $ref) | Out-Null
    $ref
}

function Assert-Commit {
    param([string]$Value, [string]$Label)
    if ($Value -notmatch '^(?:[0-9a-f]{40}|[0-9a-f]{64})$') {
        throw "$Label must be a complete commit SHA."
    }
}

function Assert-Remote {
    # No embedded credentials or unexpected transport. Compare the effective Git URLs.
    if ($ExpectedUrl -cnotmatch '^(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)[A-Za-z0-9-]+/[A-Za-z0-9_.-]+$') {
        throw 'Supply the exact HTTPS or SSH GitHub URL without credentials as -ExpectedUrl.'
    }
    $readUrls = @(Invoke-Git -Arguments @('remote','get-url','--all',$Remote))
    $writeUrls = @(Invoke-Git -Arguments @('remote','get-url','--push','--all',$Remote))
    if ($readUrls.Count -ne 1 -or $writeUrls.Count -ne 1 -or
        $readUrls[0] -cne $ExpectedUrl -or $writeUrls[0] -cne $ExpectedUrl) {
        throw 'The effective fetch or push URL does not match the project target.'
    }
}

function Get-RemoteCommit {
    param([string]$Ref)
    $rows = @(Invoke-Git -Arguments @('ls-remote','--exit-code','--refs',$Remote,$Ref) -AllowedExit @(0,2))
    if ($script:LastGitExit -eq 2) { return 'missing' }
    if ($rows.Count -ne 1) { throw 'Remote returned an unexpected number of matching refs.' }
    $parts = $rows[0] -split "`t"
    if ($parts.Count -ne 2 -or $parts[1] -cne $Ref) { throw 'Remote returned an unexpected ref.' }
    Assert-Commit $parts[0] 'Remote commit'
    $parts[0]
}

try {
    foreach ($name in @('GIT_DIR','GIT_WORK_TREE','GIT_COMMON_DIR','GIT_NAMESPACE','GIT_INDEX_FILE')) {
        if ([Environment]::GetEnvironmentVariable($name)) {
            throw "Clear $name before using this project launcher."
        }
    }
    $script:Git = (Get-Command git -CommandType Application | Select-Object -First 1).Source
    $script:Root = (Get-Item -LiteralPath $Repository).FullName
    $script:Root = [string](Invoke-Git -Arguments @('rev-parse','--show-toplevel'))

    switch ($Action) {
        'Status' {
            Invoke-Git -Arguments @('status','--short','--branch')
            Invoke-Git -Arguments @('rev-parse','--verify','HEAD')
        }
        { $_ -in 'VerifyBundle','ImportBundle' } {
            $file = Get-Item -LiteralPath $Bundle
            if ($file.PSIsContainer) { throw 'Bundle must be a file.' }
            $source = Get-BranchRef $BundleBranch
            Assert-Commit $ExpectedCommit 'Expected bundle commit'
            $heads = @(Invoke-Git -Arguments @('bundle','list-heads',$file.FullName,$source))
            if ($heads.Count -ne 1 -or $heads[0] -ine "$ExpectedCommit $source") {
                throw 'Bundle does not contain the expected source branch and commit.'
            }
            Invoke-Git -Arguments @('bundle','verify',$file.FullName)
            if ($Action -eq 'VerifyBundle') { break }
            $target = Get-BranchRef $Branch
            if (-not $Apply) {
                Write-Output "Preview: import $ExpectedCommit into the new local branch $target. Re-run with -Apply."
                break
            }
            Invoke-Git -Arguments @('fetch','--no-tags','--no-write-fetch-head','--refmap=',$file.FullName,$source)
            Invoke-Git -Arguments @('cat-file','-e',"${ExpectedCommit}^{commit}")
            $zero = '0' * $ExpectedCommit.Length
            Invoke-Git -Arguments @('update-ref','--no-deref',$target,$ExpectedCommit,$zero)
            $actual = Invoke-Git -Arguments @('rev-parse','--verify',$target)
            if ($actual -ine $ExpectedCommit) { throw 'Local branch readback does not match the bundle commit.' }
            Write-Output "Verified local branch $target at $actual."
        }
        default {
            Assert-Remote
            $target = Get-BranchRef $Branch
            if ($Action -eq 'VerifyRemote') {
                $actual = Get-RemoteCommit $target
                if ($ExpectedCommit) {
                    Assert-Commit $ExpectedCommit 'Expected remote result'
                    if ($actual -ine $ExpectedCommit) { throw "Remote branch mismatch: $actual." }
                }
                Write-Output "${target}: $actual"
                break
            }
            if ($Action -eq 'Fetch') {
                if ($ExpectedCommit) {
                    Assert-Commit $ExpectedCommit 'Expected fetch commit'
                    if ((Get-RemoteCommit $target) -ine $ExpectedCommit) { throw 'Remote branch differs from the expected fetch commit.' }
                }
                Invoke-Git -Arguments @('fetch','--no-tags','--refmap=',$Remote,$target)
                $actual = Invoke-Git -Arguments @('rev-parse','--verify','FETCH_HEAD')
                if ($ExpectedCommit -and $actual -ine $ExpectedCommit) { throw 'FETCH_HEAD readback does not match.' }
                Write-Output "FETCH_HEAD: $actual"
                break
            }
            Assert-Commit $ExpectedCommit 'Expected local commit'
            if ($ExpectedRemoteCommit -cne 'missing') { Assert-Commit $ExpectedRemoteCommit 'Expected remote commit' }
            $local = Invoke-Git -Arguments @('rev-parse','--verify',$target)
            if ($local -ine $ExpectedCommit) { throw 'Local branch differs from the expected commit.' }
            if ((Get-RemoteCommit $target) -ine $ExpectedRemoteCommit) { throw 'Remote branch moved. Read back the target before retrying.' }
            $refspec = "${local}:${target}"
            if (-not $Apply) {
                Invoke-Git -Arguments @('push','--dry-run','--porcelain','--no-follow-tags','--recurse-submodules=no',$Remote,$refspec)
                Write-Output 'Preview only. Re-run with -Apply to publish this exact commit.'
                break
            }
            Invoke-Git -Arguments @('push','--porcelain','--no-follow-tags','--recurse-submodules=no',$Remote,$refspec)
            $actual = Get-RemoteCommit $target
            if ($actual -ine $local) { throw 'Push result is unconfirmed. Check the remote branch before retrying.' }
            Write-Output "Verified GitHub branch $target at $actual."
        }
    }
    exit 0
}
catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit $script:GitExit
}
