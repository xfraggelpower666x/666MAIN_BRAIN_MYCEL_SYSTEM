# Windows PowerShell 5.1 compatibility: this bootstrap is intentionally ASCII-only.
# Do not add Unicode punctuation to this file; keep user-facing Unicode in the GUI instead.
[CmdletBinding()]
param(
    [ValidateSet("Run", "Build", "Audit", "VerifyRuntime", "VerifyHost", "VerifyRelease")]
    [string]$Mode = "Run",
    [switch]$LaunchHidden,
    [switch]$SkipUpdateCheck,
    [switch]$ForceSource,
    [switch]$RequireExe,
    [string]$ShareUrl
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$Root = Split-Path -Parent $PSScriptRoot
$ManifestPath = Join-Path $PSScriptRoot "dependencies.json"
$AppPath = Join-Path $Root "app\chatbackup_gui.pyw"
$SpecPath = Join-Path $Root "666_CHATBACKUP_PC_TOOL.spec"
$ExePath = Join-Path $Root "dist\666_CHATBACKUP_PC_TOOL.exe"
$BuildVenv = Join-Path $Root ".venv-build"
$RequirementsBuild = Join-Path $Root "requirements-build.txt"
$RequirementsRuntime = Join-Path $Root "requirements-runtime.txt"
$StateRoot = Join-Path $env:LOCALAPPDATA "666SOUNDsDESIGn\666_CHATBACKUP_PC_TOOL"
$LogRoot = Join-Path $StateRoot "logs"
$StatusPath = Join-Path $StateRoot "last_bootstrap_status.json"
$Timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$LogPath = Join-Path $LogRoot ("bootstrap_{0}.log" -f $Timestamp)

New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null

function Write-Log {
    param(
        [Parameter(Mandatory = $true)][string]$Message,
        [ValidateSet("INFO", "PASS", "WARN", "ERROR", "ACTION")]
        [string]$Level = "INFO"
    )
    $line = "[{0}] [{1}] {2}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Level, $Message
    Add-Content -LiteralPath $LogPath -Value $line -Encoding UTF8
    if (-not $LaunchHidden) {
        switch ($Level) {
            "ERROR" { Write-Host $line -ForegroundColor Red }
            "WARN" { Write-Host $line -ForegroundColor Yellow }
            "PASS" { Write-Host $line -ForegroundColor Green }
            "ACTION" { Write-Host $line -ForegroundColor Cyan }
            default { Write-Host $line }
        }
    }
}

function Save-Status {
    param(
        [string]$OverallStatus,
        [string]$Summary,
        [hashtable]$Details
    )
    $payload = [ordered]@{
        schemaVersion = "1.0.0"
        tool = "666_CHATBACKUP_PC_TOOL"
        toolVersion = "1.10.5"
        timestamp = (Get-Date).ToString("o")
        mode = $Mode
        status = $OverallStatus
        summary = $Summary
        details = $Details
        logPath = $LogPath
    }
    $payload | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $StatusPath -Encoding UTF8
}

function Test-Command {
    param([Parameter(Mandatory = $true)][string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Invoke-External {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [string[]]$Arguments = @(),
        [switch]$AllowFailure
    )
    Write-Log -Level "ACTION" -Message ("Ausfuehren: {0} {1}" -f $FilePath, ($Arguments -join " "))
    & $FilePath @Arguments
    $exitCode = $LASTEXITCODE
    if (($exitCode -ne 0) -and (-not $AllowFailure)) {
        throw "Befehl fehlgeschlagen (ExitCode $exitCode): $FilePath $($Arguments -join ' ')"
    }
    return $exitCode
}

function Get-Manifest {
    if (-not (Test-Path -LiteralPath $ManifestPath)) {
        throw "Abhaengigkeitsmanifest fehlt: $ManifestPath"
    }
    return Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
}

function Get-PythonCandidates {
    $candidates = New-Object System.Collections.Generic.List[object]

    if (Test-Command "py.exe") {
        $candidates.Add([pscustomobject]@{ Kind = "launcher"; File = "py.exe"; Prefix = @("-3") })
    }
    $pythonCommand = Get-Command "python.exe" -ErrorAction SilentlyContinue
    if ($pythonCommand -and $pythonCommand.Source -notmatch "\\WindowsApps\\") {
        $candidates.Add([pscustomobject]@{ Kind = "path"; File = $pythonCommand.Source; Prefix = @() })
    }
    $python3Command = Get-Command "python3.exe" -ErrorAction SilentlyContinue
    if ($python3Command -and $python3Command.Source -notmatch "\\WindowsApps\\") {
        $candidates.Add([pscustomobject]@{ Kind = "path"; File = $python3Command.Source; Prefix = @() })
    }

    $knownRoots = New-Object System.Collections.Generic.List[string]
    if ($env:LOCALAPPDATA) {
        $knownRoots.Add((Join-Path $env:LOCALAPPDATA "Programs\Python"))
    }
    if ($env:ProgramFiles) {
        $knownRoots.Add((Join-Path $env:ProgramFiles "Python*"))
    }
    if (${env:ProgramFiles(x86)}) {
        $knownRoots.Add((Join-Path ${env:ProgramFiles(x86)} "Python*"))
    }

    foreach ($rootPattern in $knownRoots) {
        $dirs = Get-ChildItem -Path $rootPattern -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending
        foreach ($dir in $dirs) {
            $pythonExe = Join-Path $dir.FullName "python.exe"
            if (Test-Path -LiteralPath $pythonExe) {
                $candidates.Add([pscustomobject]@{ Kind = "known"; File = $pythonExe; Prefix = @() })
            }
        }
    }

    return $candidates
}

function Get-PythonInfo {
    $seen = @{}
    foreach ($candidate in Get-PythonCandidates) {
        $key = "{0}|{1}" -f $candidate.File, ($candidate.Prefix -join " ")
        if ($seen.ContainsKey($key)) { continue }
        $seen[$key] = $true
        try {
            $args = @($candidate.Prefix) + @("-c", "import json,sys; print(json.dumps({'version':sys.version.split()[0],'executable':sys.executable}))")
            $raw = & $candidate.File @args 2>$null
            if ($LASTEXITCODE -ne 0 -or -not $raw) { continue }
            $parsed = ($raw | Select-Object -Last 1) | ConvertFrom-Json
            return [pscustomobject]@{
                File = [string]$candidate.File
                Prefix = @($candidate.Prefix)
                Version = [version]$parsed.version
                VersionText = [string]$parsed.version
                Executable = [string]$parsed.executable
            }
        } catch {
            continue
        }
    }
    return $null
}

function Test-Tkinter {
    param([Parameter(Mandatory = $true)]$PythonInfo)
    $args = @($PythonInfo.Prefix) + @("-c", "import tkinter; print(tkinter.TkVersion)")
    try {
        $result = & $PythonInfo.File @args 2>$null
        if ($LASTEXITCODE -eq 0 -and $result) {
            return [pscustomobject]@{ Present = $true; Version = [string]($result | Select-Object -Last 1) }
        }
    } catch { }
    return [pscustomobject]@{ Present = $false; Version = "" }
}

function Get-ArchitectureSuffix {
    $arch = $env:PROCESSOR_ARCHITECTURE
    if ($arch -eq "ARM64") { return "-arm64.exe" }
    if ([Environment]::Is64BitOperatingSystem) { return "-amd64.exe" }
    return ".exe"
}

function Get-PythonPatchCandidates {
    param([Parameter(Mandatory = $true)][string]$MajorMinor)
    $indexUrl = "https://www.python.org/ftp/python/"
    $response = Invoke-WebRequest -Uri $indexUrl -UseBasicParsing -TimeoutSec 30
    $pattern = [regex]::Escape($MajorMinor) + '\.(\d+)/'
    $versions = foreach ($match in [regex]::Matches($response.Content, $pattern)) {
        try { [version]("{0}.{1}" -f $MajorMinor, $match.Groups[1].Value) } catch { }
    }
    return @($versions | Sort-Object -Unique -Descending)
}

function Test-RemoteFileExists {
    param([Parameter(Mandatory = $true)][string]$Url)
    try {
        $response = Invoke-WebRequest -Uri $Url -Method Head -UseBasicParsing -TimeoutSec 20
        return ($response.StatusCode -ge 200 -and $response.StatusCode -lt 400)
    } catch {
        # Some servers reject HEAD even when GET works. Probe with a tiny ranged GET.
        try {
            $headers = @{ Range = "bytes=0-0" }
            $response = Invoke-WebRequest -Uri $Url -Headers $headers -UseBasicParsing -TimeoutSec 20
            return ($response.StatusCode -ge 200 -and $response.StatusCode -lt 400)
        } catch {
            return $false
        }
    }
}

function Get-LatestPythonInstallerVersion {
    param([Parameter(Mandatory = $true)][string]$MajorMinor)
    $suffix = Get-ArchitectureSuffix
    $candidates = Get-PythonPatchCandidates -MajorMinor $MajorMinor
    foreach ($version in $candidates) {
        $versionText = $version.ToString()
        $url = "https://www.python.org/ftp/python/$versionText/python-$versionText$suffix"
        if (Test-RemoteFileExists -Url $url) {
            return $version
        }
    }
    throw "Kein verfuegbarer Windows-Installer fuer Python-Linie $MajorMinor auf python.org gefunden."
}

function Install-OfficialPython {
    param([Parameter(Mandatory = $true)][version]$Version)

    $suffix = Get-ArchitectureSuffix
    $versionText = $Version.ToString()
    $url = "https://www.python.org/ftp/python/$versionText/python-$versionText$suffix"
    $download = Join-Path $env:TEMP ("python-{0}{1}" -f $versionText, $suffix)

    Write-Log -Level "ACTION" -Message "Offiziellen Python-Installer laden: $url"
    Invoke-WebRequest -Uri $url -OutFile $download -UseBasicParsing -TimeoutSec 180

    $signature = Get-AuthenticodeSignature -LiteralPath $download
    if ($signature.Status -ne "Valid" -or $signature.SignerCertificate.Subject -notmatch "Python Software Foundation") {
        Remove-Item -LiteralPath $download -Force -ErrorAction SilentlyContinue
        throw "Sicherheitspruefung des Python-Installers fehlgeschlagen. Status: $($signature.Status)"
    }

    Write-Log -Level "PASS" -Message "Python-Installer-Signatur verifiziert: $($signature.SignerCertificate.Subject)"
    $installerArgs = @(
        "/quiet",
        "InstallAllUsers=0",
        "PrependPath=1",
        "Include_launcher=1",
        "Include_pip=1",
        "Include_tcltk=1",
        "Include_test=0",
        "Shortcuts=0"
    )
    Invoke-External -FilePath $download -Arguments $installerArgs | Out-Null
    Remove-Item -LiteralPath $download -Force -ErrorAction SilentlyContinue
}

function Install-PythonPreferred {
    param([Parameter(Mandatory = $true)][string]$PreferredLine)

    if (Test-Command "winget.exe") {
        $packageId = "Python.Python.$PreferredLine"
        Write-Log -Level "ACTION" -Message "Python fehlt oder ist zu alt. Installation ueber winget: $packageId"
        $args = @(
            "install", "--id", $packageId, "--exact", "--scope", "user", "--silent",
            "--accept-package-agreements", "--accept-source-agreements",
            "--disable-interactivity"
        )
        $code = Invoke-External -FilePath "winget.exe" -Arguments $args -AllowFailure
        if ($code -eq 0) { return }

        Write-Log -Level "WARN" -Message "winget-Benutzerinstallation schlug fehl. Zweiter Versuch ohne Scope-Vorgabe."
        $fallbackWingetArgs = @(
            "install", "--id", $packageId, "--exact", "--silent",
            "--accept-package-agreements", "--accept-source-agreements",
            "--disable-interactivity"
        )
        $code = Invoke-External -FilePath "winget.exe" -Arguments $fallbackWingetArgs -AllowFailure
        if ($code -eq 0) { return }
        Write-Log -Level "WARN" -Message "winget-Installation schlug fehl. Offizieller Python-Installer wird als Fallback verwendet."
    } else {
        Write-Log -Level "WARN" -Message "winget ist nicht verfuegbar. Offizieller Python-Installer wird verwendet."
    }

    $latest = Get-LatestPythonInstallerVersion -MajorMinor $PreferredLine
    Install-OfficialPython -Version $latest
}

function Update-PythonIfRequired {
    param(
        [Parameter(Mandatory = $true)]$PythonInfo,
        [switch]$Skip
    )
    if ($Skip) {
        Write-Log -Level "INFO" -Message "Python-Updatepruefung wurde ueber Parameter uebersprungen."
        return $PythonInfo
    }

    $line = "{0}.{1}" -f $PythonInfo.Version.Major, $PythonInfo.Version.Minor
    $packageId = "Python.Python.$line"

    if (Test-Command "winget.exe") {
        $listArgs = @("list", "--id", $packageId, "--exact", "--accept-source-agreements", "--disable-interactivity")
        & winget.exe @listArgs *> $null
        if ($LASTEXITCODE -eq 0) {
            Write-Log -Level "ACTION" -Message "winget prueft Python $line auf verfuegbare Updates."
            $upgradeArgs = @(
                "upgrade", "--id", $packageId, "--exact", "--scope", "user", "--silent",
                "--accept-package-agreements", "--accept-source-agreements",
                "--disable-interactivity"
            )
            $code = Invoke-External -FilePath "winget.exe" -Arguments $upgradeArgs -AllowFailure
            if ($code -ne 0) {
                Write-Log -Level "WARN" -Message "winget-Benutzerupdate war nicht anwendbar. Zweiter Versuch ohne Scope-Vorgabe."
                $fallbackUpgradeArgs = @(
                    "upgrade", "--id", $packageId, "--exact", "--silent",
                    "--accept-package-agreements", "--accept-source-agreements",
                    "--disable-interactivity"
                )
                $code = Invoke-External -FilePath "winget.exe" -Arguments $fallbackUpgradeArgs -AllowFailure
            }
            if ($code -eq 0) {
                $refreshed = Get-PythonInfo
                if ($refreshed) { return $refreshed }
                return $PythonInfo
            }
            Write-Log -Level "WARN" -Message "winget konnte den Patchstand nicht bestaetigen. Offizielle Python-Updatepruefung folgt."
        }
    }

    # Existing compatible Python is already a valid runtime. Patch updates are best-effort only.
    # Important: python.org may publish source-only security releases without Windows installers.
    # Therefore never infer an installable Windows patch from a directory number alone.
    try {
        $latestInstaller = Get-LatestPythonInstallerVersion -MajorMinor $line
        if ($latestInstaller -gt $PythonInfo.Version) {
            Write-Log -Level "ACTION" -Message "Optionales Python-Patchupdate verfuegbar: $($PythonInfo.VersionText) -> $latestInstaller"
            try {
                Install-OfficialPython -Version $latestInstaller
                $refreshed = Get-PythonInfo
                if ($refreshed) { return $refreshed }
            } catch {
                Write-Log -Level "WARN" -Message "Optionales Python-Patchupdate konnte nicht installiert werden; vorhandenes kompatibles Python bleibt aktiv: $($_.Exception.Message)"
            }
        } else {
            Write-Log -Level "PASS" -Message "Python ist innerhalb der verfuegbaren Windows-Installer seiner Linie aktuell: $($PythonInfo.VersionText)"
        }
    } catch {
        Write-Log -Level "WARN" -Message "Optionale Python-Patchpruefung nicht moeglich; vorhandenes kompatibles Python bleibt aktiv: $($_.Exception.Message)"
    }
    return $PythonInfo
}

function Ensure-Python {
    param($Manifest)
    $minimum = [version]$Manifest.runtime.python.minimumVersion
    $preferredLine = [string]$Manifest.runtime.python.preferredInstallLine
    $python = Get-PythonInfo

    if (-not $python -or $python.Version -lt $minimum) {
        if ($python) {
            Write-Log -Level "WARN" -Message "Python $($python.VersionText) ist aelter als Minimum $minimum."
        } else {
            Write-Log -Level "WARN" -Message "Python wurde nicht gefunden."
        }
        Install-PythonPreferred -PreferredLine $preferredLine
        $python = Get-PythonInfo
    }

    if (-not $python) {
        throw "Python konnte nach der automatischen Installation nicht gefunden werden. Log: $LogPath"
    }
    if ($python.Version -lt $minimum) {
        throw "Gefundene Python-Version $($python.VersionText) erfuellt Minimum $minimum nicht."
    }

    Write-Log -Level "PASS" -Message "Python verifiziert: $($python.VersionText) unter $($python.Executable)"
    $python = Update-PythonIfRequired -PythonInfo $python -Skip:$SkipUpdateCheck

    $tk = Test-Tkinter -PythonInfo $python
    if (-not $tk.Present) {
        Write-Log -Level "WARN" -Message "Tkinter fehlt. Python wird mit offizieller Tcl/Tk-Komponente repariert."
        $line = "{0}.{1}" -f $python.Version.Major, $python.Version.Minor
        try {
            $latest = Get-LatestPythonInstallerVersion -MajorMinor $line
            Install-OfficialPython -Version $latest
        } catch {
            Write-Log -Level "WARN" -Message "Reparatur in Python-Linie $line war nicht moeglich. Fallback auf bevorzugte stabile Linie $preferredLine."
            Install-PythonPreferred -PreferredLine $preferredLine
        }
        $python = Get-PythonInfo
        if (-not $python) { throw "Python ist nach Tkinter-Reparatur nicht verfuegbar." }
        $tk = Test-Tkinter -PythonInfo $python
    }
    if (-not $tk.Present) {
        throw "Tkinter konnte nicht installiert oder geladen werden."
    }
    Write-Log -Level "PASS" -Message "Tkinter verifiziert: Tk $($tk.Version)"

    return [pscustomobject]@{ Python = $python; Tkinter = $tk }
}

function Ensure-RuntimePackages {
    param([Parameter(Mandatory = $true)]$PythonInfo)

    if (-not (Test-Path -LiteralPath $RequirementsRuntime)) {
        throw "Runtime-Abhaengigkeiten fehlen: $RequirementsRuntime"
    }

    Write-Log -Level "ACTION" -Message "Python-Runtime-Pakete werden geprueft und bei Bedarf aktualisiert."
    Invoke-External -FilePath $PythonInfo.Executable -Arguments @("-m", "pip", "install", "--disable-pip-version-check", "--upgrade", "--user", "-r", $RequirementsRuntime) | Out-Null
    Invoke-External -FilePath $PythonInfo.Executable -Arguments @("-m", "pip", "check") | Out-Null

    $pillowVersion = & $PythonInfo.Executable -c "import PIL; print(PIL.__version__)" 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Pillow konnte nach der automatischen Installation nicht importiert werden."
    }
    $versionText = (($pillowVersion | Select-Object -Last 1).ToString()).Trim()
    Write-Log -Level "PASS" -Message "Pillow/Bildvorschau verifiziert: $versionText"
    return $versionText
}

function Ensure-BuildEnvironment {
    param([Parameter(Mandatory = $true)]$PythonInfo)

    $venvPython = Join-Path $BuildVenv "Scripts\python.exe"
    if (-not (Test-Path -LiteralPath $venvPython)) {
        Write-Log -Level "ACTION" -Message "Isolierte Build-Umgebung wird erstellt: $BuildVenv"
        $args = @("-m", "venv", $BuildVenv)
        Invoke-External -FilePath $PythonInfo.Executable -Arguments $args | Out-Null
    }

    Invoke-External -FilePath $venvPython -Arguments @("-m", "pip", "install", "--disable-pip-version-check", "--upgrade", "pip", "setuptools", "wheel") | Out-Null
    Invoke-External -FilePath $venvPython -Arguments @("-m", "pip", "install", "--disable-pip-version-check", "--upgrade", "-r", $RequirementsRuntime) | Out-Null
    Invoke-External -FilePath $venvPython -Arguments @("-m", "pip", "install", "--disable-pip-version-check", "--upgrade", "-r", $RequirementsBuild) | Out-Null
    Invoke-External -FilePath $venvPython -Arguments @("-m", "pip", "check") | Out-Null
    Write-Log -Level "PASS" -Message "Build-Abhaengigkeiten sind installiert, aktualisiert und konsistent."
    return $venvPython
}

function Start-Application {
    param(
        $PythonInfo,
        [switch]$PreferExe
    )

    $env:CHATBACKUP_BOOTSTRAP_STATUS = "PASS"
    $env:CHATBACKUP_BOOTSTRAP_STATUS_FILE = $StatusPath

    if ($PreferExe -and (Test-Path -LiteralPath $ExePath)) {
        Write-Log -Level "PASS" -Message "Standalone-EXE gefunden. Externe Python-Laufzeit wird fuer die EXE nicht benoetigt."
        Start-Process -FilePath $ExePath -WorkingDirectory $Root | Out-Null
        return
    }

    if (-not $PythonInfo) {
        throw "Fuer den Quellstart wurden keine verifizierten Python-Informationen uebergeben."
    }

    if (-not (Test-Path -LiteralPath $AppPath)) {
        throw "Anwendung fehlt: $AppPath"
    }

    $pythonw = Join-Path (Split-Path -Parent $PythonInfo.Executable) "pythonw.exe"
    if ($LaunchHidden -and (Test-Path -LiteralPath $pythonw)) {
        Start-Process -FilePath $pythonw -ArgumentList ('"{0}"' -f $AppPath) -WorkingDirectory $Root | Out-Null
    } else {
        Start-Process -FilePath $PythonInfo.Executable -ArgumentList ('"{0}"' -f $AppPath) -WorkingDirectory $Root | Out-Null
    }
    Write-Log -Level "PASS" -Message "Anwendung gestartet."
}

try {
    Write-Log -Level "INFO" -Message "Automatischer Systemstart beginnt. Modus: $Mode"
    Write-Log -Level "INFO" -Message "Projektpfad: $Root"
    $manifest = Get-Manifest

    $nodePresent = Test-Command "node.exe"
    $npmPresent = Test-Command "npm.cmd"
    Write-Log -Level "INFO" -Message ("Node.js: {0} - NOT_REQUIRED, keine Installation oder Aktualisierung." -f $(if ($nodePresent) { "vorhanden" } else { "nicht vorhanden" }))
    Write-Log -Level "INFO" -Message ("NPM: {0} - NOT_REQUIRED, keine Installation oder Aktualisierung." -f $(if ($npmPresent) { "vorhanden" } else { "nicht vorhanden" }))

    $details = @{
        nodeJs = @{ required = $false; present = $nodePresent; action = "none" }
        npm = @{ required = $false; present = $npmPresent; action = "none" }
        standaloneExe = @{ present = (Test-Path -LiteralPath $ExePath); path = $ExePath }
    }

    if ($RequireExe) {
        if (-not (Test-Path -LiteralPath $ExePath)) {
            throw "Die Windows-EXE ist noch nicht vorhanden. Fuehre zuerst BUILD_EXE.bat aus."
        }
        $details.python = @{ required = $false; reason = "standalone-exe" }
        Save-Status -OverallStatus "PASS" -Summary "Standalone-EXE ist startbereit; keine externe Runtime erforderlich." -Details $details
        Start-Application -PythonInfo $null -PreferExe
        exit 0
    }

    if (($Mode -eq "Run") -and (-not $ForceSource) -and (Test-Path -LiteralPath $ExePath)) {
        $details.python = @{ required = $false; reason = "standalone-exe" }
        Save-Status -OverallStatus "PASS" -Summary "Standalone-EXE ist startbereit; keine externe Runtime erforderlich." -Details $details
        Start-Application -PythonInfo $null -PreferExe
        exit 0
    }

    if ($Mode -eq "VerifyRelease") {
        $python = Get-PythonInfo
        if (-not $python -or $python.Version -lt [version]$manifest.runtime.python.minimumVersion) {
            throw "Fuer die Integritaetspruefung wird kompatibles Python benoetigt. Starte zuerst SYSTEM_CHECK_ONLY.bat."
        }
        & $python.Executable (Join-Path $Root "tests\release_integrity_probe.py")
        exit $LASTEXITCODE
    }

    if ($Mode -eq "VerifyHost" -and [string]::IsNullOrWhiteSpace($ShareUrl)) {
        $ShareUrl = Read-Host "Public ChatGPT Share URL"
        if ([string]::IsNullOrWhiteSpace($ShareUrl)) {
            Write-Log -Level "ERROR" -Message "Kein oeffentlicher Share-Link angegeben."
            exit 4
        }
    }

    $runtime = Ensure-Python -Manifest $manifest
    $details.python = @{
        required = $true
        version = $runtime.Python.VersionText
        executable = $runtime.Python.Executable
        minimum = [string]$manifest.runtime.python.minimumVersion
    }
    $details.tkinter = @{ required = $true; present = $true; version = $runtime.Tkinter.Version }
    $pillowVersion = Ensure-RuntimePackages -PythonInfo $runtime.Python
    $details.pillow = @{ required = $true; present = $true; version = $pillowVersion }

    if ($Mode -eq "Build") {
        $venvPython = Ensure-BuildEnvironment -PythonInfo $runtime.Python
        $details.pyinstaller = @{ required = $true; environment = $BuildVenv; python = $venvPython }
        Save-Status -OverallStatus "PASS" -Summary "Build-Umgebung ist installiert, aktualisiert und geprueft." -Details $details
        Write-Log -Level "PASS" -Message "Bootstrap fuer EXE-Build abgeschlossen."
        exit 0
    }

    if ($Mode -in @("VerifyRuntime", "VerifyHost")) {
        $python = $runtime.Python.Executable
        Save-Status -OverallStatus "PASS" -Summary "Benoetigte Runtime-Komponenten verfuegbar; Abnahme-Receipts werden separat geschrieben." -Details $details
        if ($Mode -eq "VerifyHost") {
            Write-Host "[1/3] Release Integrity..."
            & $python (Join-Path $Root "tests\release_integrity_probe.py")
            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        }
        Write-Host "Windows GUI / Runtime Readback..."
        & $python (Join-Path $Root "tests\runtime_readback_probe.py")
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        if ($Mode -eq "VerifyHost") {
            Write-Host "[3/3] Live Share importieren und Export zuruecklesen..."
            & $python (Join-Path $Root "tests\host_acceptance_probe.py") ("--share-url=" + $ShareUrl)
            exit $LASTEXITCODE
        }
        exit 0
    }

    if ($Mode -eq "Audit") {
        Save-Status -OverallStatus "PASS" -Summary "Alle benoetigten Runtime-Komponenten sind verfuegbar." -Details $details
        Write-Log -Level "PASS" -Message "Systempruefung abgeschlossen. Keine Anwendung gestartet."
        exit 0
    }

    Save-Status -OverallStatus "PASS" -Summary "Runtime ist installiert, aktualisiert und geprueft; Anwendung wird gestartet." -Details $details
    Start-Application -PythonInfo $runtime.Python
    exit 0
} catch {
    $message = $_.Exception.Message
    Write-Log -Level "ERROR" -Message $message
    Save-Status -OverallStatus "BLOCKIERT" -Summary $message -Details @{ mode = $Mode }

    if ($LaunchHidden) {
        try {
            Add-Type -AssemblyName PresentationFramework -ErrorAction Stop
            [System.Windows.MessageBox]::Show(
                "$message`n`nLogdatei:`n$LogPath",
                "666 ChatBackup PC Tool - Systemstart blockiert",
                [System.Windows.MessageBoxButton]::OK,
                [System.Windows.MessageBoxImage]::Error
            ) | Out-Null
        } catch {
            # Fehler wurde bereits vollstaendig protokolliert.
        }
    } else {
        Write-Host ""
        Write-Host "BLOCKIERT: $message" -ForegroundColor Red
        Write-Host "Logdatei: $LogPath"
    }
    exit 1
}
