# R13 COMPLETE REPAIR: Python discovery, safe recovery and verified setup.
# Windows PowerShell 5.1 kompatibel. Aktionen nur nach Menueauswahl.
param(
    [ValidateSet('Diagnose','Setup','Update','Verify','PythonRecovery')][string]$Action='Diagnose',
    [string]$ProjectRoot=''
)
$ErrorActionPreference = 'Stop'
# Der Projektpfad kommt standardmaessig aus der Position dieses Skripts.
# Dadurch kann kein CMD-Argument mit abschliessendem Backslash/Anfuehrungszeichen
# den PowerShell-Native-Argumentparser beschaedigen.
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
} else {
    # Rueckwaertskompatibilitaet fuer manuelle Aufrufe mit altem kaputtem
    # Windows-Argument: Pfad in Anfuehrungszeichen + abschliessender Slash.
    $ProjectRoot = $ProjectRoot.Trim().Trim('"').TrimEnd('\','/')
}
$root = (Resolve-Path -LiteralPath $ProjectRoot -ErrorAction Stop).ProviderPath

$venv = Join-Path $root '.venv\Scripts\python.exe'
$reportDir = Join-Path $root 'TOOLS\REPORTS'
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
$report = [ordered]@{
    schema='klrw.r13.repair.complete.v1'; action=$Action; timestamp=(Get-Date).ToString('o')
    platform=[Environment]::OSVersion.VersionString
    python='MISSING'; python_path=''; python_version=''
    launcher=''; winget='MISSING'; pip='MISSING'; local_venv='MISSING'
    powershell=$PSVersionTable.PSVersion.ToString(); modules=[ordered]@{}; python_candidates=@()
    smartctl='OPTIONAL_MISSING'; result='PARTIAL'; messages=@(); winget_install_exit=$null; installed_python_packages=@(); python_search_notes=@(); registry_python_paths=@(); python_remediation=''; python_scan_roots=@(); python_registry_hints=@()
}
function Note([string]$message) {
    Write-Host $message
    $report.messages += $message
}
# A verified interpreter must execute actual Python code successfully; registry and winget
# inventory entries are NOT proof that the executable is usable.
function Invoke-PythonCheck([string]$exe, [string[]]$preArgs) {
    # B-12: Native Prozesse nicht ueber PowerShells Fehlerstream-Umleitung
    # validieren. Unter Windows PowerShell 5.1 kann native stderr-Zeilen
    # als ErrorRecord behandeln. Stattdessen kontrollierter .NET-Prozessstart.
    # Nur --version wird ausgefuehrt, KEIN Python-Projektcode.
    # Historischer Versionsvertrag: sys.version_info >= (3,10), nun Parser-Pruefung.
    # Frueherer Aufruf @('--version') bleibt inhaltlich erhalten.
    if ([string]::IsNullOrWhiteSpace($exe) -or -not (Test-Path -LiteralPath $exe -PathType Leaf)) {
        $report.python_search_notes += ('python not_found: ' + $exe)
        return $null
    }
    $process = $null
    try {
        $start = New-Object System.Diagnostics.ProcessStartInfo
        $start.FileName = $exe
        $argsList = New-Object 'System.Collections.Generic.List[string]'
        foreach ($arg in @($preArgs)) { if (-not [string]::IsNullOrWhiteSpace($arg)) { [void]$argsList.Add($arg) } }
        [void]$argsList.Add('--version')
        $start.Arguments = $argsList -join ' '
        $start.UseShellExecute = $false
        $start.RedirectStandardOutput = $true
        $start.RedirectStandardError = $true
        $start.CreateNoWindow = $true
        $process = New-Object System.Diagnostics.Process
        $process.StartInfo = $start
        if (-not $process.Start()) { throw 'process_start_returned_false' }
        if (-not $process.WaitForExit(10000)) {
            try { $process.Kill() } catch {}
            $report.python_search_notes += ('python version timeout: ' + $exe)
            return $null
        }
        $stdout = $process.StandardOutput.ReadToEnd().Trim()
        $stderr = $process.StandardError.ReadToEnd().Trim()
        $exitCode = $process.ExitCode
        # Python kann die Version je nach Launcher auf stdout oder stderr ausgeben.
        $versionMatch = [regex]::Match(($stdout + "`n" + $stderr), '(?im)^\s*Python\s+(\d+)\.(\d+)(?:\.(\d+))?\s*$')
        if ($exitCode -eq 0 -and $versionMatch.Success) {
            $major=[int]$versionMatch.Groups[1].Value
            $minor=[int]$versionMatch.Groups[2].Value
            $patch=if ($versionMatch.Groups[3].Success) { [int]$versionMatch.Groups[3].Value } else { 0 }
            if ($major -gt 3 -or ($major -eq 3 -and $minor -ge 10)) {
                return ('{0}.{1}.{2}' -f $major,$minor,$patch)
            }
            $report.python_search_notes += ('python rejected (below 3.10): ' + $exe)
            return $null
        }
        # Diagnose im JSON: Native Prozesse koennen starten und trotzdem ungueltig sein.
        # Keine Store-Alias-Fehlermeldung als gueltiges Python akzeptieren.
        $reason = 'python version check failed: ' + $exe + ' exit=' + $exitCode
        $reason += ' stdout=' + $stdout.Substring(0,[Math]::Min(240,$stdout.Length))
        $reason += ' stderr=' + $stderr.Substring(0,[Math]::Min(240,$stderr.Length))
        $report.python_search_notes += $reason
    } catch {
        $report.python_search_notes += ('python version exception: ' + $exe + ' -> ' + $_.Exception.Message)
    } finally {
        if ($null -ne $process) { $process.Dispose() }
    }
    return $null
}
# Ermittelt bereits registrierte Python-Pakete unabhaengig vom PATH.
# Rueckgabe ist ausschliesslich eine Liste; kein winget-Installationsversuch.
function Get-InstalledPythonPackages {
    $found = New-Object System.Collections.ArrayList
    foreach ($base in @('HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall',
                        'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
                        'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall')) {
        if (-not (Test-Path -LiteralPath $base)) { continue }
        foreach ($entry in @(Get-ChildItem -LiteralPath $base -ErrorAction SilentlyContinue)) {
            try {
                $info=Get-ItemProperty -LiteralPath $entry.PSPath -ErrorAction Stop
                if ($info.DisplayName -match '(?i)^Python\s+3\.(1[0-9])(?:\.|\s|$)') {
                    [void]$found.Add(@{name=[string]$info.DisplayName; location=[string]$info.InstallLocation; icon=[string]$info.DisplayIcon; uninstall=[string]$info.UninstallString; install_source=[string]$info.InstallSource; source='uninstall-registry'})
                }
            } catch {}
        }
    }
    return $found.ToArray()
}
function Get-WingetPythonInventory {
    $entries = @(Get-InstalledPythonPackages)
    # winget erkennt Pakete manchmal ohne gueltigen Python-Registry-Key.
    if (Get-Command winget.exe -ErrorAction SilentlyContinue) {
        try {
            $output = @(& winget.exe list --id Python.Python.3.13 --exact --source winget --disable-interactivity 2>$null)
            $raw = $output -join "`n"
            if ($LASTEXITCODE -eq 0 -and $raw -match 'Python\.Python\.3\.13') {
                $entries += @{name='Python.Python.3.13'; location=''; source='winget-list'}
            }
        } catch {
            $report.python_search_notes += ('winget-list: '+$_.Exception.Message)
        }
    }
    return @($entries)
}
function Find-Python {
    # Vor jeder Installation alle vorhandenen, echten Python-Interpreter suchen.
    # WindowsApps-Store-Aliase werden nicht verwendet. Keine globale Python-Mutation.
    $candidates = New-Object System.Collections.ArrayList
    $seen = @{}
    function Add-Candidate([string]$path, [string[]]$arguments) {
        if ([string]::IsNullOrWhiteSpace($path)) { return }
        $key = $path.ToLowerInvariant() + ':' + ($arguments -join ' ')
        if (-not $seen.ContainsKey($key)) {
            $seen[$key] = $true
            [void]$candidates.Add(@{path=$path; args=@($arguments)})
        }
    }
    # Lokale, bereits eingerichtete Umgebung immer zuerst wiederverwenden.
    if (Test-Path -LiteralPath $venv) { Add-Candidate $venv @() }
    # Launcher, PATH und explizite Python-Versionen.
    foreach ($name in @('py.exe','python.exe','python3.exe','python3.14.exe','python3.13.exe','python3.12.exe','python3.11.exe','python3.10.exe')) {
        foreach ($cmd in @(Get-Command $name -All -ErrorAction SilentlyContinue)) {
            if ($cmd.Source) {
                $arguments=@()
                if ($name -eq 'py.exe') { $arguments=@('-3.13') }
                Add-Candidate $cmd.Source $arguments
                if ($name -eq 'py.exe') { foreach ($v in @('-3.15','-3.14','-3.12','-3.11','-3.10','-3')) { Add-Candidate $cmd.Source @($v) } }
            }
        }
    }
    # Python Launcher kann installierte Interpreter auch ausserhalb des PATH melden.
    foreach ($launcher in @(Get-Command py.exe -All -ErrorAction SilentlyContinue)) {
        if (-not $launcher.Source -or $launcher.Source -match '(?i)\\WindowsApps\\') { continue }
        try {
            $installed = & $launcher.Source -0p 2>$null
            foreach ($line in @($installed)) {
                if ($line -match '(?i)([A-Z]:\\[^\r\n\"]*?python(?:w)?\.exe)\s*$') {
                    Add-Candidate $Matches[1].Trim() @()
                }
            }
        } catch {}
    }
    # B-09: Python Install Manager legt echte Interpreter unter
    # %LOCALAPPDATA%\Python\pythoncore-3.15-64\python.exe ab.
    # Diesen konkreten Pfad DIREKT pruefen (keine -Recurse/-Depth-Abhaengigkeit).
    # Verwendet das aktuelle Benutzerprofil, keinen hartkodierten Benutzernamen.
    $pythonCoreRoot = if ($env:LOCALAPPDATA) { Join-Path $env:LOCALAPPDATA 'Python' } else { '' }
    if ($pythonCoreRoot -and (Test-Path -LiteralPath $pythonCoreRoot -PathType Container)) {
        $coreDirs = @(Get-ChildItem -LiteralPath $pythonCoreRoot -Directory -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -match '(?i)^pythoncore-3\.(\d+)(?:-\d+)?$' } |
            Sort-Object -Property Name)
        # Echte EXEs testen, 3.13/3.14 bevorzugen, 3.15 als Fallback zulassen.
        $coreDirs = @($coreDirs | Sort-Object -Property @{Expression={ if ($_.Name -match '(?i)^pythoncore-3\.(\d+)') { $minor=[int]$Matches[1]; if ($minor -eq 13) { 0 } elseif ($minor -eq 14) { 1 } elseif ($minor -eq 12) { 2 } elseif ($minor -eq 11) { 3 } elseif ($minor -eq 10) { 4 } else { 10 + $minor } } else { 999 } }})
        foreach ($coreDir in $coreDirs) {
            $coreExe = Join-Path $coreDir.FullName 'python.exe'
            Add-Candidate $coreExe @()
            $report.python_search_notes += ('pythoncore direct candidate: ' + $coreExe)
        }
    }
    # B-11: Uninstall inventory already exposed an actual pythoncore directory.
    # Test its python.exe directly rather than treating the entry as mere metadata.
    foreach ($installed in @(Get-InstalledPythonPackages)) {
        $location = [string]$installed.location
        if ($location -and (Test-Path -LiteralPath $location -PathType Container)) {
            $inventoryExe = Join-Path $location 'python.exe'
            Add-Candidate $inventoryExe @()
            $report.python_search_notes += ('uninstall-location direct candidate: '+$inventoryExe)
        }
    }
    # Offizielle Installer schreiben die InstallPath-Registry-Keys.
    foreach ($key in @('HKCU:\Software\Python\PythonCore','HKLM:\SOFTWARE\Python\PythonCore','HKLM:\SOFTWARE\WOW6432Node\Python\PythonCore')) {
        if (-not (Test-Path $key)) { continue }
        foreach ($ver in @(Get-ChildItem -LiteralPath $key -ErrorAction SilentlyContinue)) {
            try {
                $installKey = Join-Path $ver.PSPath 'InstallPath'
                $item = Get-Item -LiteralPath $installKey -ErrorAction Stop
                $folder = $item.GetValue('')
                if ($folder) { Add-Candidate (Join-Path $folder 'python.exe') @() }
                $exe = $item.GetValue('ExecutablePath')
                if ($exe) { Add-Candidate $exe @() }
            } catch {}
        }
    }
    # Offizielle Installationsregistrierung (PEP 514): Registry-Views 32/64 Bit.
    # Registry-Eintraege allein sind KEIN Nachweis einer funktionierenden Python-EXE.
    foreach ($hive in @([Microsoft.Win32.RegistryHive]::CurrentUser,[Microsoft.Win32.RegistryHive]::LocalMachine)) {
        foreach ($view in @([Microsoft.Win32.RegistryView]::Registry64,[Microsoft.Win32.RegistryView]::Registry32)) {
            try {
                $h = [Microsoft.Win32.RegistryKey]::OpenBaseKey($hive,$view)
                foreach ($company in @('Python\PythonCore','Python\PyManager')) {
                    $k=$h.OpenSubKey('SOFTWARE\'+$company)
                    if (-not $k) { continue }
                    foreach ($version in $k.GetSubKeyNames()) {
                        $v=$k.OpenSubKey($version)
                        $install=$v.OpenSubKey('InstallPath')
                        if ($install) {
                            $dir=[string]$install.GetValue('')
                            $exe=[string]$install.GetValue('ExecutablePath')
                            if ($dir) { Add-Candidate (Join-Path $dir 'python.exe') @() }
                            if ($exe) { Add-Candidate $exe @() }
                            $report.registry_python_paths += [ordered]@{hive=$hive.ToString();view=$view.ToString();version=$version;directory=$dir;executable=$exe}
                        }
                    }
                }
            } catch { $report.python_search_notes += ('registry-view '+$view+': '+$_.Exception.Message) }
        }
    }
    # Auch 'py -0p' ueber den Windows-Launcher an bekannten Dateistellen pruefen.
    foreach ($launchPath in @((Join-Path $env:WINDIR 'py.exe'),(Join-Path $env:LOCALAPPDATA 'Programs\Python\Launcher\py.exe'))) {
        if (-not (Test-Path -LiteralPath $launchPath -PathType Leaf)) { continue }
        try {
            foreach ($line in @(& $launchPath -0p 2>$null)) {
                if ($line -match '(?i)([A-Z]:\\[^\r\n"]*?python(?:w)?\.exe)\s*$') { Add-Candidate $Matches[1].Trim() @() }
            }
        } catch {}
    }
    # Registry-InstallLocation aus dem Windows-Uninstall-Register aufloesen.
    foreach ($pkg in @(Get-InstalledPythonPackages)) {
        if ($pkg.location -and (Test-Path -LiteralPath $pkg.location)) { Add-Candidate (Join-Path $pkg.location 'python.exe') @() }
        # MSI-/Uninstall-Eintraege koennen InstallLocation leer lassen, aber DisplayIcon liefern.
        # Erst auf tatsaechliche Dateien pruefen, nie UninstallString ausfuehren.
        foreach ($field in @('icon','uninstall','install_source')) {
            $value=[string]$pkg[$field]
            if (-not $value) { continue }
            if ($value -match '(?i)"?([A-Z]:\\[^"\r\n,]*?python(?:w)?\.exe)') { Add-Candidate $Matches[1] @() }
            elseif ($field -eq 'install_source' -and (Test-Path -LiteralPath $value -PathType Container)) { Add-Candidate (Join-Path $value 'python.exe') @() }
        }
    }
    # winget-Python liegt oft NICHT in AppData\Local\Programs\Python.
    $roots=@(
        (Join-Path $env:LOCALAPPDATA 'Programs\Python'),
        (Join-Path $env:LOCALAPPDATA 'Python'),
        (Join-Path $env:APPDATA 'Python'),
        (Join-Path $env:USERPROFILE 'scoop\apps\python'),
        (Join-Path $env:ProgramData 'chocolatey\bin'),
        (Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Packages'),
        (Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Links'),
        (Join-Path $env:LOCALAPPDATA 'Microsoft\WindowsApps'),
        (Join-Path $env:LOCALAPPDATA 'Programs'),
        (Join-Path $env:ProgramFiles 'Python'),
        ${env:ProgramFiles(x86)}, 'C:\Python',
        (Join-Path $env:ProgramFiles 'Python313'), (Join-Path $env:ProgramFiles 'Python314'),
        (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python313'),
        (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python314'),
        (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python315'),
        (Join-Path $env:ProgramFiles 'Python315'),
        (Join-Path $env:USERPROFILE '.pyenv\pyenv-win\versions'),
        (Join-Path $env:LOCALAPPDATA 'uv\python'),
        (Join-Path $env:USERPROFILE '.local\share\uv\python')
    )
    foreach ($base in $roots) {
        if (-not $base -or -not (Test-Path -LiteralPath $base)) { continue }
        try {
            # Keine unkontrollierte rekursive Vollsuche in Program Files.
            if ($base -like '*WinGet\Packages') {
                $dirs = Get-ChildItem -LiteralPath $base -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '(?i)^Python\.' }
                foreach ($dir in @($dirs)) {
                    foreach ($file in @(Get-ChildItem -LiteralPath $dir.FullName -Filter 'python.exe' -File -Recurse -Depth 3 -ErrorAction SilentlyContinue)) {
                        Add-Candidate $file.FullName @()
                    }
                }
            } elseif ($base -like '*WinGet\Links') {
                foreach ($file in @(Get-ChildItem -LiteralPath $base -Filter 'python*.exe' -File -ErrorAction SilentlyContinue)) { Add-Candidate $file.FullName @() }
            } else {
                foreach ($file in @(Get-ChildItem -LiteralPath $base -Filter 'python.exe' -File -Recurse -Depth 2 -ErrorAction SilentlyContinue)) { Add-Candidate $file.FullName @() }
            }
        } catch {}
    }
    # Repair discovery: registry App Paths, full uninstall record and profile-root
    # Python locations, including non-default directories on the user's B: drive.
    foreach ($hive in @([Microsoft.Win32.RegistryHive]::CurrentUser,[Microsoft.Win32.RegistryHive]::LocalMachine)) {
        foreach ($view in @([Microsoft.Win32.RegistryView]::Registry64,[Microsoft.Win32.RegistryView]::Registry32)) {
            try {
                $r=[Microsoft.Win32.RegistryKey]::OpenBaseKey($hive,$view)
                $apps=$r.OpenSubKey('SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\python.exe')
                if ($apps) {
                    $appPath=[string]$apps.GetValue('')
                    if ($appPath) { Add-Candidate ($appPath.Trim('"')) @() }
                }
            } catch { $report.python_search_notes += ('app-paths '+$hive+'/'+$view+': '+$_.Exception.Message) }
        }
    }
    foreach ($pkg in @(Get-InstalledPythonPackages)) {
        foreach ($field in @('location','icon','install_source','uninstall')) {
            $raw=[string]$pkg[$field]
            if (-not $raw) { continue }
            $report.python_registry_hints += [ordered]@{name=$pkg.name; source=$field; raw=$raw}
            $raw=$raw.Trim('"')
            if ($field -eq 'location' -and (Test-Path -LiteralPath $raw -PathType Container)) {
                Add-Candidate (Join-Path $raw 'python.exe') @()
                # Some uninstall records point to the parent installation tree.
                foreach ($child in @(Get-ChildItem -LiteralPath $raw -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '(?i)^Python3(1[0-9])$' })) {
                    Add-Candidate (Join-Path $child.FullName 'python.exe') @()
                }
            }
            if ($raw -match '(?i)([A-Z]:\\[^"\r\n,]*?python(?:w)?\.exe)') { Add-Candidate $Matches[1] @() }
        }
    }
    # Explicitly test real per-user / per-machine installation roots and their
    # immediate Python directories; never scan entire drives or run arbitrary EXEs.
    foreach ($base in @($env:LOCALAPPDATA,$env:APPDATA,$env:ProgramFiles,${env:ProgramFiles(x86)},$env:USERPROFILE,'B:\Tools','B:\Python','B:\Program Files')) {
        if ([string]::IsNullOrWhiteSpace($base) -or -not (Test-Path -LiteralPath $base -PathType Container)) { continue }
        $report.python_scan_roots += $base
        foreach ($relative in @('python.exe','Python313\python.exe','Python314\python.exe','Python315\python.exe','Programs\Python\Python313\python.exe','Programs\Python\Python314\python.exe','Programs\Python\Python315\python.exe','Python\Python313\python.exe','Python\Python315\python.exe')) {
            Add-Candidate (Join-Path $base $relative) @()
        }
    }
    foreach ($candidate in $candidates) {
        if (-not (Test-Path -LiteralPath $candidate.path -PathType Leaf)) {
            $report.python_candidates += [ordered]@{path=$candidate.path; arguments=($candidate.args -join ' '); valid=$false; version=''; reason='not_found'}
            continue
        }
        $version=Invoke-PythonCheck $candidate.path $candidate.args
        $report.python_candidates += [ordered]@{path=$candidate.path; arguments=($candidate.args -join ' '); valid=([bool]$version); version=$version; reason=$(if($version){'ok'}else{'execution_or_version_failed'})}
        if ($version) { return @{path=$candidate.path; args=$candidate.args; version=$version} }
    }
    return $null
}
function RunPython([hashtable]$choice, [string[]]$arguments) {
    $fullArgs = @($choice.args) + @($arguments)
    & $choice.path @fullArgs
    if ($LASTEXITCODE -ne 0) { throw "Python fehlgeschlagen ($LASTEXITCODE): $($arguments -join ' ')" }
}
function Check-Environment {
    if (Test-Path -LiteralPath $venv) {
        $v = Invoke-PythonCheck $venv @()
        if ($v) { $report.local_venv = "OK $v"; Note "[OK] Lokales Environment: $venv ($v)" }
        else { $report.local_venv='BROKEN'; Note '[FEHLER] Lokale .venv nicht lauffaehig.' }
    } else { Note '[FEHLT] Lokale .venv (Menuepunkt 2 richtet sie ein).' }
    if ($report.local_venv -notlike 'OK*') { return }
    try {
        $pipVer = & $venv -m pip --version 2>$null
        if ($LASTEXITCODE -eq 0) { $report.pip='OK'; Note "[OK] pip: $pipVer" }
        else { Note '[FEHLT] pip in lokaler .venv' }
    } catch { Note '[FEHLT] pip in lokaler .venv' }
    foreach ($module in @('klrw','psutil','pystray','PIL','pytest','setuptools','wheel','build')) {
        try {
            & $venv -c "import importlib.util as u,sys;sys.exit(0 if u.find_spec('$module') else 1)" 2>$null
            if ($LASTEXITCODE -eq 0) { $report.modules[$module]='OK'; Note "[OK] $module" }
            else { $report.modules[$module]='MISSING'; Note "[FEHLT] $module" }
        } catch { $report.modules[$module]='MISSING'; Note "[FEHLT] $module" }
    }
}
function Diagnose {
    $wingetCmd = Get-Command winget.exe -ErrorAction SilentlyContinue
    if ($wingetCmd) { $report.winget='OK'; Note '[OK] winget vorhanden' }
    else { Note '[FEHLT] winget. App Installer / Microsoft Store erforderlich fuer automatische Python-Installation.' }
    $smart = Get-Command smartctl.exe -ErrorAction SilentlyContinue
    if ($smart) { $report.smartctl='AVAILABLE'; Note '[OPTIONAL] smartctl gefunden (nicht aktiviert).' }
    else { Note '[OPTIONAL] smartctl nicht installiert: SMART bleibt deaktiviert.' }
    $choice = Find-Python
    $report.installed_python_packages = @(Get-WingetPythonInventory)
    if ($choice) {
        $report.python='OK'; $report.python_path=$choice.path
        $report.python_version=$choice.version
        $report.launcher=($choice.args -join ' ')
        Note "[OK] Python $($choice.version): $($choice.path) $($choice.args -join ' ')"
    } else {
        Note '[FEHLT] Kein funktionsfaehiges Python >= 3.10 erkannt.'
        Note '[HINWEIS] Ein Store-Alias gilt nur dann als Python, wenn der echte Versionstest erfolgreich ist.'
        if (@($report.installed_python_packages).Count -gt 0) { Note '[WICHTIG] Python ist bei Windows als installiert registriert, aber keine funktionierende python.exe wurde gefunden.'; foreach($pkg in @($report.installed_python_packages)) { Note ("[INVENTAR] $($pkg.name) $($pkg.source) $($pkg.location)") } }
    }
    Check-Environment
    if ($report.local_venv -like 'OK*' -and $report.pip -eq 'OK' -and
        @((@('klrw','psutil','pystray','PIL','pytest') | Where-Object { $report.modules[$_] -ne 'OK' })).Count -eq 0) {
        $report.result='READY'; Note '[OK] Projekt bereit fuer Tray, Tests und Dashboard.'
    } else { $report.result='NEEDS_SETUP'; Note '[INFO] Menuepunkt 2 richtet fehlende Pflicht- und optionale Tray-/Testpakete ein.' }
    return $choice
}
function Confirm([string]$prompt) {
    $answer = (Read-Host "$prompt [J/N]").Trim().ToUpperInvariant()
    return $answer -eq 'J'
}
function Ensure-Python([hashtable]$choice) {
    if ($choice) { return $choice }
    # Ein Benutzer kann einen vorhandenen Interpreter ohne PATH/Registry manuell angeben.
    # Keine Ausfuehrung unbekannter Dateien ohne bewusste Auswahl.
    Note '[INFO] Vorhandene Python-EXE kann manuell angegeben werden (z.B. D:\Tools\Python314\python.exe).'
    $manual = (Read-Host 'Pfad zu vorhandener python.exe [ENTER = ueberspringen, ? = Dateiauswahl]').Trim().Trim('"')
    if ($manual -eq '?') {
        try {
            Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
            $dialog = New-Object System.Windows.Forms.OpenFileDialog
            $dialog.Title = 'Vorhandene Python-EXE auswaehlen'
            $dialog.Filter = 'Python Interpreter (python.exe)|python.exe|Executables (*.exe)|*.exe'
            $dialog.CheckFileExists = $true
            if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { $manual = $dialog.FileName }
            else { $manual = '' }
        } catch { Note '[HINWEIS] Dateiauswahl nicht verfuegbar. Bitte vollstaendigen Pfad direkt eintippen.'; $manual='' }
    }
    if ($manual) {
        if (Test-Path -LiteralPath $manual -PathType Leaf) {
            $version = Invoke-PythonCheck $manual @()
            if ($version) {
                Note "[OK] Manuell gewaehltes Python ${version}: $manual"
                return @{path=(Resolve-Path -LiteralPath $manual).ProviderPath; args=@(); version=$version}
            }
            Note '[FEHLER] Die gewaehlte Datei ist kein funktionsfaehiges Python >= 3.10.'
        } else { Note '[FEHLER] Angegebene Python-Datei nicht gefunden.' }
    }
    # Nach einer Installation in einem frueheren Lauf NIE automatisch install
    # wiederholen. Das koennte 'already installed / no upgrades' ergeben.
    $registered = @(Get-WingetPythonInventory)
    $report.installed_python_packages = $registered
    if ($registered.Count -gt 0) {
        Note '[BLOCKIERT] Windows meldet Python bereits als installiert, aber die EXE ist nicht gefunden oder nicht lauffaehig.'
        Note '[HINWEIS] Keine erneute winget-install-Schleife. Der Python-Recovery-Modus bietet gezielte Pfadwahl und Reparaturanleitung.'
        Note '[HINWEIS] Keine erneute Installation. Erst InstallPath/ExecutablePath sowie DisplayIcon im Bericht pruefen.'
        Note '[HINWEIS] Windows-Apps > Installierte Apps > Python 3.13 > Aendern > Repair ist eine manuelle Option, falls die EXE wirklich fehlt.'
        Note '[HINWEIS] Der Installer repariert/deinstalliert vorhandene Python-Versionen NICHT automatisch.'
        $report.python_remediation='PYTHON_REGISTERED_EXECUTABLE_UNVERIFIED'
        Note '[HINWEIS] Alternativ bei Menuepunkt 2 den vollstaendigen Pfad einer funktionierenden python.exe angeben.'
        $report.result='READBACK_PENDING'
        return $null
    }
    if ($report.winget -ne 'OK') {
        Note '[BLOCKIERT] Python fehlt und winget ist nicht vorhanden.'
        Note 'Installiere Python >= 3.10 von https://www.python.org/downloads/windows/ und starte das Menue erneut.'
        return $null
    }
    if (-not (Confirm 'Python 3.13 ueber winget installieren (systemweite Benutzer-Installation moeglich)?')) {
        Note '[ABBRUCH] Python-Installation nicht freigegeben.'
        return $null
    }
    Note '[INFO] Installiere offizielles Python-Paket ueber winget ...'
    # WICHTIG: PowerShell-Funktionen geben standardmaessig jede Pipeline-Ausgabe zurueck.
    # Ohne Out-Host koennen winget-Fortschrittszeilen mit dem Rueckgabeobjekt
    # aus Ensure-Python vermischt werden: System.Object[] statt Hashtable.
    & winget.exe install --id Python.Python.3.13 --exact --source winget --accept-package-agreements --accept-source-agreements --disable-interactivity | Out-Host
    $installExit = $LASTEXITCODE
    $report.winget_install_exit = $installExit
    if ($installExit -ne 0) { Note "[FEHLER] winget install Exit-Code: $installExit"; $report.installed_python_packages=@(Get-WingetPythonInventory); return $null }
    # Das aktuelle Terminal erhaelt nach winget nicht zwangslaeufig neue PATH-Eintraege.
    # Frisch installierte Interpreter daher direkt ueber die bekannten Fundorte suchen.
    $choice=Find-Python
    $report.installed_python_packages=@(Get-WingetPythonInventory)
    if (-not $choice) {
        $report.result='READBACK_PENDING'
        Note '[READBACK_PENDING] winget meldet Erfolg, aber Python ist in diesem Prozess nicht auffindbar. Installationsort pruefen / Terminal neu starten.'
        return $null
    }
    Note "[OK] Python nach Installation erkannt: $($choice.path)"
    return $choice
}
function Ensure-Venv([hashtable]$choice) {
    if (-not (Test-Path -LiteralPath $venv)) {
        Note '[INFO] Erstelle lokale virtuelle Python-Umgebung ...'
        RunPython $choice @('-m','venv',(Join-Path $root '.venv'))
    }
    if (-not (Invoke-PythonCheck $venv @())) {
        Note '[FEHLER] Vorhandene .venv ist unbrauchbar. Kein automatisches Loeschen.'
        Note 'Bitte .venv manuell pruefen oder separat sichern; Projektdateien bleiben erhalten.'
        return $false
    }
    return $true
}
function Install-Dependencies([bool]$upgrade) {
    & $venv -m pip --version *> $null
    if ($LASTEXITCODE -ne 0) {
        Note '[INFO] pip fehlt in .venv; versuche Python ensurepip (nur lokal).'
        & $venv -m ensurepip --upgrade
        if ($LASTEXITCODE -ne 0) { throw 'pip konnte in .venv nicht eingerichtet werden.' }
    }
    if ($upgrade) {
        Note '[INFO] Aktualisiere pip, setuptools und wheel innerhalb der lokalen .venv ...'
        & $venv -m pip install --upgrade pip setuptools wheel build
        if ($LASTEXITCODE -ne 0) { throw 'pip-Toolupdate fehlgeschlagen' }
        Note '[INFO] Aktualisiere Projekt-, Tray- und Test-Abhaengigkeiten innerhalb der lokalen .venv ...'
        & $venv -m pip install --upgrade -e "${root}[tray,test]"
    } else {
        Note '[INFO] Installiere/repariere Projekt-, Tray- und Test-Abhaengigkeiten in lokaler .venv ...'
        & $venv -m pip install -e "${root}[tray,test]"
    }
    if ($LASTEXITCODE -ne 0) { throw "pip install fehlgeschlagen (Exit-Code: $LASTEXITCODE)" }
    Note '[OK] pip-Installation abgeschlossen.'
}
function Verify {
    Check-Environment
    if ($report.local_venv -notlike 'OK*' -or $report.pip -ne 'OK' -or
        @((@('klrw','psutil','pystray','PIL','pytest') | Where-Object { $report.modules[$_] -ne 'OK' })).Count -ne 0) {
        throw 'Python-Umgebung unvollstaendig; Abnahme nicht bestanden.'
    }
    # PowerShell 5.1 / native argv: no nested string literal in Python -c.
    # The prior print("[OK] ...") was passed without its inner quotes on Windows
    # and made an otherwise successful setup fail with SyntaxError.
    & $venv -c 'import klrw.unified_tray, klrw.unified_state, psutil, pystray, PIL, pytest'
    if ($LASTEXITCODE -ne 0) { throw "Modul-Readback fehlgeschlagen (Exit-Code: $LASTEXITCODE)." }
    Note '[OK] Unified Tray und alle Abhaengigkeiten importierbar.' 
    $report.result='READY'; Note '[OK] Vollstaendiger Umgebung-Readback bestanden.'
}
$choice=$null
try {
    if ($Action -eq 'Diagnose' -or $Action -eq 'PythonRecovery') {
        $choice=Diagnose
        if ($Action -eq 'PythonRecovery' -and -not $choice) {
            Note '[RECOVERY] Bevor Windows-Python repariert wird, pruefe folgende Moeglichkeiten:'
            Note '[RECOVERY] (1) py -0p in neuer PowerShell pruefen (falls Launcher vorhanden).'
            Note '[RECOVERY] (2) Windows Einstellungen > Apps > Installierte Apps > Python 3.13 > Aendern > Repair.'
            Note '[RECOVERY] (3) Im Menuepunkt 2 ? fuer Dateiauswahl (python.exe) nutzen.'
            Note '[RECOVERY] Ohne konkreten EXE-Readback bleiben die Registry-Eintraege nur Metadaten.'
            $report.python_remediation='CHECK_PY_LAUNCHER_OR_WINDOWS_INSTALLER_REPAIR'
            $report.result='READBACK_PENDING'
        }
    }
    elseif ($Action -eq 'Verify') { Verify }
    else {
        $choice=Diagnose
        if ($Action -eq 'Setup' -and $report.result -eq 'READY') {
            Note '[OK] Alle Pflichtwerkzeuge sind bereits bereit. Keine erneute Installation erforderlich.'
            Verify
            throw 'ALREADY_READY'
        }
        $choice=Ensure-Python $choice
        if ($null -ne $choice -and $choice -isnot [hashtable]) {
            $report.result='BLOCKED'
            throw 'Interner Fehler: Python-Auswahl ist keine Hashtable. Siehe TOOL_REPORT.'
        }
        if (-not $choice) { if ($report.result -ne 'READBACK_PENDING') { $report.result='BLOCKED' }; throw 'Kein funktionsfaehiges Python verfuegbar.' }
        if (-not (Ensure-Venv $choice)) { $report.result='BLOCKED'; throw 'Bestehende .venv defekt.' }
        if ($Action -eq 'Update') {
            Note '[INFO] Python selbst wird nicht still aktualisiert. Du kannst dafuer separat winget upgrade verwenden.'
            if (-not (Confirm 'Lokale pip-/Projekt-Abhaengigkeiten jetzt aktualisieren?')) { throw 'Update nicht freigegeben.' }
            Install-Dependencies $true
        } else {
            if (-not (Confirm 'Fehlende Projekt-, Tray- und Testpakete ueber pip installieren/reparieren?')) { throw 'Setup nicht freigegeben.' }
            Install-Dependencies $false
        }
        Verify
    }
} catch {
    $msg=$_.Exception.Message
    if ($msg -eq 'ALREADY_READY') { $report.result='READY' } else { Note "[FEHLER] $msg"
    if ($report.result -notin @('BLOCKED','READBACK_PENDING')) { $report.result='PARTIAL' } }
} finally {
    $path=Join-Path $reportDir ("TOOL_REPORT_"+(Get-Date -Format 'yyyyMMdd_HHmmss')+'.json')
    try { ($report | ConvertTo-Json -Depth 8) | Set-Content -LiteralPath $path -Encoding UTF8; Write-Host "[BERICHT] $path" }
    catch { Write-Warning "Bericht konnte nicht geschrieben werden: $_" }
    Write-Host "[STATUS] $($report.result)"
}
if ($report.result -eq 'READY') { exit 0 }
exit 1
