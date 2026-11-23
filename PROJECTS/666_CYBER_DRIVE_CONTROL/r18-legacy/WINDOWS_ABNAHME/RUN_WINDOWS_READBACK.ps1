# R13 Windows-Readback: keine Adminrechte, keine EXE Dritter, keine Eingriffe in Lock-LEDs.
param([switch]$PreviewOnly, [string]$PythonExe = 'py')
$ErrorActionPreference = 'Stop'
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$project = Split-Path -Parent $dir
$reportDir = Join-Path $dir 'REPORTS'
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$reportPath = Join-Path $reportDir "R13_WINDOWS_READBACK_$stamp.json"
$results = [ordered]@{
 schema='klrw.r13.windows-acceptance.v1'; at=(Get-Date).ToString('o'); hostname=$env:COMPUTERNAME;
 platform=[Environment]::OSVersion.VersionString; powershell=$PSVersionTable.PSVersion.ToString();
 user_is_admin=$false; python=''; import_check='OFFEN'; tray_dependencies='OFFEN';
 display_count=0; display_geometry=@(); processes=@(); manual=[ordered]@{};
 verdict='PARTIAL'; note='Automatisierte Prüfungen ersetzen keine Sichtprüfung des Windows-Trays.'
}
try {
 $id=[Security.Principal.WindowsIdentity]::GetCurrent()
 $principal=New-Object Security.Principal.WindowsPrincipal($id)
 $results.user_is_admin=$principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
} catch {}
function Invoke-Py([string]$code) {
 $args=@('-c',$code)
 $output = & $PythonExe @args 2>&1
 if ($LASTEXITCODE -ne 0) { throw "Python-Check gescheitert: $output" }
 return ($output | Out-String).Trim()
}
$old=(Get-Location).Path
try {
 Set-Location $project
 $results.python = (& $PythonExe -c 'import sys; print(sys.version)' 2>&1 | Out-String).Trim()
 $v=Invoke-Py 'import klrw.unified_tray, klrw.unified_state; print("PASS")'
 $results.import_check=$v
 try { $results.tray_dependencies=Invoke-Py 'import pystray, PIL; print("PASS")' }
 catch { $results.tray_dependencies="FEHLT: $($_.Exception.Message)" }
 try {
  Add-Type -AssemblyName System.Windows.Forms
  $screens=@([System.Windows.Forms.Screen]::AllScreens)
  $results.display_count=$screens.Count
  $results.display_geometry=@($screens | ForEach-Object { [ordered]@{device=$_.DeviceName; bounds=$_.Bounds.ToString(); working_area=$_.WorkingArea.ToString(); primary=$_.Primary}})
 } catch { $results.display_geometry=@("Fehler: $($_.Exception.Message)") }
 if (-not $PreviewOnly) {
  Write-Host 'Starte R13 Unified Tray als separaten Python-Prozess; bitte Tray und Desktopfenster pruefen.'
  $proc=Start-Process -FilePath $PythonExe -ArgumentList '-m','klrw.unified_tray','--interval-ms','500' -PassThru -WorkingDirectory $project
  Start-Sleep -Seconds 3
  $results.processes += [ordered]@{pid=$proc.Id; alive=(-not $proc.HasExited); mode='live-read-only'; exit_code=$(if($proc.HasExited){$proc.ExitCode}else{$null})}
  Write-Host 'Manuelle Pruefung: Tray-Symbol sichtbar? Fenster per Tray-Menue zeigen/verbergen? Danach Lock-Tasten EIN/AUS, sowie Disk- und Netzwerkaktivitaet pruefen.'
  $questions=[ordered]@{
   tray_visible='Tray-Symbol sichtbar (J/N)?'; tray_menu='Tray-Menue Show/Hide und Exit funktionieren (J/N)?';
   state_refresh='Num/Caps/Scroll bei echter Tastenaenderung aktuell (J/N)?';
   disk_activity='Datentraeger-Lese-/Schreibaktivitaet sichtbar (J/N)?';
   network_activity='RX/TX-Netzwerkaktivitaet sichtbar (J/N)?';
   rgb_preview='RGB-Ebenenauswahl sichtbar und Reaktion korrekt (J/N)?';
   multi_monitor='Fenster/Tray-Verhalten bei vorhandenen Bildschirmen korrekt (J/N/U)?';
   restart='Neustart/Schliessen des Tray-Menues verifiziert (J/N/U)?'
  }
  foreach ($key in $questions.Keys) {$results.manual[$key]=(Read-Host $questions[$key]).Trim().ToUpperInvariant()}
  if (-not $proc.HasExited) { Write-Host 'R13 Prozess laeuft noch. Bitte ueber Tray-Menue Exit beenden.' }
 } else {
  $results.manual.preview_only='Y'; Write-Host 'Nur Umgebungs- und Importpruefung (PreviewOnly).'
 }
 if (($results.import_check -eq 'PASS') -and ($results.tray_dependencies -eq 'PASS') -and
     (-not $PreviewOnly) -and (@($results.manual.Values | Where-Object { $_ -eq 'N' }).Count -eq 0) -and
     (@($results.manual.Values | Where-Object { $_ -eq 'J' }).Count -ge 6)) {
  $results.verdict='MANUAL_CHECKS_REPORTED_PASS' # keine unabhängige Hardware-Verifikation
 }
} catch { $results.verdict='PARTIAL';$results.note="Abbruch/Fehler: $($_.Exception.Message)";Write-Warning $results.note }
finally {
 Set-Location $old
 $results | ConvertTo-Json -Depth 8 | Set-Content -Path $reportPath -Encoding UTF8
 Write-Host "R13 Readback: $reportPath"
 Write-Host "Status: $($results.verdict)"
}
