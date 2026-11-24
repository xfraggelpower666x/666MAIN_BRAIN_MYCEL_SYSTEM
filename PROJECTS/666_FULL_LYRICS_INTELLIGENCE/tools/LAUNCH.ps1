$ErrorActionPreference='Stop'
$Root=Split-Path -Parent $PSScriptRoot
Set-Location $Root
function Ask([string]$Message) { $answer=Read-Host "$Message [J/N]"; return $answer -match '^(j|ja|y|yes)$' }
function Has([string]$Name) { return [bool](Get-Command $Name -ErrorAction SilentlyContinue) }
function InstallTool([string]$Name,[string]$Winget) {
 if(Has $Name) {Write-Host "$Name vorhanden" -ForegroundColor Cyan;return}
 Write-Host "$Name nicht vorhanden" -ForegroundColor Yellow
 if((Has 'winget') -and (Ask "$Name via winget installieren?")) {
  & winget install --id $Winget --exact --accept-package-agreements --accept-source-agreements
  if($LASTEXITCODE -ne 0){throw "$Name Installation fehlgeschlagen"}
  $env:PATH=[Environment]::GetEnvironmentVariable('Path','Machine')+';'+[Environment]::GetEnvironmentVariable('Path','User')
 }else{throw "Bitte $Name installieren und STARTEN.bat erneut starten."}
 if(-not (Has $Name)){throw "$Name installiert, bitte Terminal neu starten und STARTEN.bat erneut ausführen"}
}
function ElectronExecutablePath {
 $direct=Join-Path $Root 'node_modules\electron\dist\electron.exe'
 if(Test-Path $direct){return $direct}
 $pathFile=Join-Path $Root 'node_modules\electron\path.txt'
 if(Test-Path $pathFile){
  $relative=(Get-Content $pathFile -Raw).Trim()
  if($relative){
   $resolved=Join-Path (Join-Path $Root 'node_modules\electron') $relative
   if(Test-Path $resolved){return $resolved}
  }
 }
 return $null
}
function RepairElectronPathMarker {
 # Node/Electron reads path.txt literally. Set-Content added CRLF and made spawn fail with ENOENT.
 $pkg=Join-Path $Root 'node_modules\electron'
 $exe=Join-Path $pkg 'dist\electron.exe'
 $marker=Join-Path $pkg 'path.txt'
 if(-not (Test-Path $exe)){return}
 $expected='electron.exe'
 $actual=if(Test-Path $marker){[System.IO.File]::ReadAllText($marker)}else{''}
 if($actual -cne $expected){
  Write-Host 'Repariere Electron path.txt (entferne CRLF/Leerzeichen am Dateiende).' -ForegroundColor Yellow
  [System.IO.File]::WriteAllText($marker,$expected,[System.Text.Encoding]::ASCII)
 }
}
function ElectronRuntimeOk {
 $exe=ElectronExecutablePath
 if(-not $exe){return $false}
 return ((Get-Item $exe).Length -gt 1000000)
}
function EnsureElectronRuntime {
 RepairElectronPathMarker
 if(ElectronRuntimeOk) {
  Write-Host "Electron Runtime vorhanden: $(ElectronExecutablePath)" -ForegroundColor Cyan
  return
 }
 $package=Join-Path $Root 'node_modules\electron\package.json'
 if(-not (Test-Path $package)){throw 'Electron npm-Paket fehlt. Zuerst Projekt-Abhaengigkeiten installieren.'}
 $version=(Get-Content $package -Raw | ConvertFrom-Json).version
 Write-Host "Electron npm-Paket $version vorhanden, aber electron.exe fehlt." -ForegroundColor Yellow
 Write-Host 'npm hat den Electron-Postinstall-Schritt blockiert oder nicht abgeschlossen.' -ForegroundColor Yellow
 Write-Host 'Es folgt nur nach Zustimmung ein SHA256-gepruefter Download der offiziellen Electron-Runtime.' -ForegroundColor Yellow
 if(-not (Ask 'Offizielle Electron-Runtime gezielt herunterladen und installieren?')) {
  throw 'Electron Runtime nicht freigegeben. Keine Aenderungen vorgenommen.'
 }
 Write-Host 'Gezielte Reparatur: Original-Electron-Runtime mit SHA256-Pruefung.' -ForegroundColor Cyan
 & powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$Root\tools\INSTALL_ELECTRON_RUNTIME.ps1" -ProjectRoot $Root
 if($LASTEXITCODE -ne 0){throw 'Electron Runtime Reparatur fehlgeschlagen. Kein Node- oder Python-Upgrade ausgefuehrt.'}
 RepairElectronPathMarker
 if(-not (ElectronRuntimeOk)){
  $dist=Join-Path $Root 'node_modules\electron\dist'
  $pathFile=Join-Path $Root 'node_modules\electron\path.txt'
  $npmCache=& npm config get cache 2>$null
  $proxyConfigured=([bool](& npm config get proxy 2>$null) -or [bool](& npm config get https-proxy 2>$null))
  Write-Host "Electron Version: $version" -ForegroundColor Yellow
  Write-Host "Runtime-Verzeichnis vorhanden: $(Test-Path $dist)" -ForegroundColor Yellow
  Write-Host "Electron path.txt vorhanden: $(Test-Path $pathFile)" -ForegroundColor Yellow
  Write-Host "npm Cache: $npmCache" -ForegroundColor Yellow
  Write-Host "Proxy konfiguriert: $proxyConfigured" -ForegroundColor Yellow
  throw 'Electron Runtime fehlt weiterhin. npm-Download/Proxy/Antivirus blockiert wahrscheinlich die electron-v35.7.5-win32-x64.zip. Keine weiteren Pakete wurden geloescht.'
 }
 $exe=ElectronExecutablePath
 Write-Host "Electron Runtime installiert: $exe" -ForegroundColor Green
}
function Toolchain {
 InstallTool 'node' 'OpenJS.NodeJS.LTS'
 InstallTool 'npm' 'OpenJS.NodeJS.LTS'
 if(-not (Has 'py') -and -not (Has 'python')) {InstallTool 'py' 'Python.Python.3.13'}
 & node --version
 if(Has 'py'){ & py -3 --version }else{& python --version}
 if(-not (Test-Path 'node_modules\electron\index.js')) {
   if(-not (Ask 'Fehlende Electron Projekt-Abhaengigkeiten lokal installieren (npm)?')){throw 'Electron npm-Paket fehlt'}
   if(Test-Path 'package-lock.json') { & npm ci --no-audit --no-fund }else{ & npm install --no-audit --no-fund }
   if($LASTEXITCODE -ne 0){throw 'npm Installation fehlgeschlagen'}
 }
 EnsureElectronRuntime
}
function PythonPip([string[]]$Args) {
 if(Has 'py'){& py -3 -m pip @Args}else{& python -m pip @Args}
 if($LASTEXITCODE -ne 0){throw 'Python pip Befehl fehlgeschlagen'}
}
function MakeBuild([string]$Target) {
 Toolchain
 $missing=@()
 $pyArgs = if(Has 'py') {@('-3')} else {@()}
 $pyCmd = if(Has 'py') {'py'} else {'python'}
 foreach($dependency in @(@('PyInstaller','pyinstaller'),@('pypdf','pypdf'),@('docx','python-docx'))){
  & $pyCmd @pyArgs -c ("import " + $dependency[0]) 2>$null
  if($LASTEXITCODE -ne 0){$missing+= $dependency[1]}
 }
 if($missing.Count -gt 0){
  Write-Host ('Fehlende Build-Pakete: ' + ($missing -join ', ')) -ForegroundColor Yellow
  if(-not (Ask 'Nur diese fehlenden Python-Pakete installieren?')){throw 'Build-Abhaengigkeiten nicht freigegeben'}
  PythonPip (@('install') + $missing)
 }else{Write-Host 'Alle Build-Pakete vorhanden. Keine Installation erforderlich.' -ForegroundColor Cyan}
 & powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$Root\build\BUILD_WINDOWS.ps1" -Action $Target
 if($LASTEXITCODE -ne 0){throw "Build $Target fehlgeschlagen"}
}
while($true){
 Clear-Host
 Write-Host '===============================================' -ForegroundColor Magenta
 Write-Host '  666 FULL LYRICS INTELLIGENCE - R06.1' -ForegroundColor Cyan
 Write-Host '===============================================' -ForegroundColor Magenta
 Write-Host '1  START - Abhaengigkeiten pruefen und Electron starten'
 Write-Host '2  Toolcheck ohne Installation'
 Write-Host '3  Windows Portable EXE bauen'
 Write-Host '4  Windows Setup bauen (Installationspfad waehlbar)'
 Write-Host '5  Portable EXE + Setup bauen'
 Write-Host '6  Lokale R02 Original-Sicherung anzeigen'
 Write-Host '0  Beenden'
 $choice=Read-Host 'Auswahl'
 try {
  switch($choice){
   '1' {Toolchain; & npm start; if($LASTEXITCODE -ne 0){throw 'Electron Start fehlgeschlagen'}}
   '2' {foreach($name in @('node','npm','py','python','winget')){Write-Host "$name : $(Has $name)"}; if(Has 'node'){Write-Host "Electron Runtime : $(ElectronRuntimeOk)"}}
   '3' {MakeBuild 'portable'}
   '4' {MakeBuild 'setup'}
   '5' {MakeBuild 'all'}
   '6' {Write-Host "R02 Backup: $Root\originals\R02_LEGACY_ORIGINAL_PRESERVED.zip";Write-Host 'Zum Import die ZIP separat entpacken, dann die SQLite-Datei ueber den Dateibrowser waehlen.'}
   '0' {exit 0}
   default {Write-Host 'Ungueltige Auswahl'}
  }
 }catch{Write-Host "FEHLER: $($_.Exception.Message)" -ForegroundColor Red}
 Read-Host 'Enter fuer Menue'
}
