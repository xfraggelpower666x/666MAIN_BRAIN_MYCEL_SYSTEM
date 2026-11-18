param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('diagnose', 'repair', 'build', 'test', 'package', 'toolstarter', 'setup', 'all', 'dev-amd64', 'dev-arm64')]
    [string]$Action
)

$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
$cache = Join-Path $project '.toolchain'
$installed = Join-Path $cache 'go'
$localGo = Join-Path $installed 'bin/go.exe'

# Die Bootstrap-Pruefung soll keine zweite Toolchain im Hintergrund laden.
$env:GOTOOLCHAIN = 'local'
Set-Location -LiteralPath $project

function Get-GoVersion([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return }
    try {
        $banner = & $Path version 2>$null
        if ($LASTEXITCODE -ne 0 -or $banner -notmatch '^go version go([0-9]+\.[0-9]+(?:\.[0-9]+)?) windows/(amd64|arm64|386)$') { return }
        $version = [version]$Matches[1]
        if ($version -lt $minimum) { return }
        $null = & $Path tool compile -V 2>$null
        if ($LASTEXITCODE -eq 0) { return $version }
    } catch {
        # Ein defekter Kandidat darf eine andere Installation nicht verdecken.
        return
    }
}

function Find-Go {
    $candidates = @(Get-Command go.exe -CommandType Application -All -ErrorAction SilentlyContinue |
        ForEach-Object { $_.Source })
    foreach ($dir in @($env:ProgramW6432, $env:ProgramFiles, ${env:ProgramFiles(x86)}, $env:LOCALAPPDATA)) {
        if ($dir) { $candidates += Join-Path $dir 'Go/bin/go.exe' }
    }
    $candidates += $localGo
    foreach ($candidate in ($candidates | Select-Object -Unique)) {
        $version = Get-GoVersion $candidate
        if ($version) {
            Write-Host "Go $version verified: $candidate"
            return $candidate
        }
    }
}

function Install-Go {
    $processor = $env:PROCESSOR_ARCHITECTURE
    if ($env:PROCESSOR_ARCHITEW6432) { $processor = $env:PROCESSOR_ARCHITEW6432 }
    $arch = switch ($processor) {
        'AMD64' { 'amd64' }
        'ARM64' { 'arm64' }
        default { throw "Unsupported Windows architecture for automatic Go installation: $processor" }
    }

    [void][IO.Directory]::CreateDirectory($cache)
    $lockPath = Join-Path $cache 'install.lock'
    try {
        $lock = [IO.File]::Open($lockPath, 'OpenOrCreate', 'ReadWrite', 'None')
    } catch [IO.IOException] {
        throw "Go installation is already running or the cache cannot be locked: $cache. $($_.Exception.Message)"
    }
    $stage = Join-Path $cache ('stage-' + [guid]::NewGuid())
    $previous = Join-Path $stage 'previous'
    try {
        if (Get-GoVersion $localGo) { return }

        [void][IO.Directory]::CreateDirectory($stage)
        if ($PSVersionTable.PSEdition -eq 'Desktop') {
            [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
        }
        Write-Host 'Reading official Go releases from go.dev ...'
        $releases = Invoke-RestMethod -Uri 'https://go.dev/dl/?mode=json' -TimeoutSec 30
        $file = $releases | Where-Object { $_.stable } | ForEach-Object { $_.files } |
            Where-Object { $_.os -eq 'windows' -and $_.arch -eq $arch -and $_.kind -eq 'archive' -and
                $_.filename -match ('^go(?<version>[0-9]+\.[0-9]+(?:\.[0-9]+)?)\.windows-' + $arch + '\.zip$') -and
                [version]$Matches['version'] -ge $minimum -and $_.sha256 -match '^[a-fA-F0-9]{64}$' } |
            Sort-Object { [version]($_.version -replace '^go', '') } -Descending |
            Select-Object -First 1
        if (-not $file) { throw "No stable Windows/$arch Go archive meeting $minimum was found." }

        $zip = Join-Path $stage $file.filename
        Write-Host "Downloading $($file.filename) ..."
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -UseBasicParsing -Uri ("https://go.dev/dl/" + $file.filename) -OutFile $zip -TimeoutSec 300
        if ((Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash -ne $file.sha256) {
            throw "SHA-256 check failed for $($file.filename)."
        }

        Write-Host 'SHA-256 verified. Extracting Go ...'
        Expand-Archive -LiteralPath $zip -DestinationPath $stage
        $candidate = Join-Path $stage 'go'
        if (-not (Get-GoVersion (Join-Path $candidate 'bin/go.exe'))) {
            throw 'The downloaded Go compiler did not pass the version and compiler checks.'
        }
        if (Test-Path -LiteralPath $installed) { Move-Item -LiteralPath $installed -Destination $previous }
        try {
            Move-Item -LiteralPath $candidate -Destination $installed
        } catch {
            if (Test-Path -LiteralPath $previous) { Move-Item -LiteralPath $previous -Destination $installed }
            throw
        }
    } finally {
        # Sicherung nur entsorgen, wenn eine Toolchain am Ziel vorhanden ist.
        if ((Test-Path -LiteralPath $installed) -or -not (Test-Path -LiteralPath $previous)) {
            Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue
        }
        $lock.Dispose()
    }
}

try {
    $directive = Select-String -LiteralPath 'go.mod' -Pattern '^go\s+([0-9]+\.[0-9]+(?:\.[0-9]+)?)\s*$'
    if (-not $directive) { throw 'The minimum Go version could not be read from go.mod.' }
    $minimum = [version]$directive.Matches[0].Groups[1].Value
    $go = Find-Go
    if (-not $go) {
        if ($Action -in @('diagnose', 'toolstarter')) {
            throw "No working Go $minimum or newer found. Run STARTEN.bat --setup or --repair for automatic installation."
        }
        Write-Host "No working Go $minimum or newer found. Installing it locally ..."
        Install-Go
        $go = Find-Go
        if (-not $go) { throw 'No working Go compiler was found after installation.' }
    }
    & $go run -buildvcs=false ./cmd/build $Action
    exit $LASTEXITCODE
} catch {
    [Console]::Error.WriteLine("666LINGUA $Action failed: $($_.Exception.Message)")
    exit 1
}
