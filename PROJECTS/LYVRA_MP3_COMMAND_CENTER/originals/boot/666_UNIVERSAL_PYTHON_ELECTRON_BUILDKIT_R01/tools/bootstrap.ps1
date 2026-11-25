param([string]$Action = 'menu')
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Config = Get-Content -LiteralPath (Join-Path $Root 'project.config.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$Project = [IO.Path]::GetFullPath((Join-Path $Root $Config.project_directory))
$Venv = Join-Path $Root '.buildenv'
$Py = Join-Path $Venv 'Scripts\python.exe'
$LogDir = Join-Path $Root 'logs'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
function Run([string]$Exe,[string[]]$Arguments,[string]$WorkingDir=$Root) {
  Push-Location -LiteralPath $WorkingDir
  try { & $Exe @Arguments; if($LASTEXITCODE -ne 0) { throw "Failed ($LASTEXITCODE): $Exe $($Arguments -join ' ')" } }
  finally { Pop-Location }
}
function Resolve-Python {
  if(Test-Path -LiteralPath $Py) { return $Py }
  if(Get-Command py -ErrorAction SilentlyContinue) { return 'py' }
  if(Get-Command python -ErrorAction SilentlyContinue) { return 'python' }
  throw 'Python nicht installiert. Menuepunkt 2 verwenden.'
}
function Confirm-Action([string]$Message) {
  $reply = Read-Host "$Message [JA eingeben]"
  return $reply -ceq 'JA'
}
function Tools {
  Write-Host "`n--- TOOLCHAIN READ-ONLY ---" -ForegroundColor Cyan
  foreach ($spec in @(@('python','--version'),@('py','--version'),@('node','--version'),@('npm','--version'),@('winget','--version'),@('git','--version'),@('gh','--version'),@('cmake','--version'),@('dotnet','--version'),@('cl','/Bv'),@('msbuild','-version'))) {
    $cmd = Get-Command $spec[0] -ErrorAction SilentlyContinue
    if ($cmd) { Write-Host "[FOUND] $($spec[0]) : $($cmd.Source)"; & $cmd.Source $spec[1] 2>&1 | Select-Object -First 2 | Out-Host }
    else { Write-Host "[MISSING/NOT IN PATH] $($spec[0])" -ForegroundColor Yellow }
  }
  if(Get-Command python -ErrorAction SilentlyContinue) { Run 'python' @((Join-Path $Root 'tools\diagnose.py'),'--root',$Root,'--output',(Join-Path $LogDir 'diagnostic.json')) }
}
$WingetPackages = [ordered]@{
  'python'='Python.Python.3.13';'node'='OpenJS.NodeJS.LTS';'git'='Git.Git';
  'gh'='GitHub.cli';'cmake'='Kitware.CMake';'dotnet'='Microsoft.DotNet.SDK.8';
  'vsbuild'='Microsoft.VisualStudio.2022.BuildTools'
}
function InstallTool {
  if(-not(Get-Command winget -ErrorAction SilentlyContinue)) { throw 'winget fehlt. App Installer aus Microsoft Store oder Microsoft-Dokumentation installieren.' }
  Write-Host 'Installationen/Upgrades koennen Netzverkehr, Lizenzbedingungen, Adminrechte und Neustart erfordern.' -ForegroundColor Yellow
  Write-Host "Moegliche IDs: $($WingetPackages.Keys -join ', ')"
  $choice=(Read-Host 'Welche Tool-ID installieren/aktualisieren? (leer=abbrechen)').Trim()
  if(-not $WingetPackages.Contains($choice)) { Write-Host 'Abgebrochen.';return }
  $id=$WingetPackages[$choice]
  $existing=Get-Command $choice -ErrorAction SilentlyContinue
  if(-not(Confirm-Action "winget install/upgrade $id? Keine verifizierte 0-EUR-Kostenzusage fuer Drittanbieterdownloads")) {return}
  if($existing) { Run 'winget' @('upgrade','--id',$id,'--exact','--source','winget') }
  else {Run 'winget' @('install','--id',$id,'--exact','--source','winget')}
  Write-Host 'Terminal neu starten, falls PATH aktualisiert wurde.'
}
function Prepare {
  if(-not(Test-Path -LiteralPath $Py)) {
    $base=Resolve-Python
    if($base -eq 'py') {Run 'py' @('-3','-m','venv',$Venv)} else {Run $base @('-m','venv',$Venv)}
  }
  $requirements=Join-Path $Project $Config.requirements_file
  if(Test-Path -LiteralPath $requirements) {
    if(Confirm-Action 'Python-Projektpakete in der isolierten .buildenv installieren/aktualisieren?') {
      Run $Py @('-m','pip','install','--disable-pip-version-check','-r',$requirements)
    } else {throw 'Dependencies not approved; aborting launch/build'}
  }
}
function Tests {
  Prepare
  $testArgs=@($Config.test_command)
  if($testArgs.Count -eq 0) {throw 'test_command not configured'}
  Run $Py $testArgs $Project
}
function PythonStart {
  Prepare
  $entry=Join-Path $Project $Config.python_entry
  if(-not(Test-Path -LiteralPath $entry)) { throw "Entry fehlt: $entry" }
  $arguments=@($entry)+@($Config.python_args)
  Run $Py $arguments $Project
}
function SyncAssets {
  Copy-Item -LiteralPath (Join-Path $Root 'project.config.json') -Destination (Join-Path $Root 'electron\config.json') -Force
  $image=Join-Path $Root 'assets\bootscreen.png'
  if(Test-Path -LiteralPath $image) {Copy-Item -LiteralPath $image -Destination (Join-Path $Root 'electron\renderer\bootscreen.png') -Force}
}
function ElectronDependencies {
  if(-not(Get-Command node -ErrorAction SilentlyContinue)) {throw 'Node.js fehlt'}
  if(-not(Get-Command npm -ErrorAction SilentlyContinue)) {throw 'npm fehlt'}
  $edir=Join-Path $Root 'electron'
  if(-not(Test-Path -LiteralPath (Join-Path $edir 'package-lock.json'))) {
    if(-not(Confirm-Action 'npm Lockfile aus verifizierbarer Registry erzeugen?')) {throw 'Lockfile generation not approved'}
    Run 'npm' @('install','--package-lock-only','--ignore-scripts','--no-audit','--no-fund') $edir
    if(-not(Test-Path -LiteralPath (Join-Path $edir 'package-lock.json'))) {throw 'Lockfile creation failed'}
  }
  if(Confirm-Action 'Electron-Abhaengigkeiten nach Lockfile installieren (npm ci)?') {Run 'npm' @('ci','--no-audit','--no-fund') $edir} else {throw 'Dependencies not approved'}
}
function SetupControl {
  if(-not(Get-Command node -ErrorAction SilentlyContinue)){throw 'Node.js fehlt. Menuepunkt 2.'}
  if(-not(Get-Command npm -ErrorAction SilentlyContinue)){throw 'npm fehlt. Menuepunkt 2.'}
  $edir=Join-Path $Root 'electron'
  if(-not(Test-Path (Join-Path $edir 'node_modules\electron\package.json'))){
    if(-not(Confirm-Action 'Electron npm-Abhaengigkeiten nach Lockfile installieren?')){return}
    if(-not(Test-Path (Join-Path $edir 'package-lock.json'))){
      if(-not(Confirm-Action 'Electron package-lock.json zuerst erzeugen?')){return}
      Run 'npm' @('install','--package-lock-only','--ignore-scripts','--no-audit','--no-fund') $edir
    }
    Run 'npm' @('ci','--no-audit','--no-fund') $edir
  }
  $repair=Join-Path $Root 'tools\electron-runtime-r061.ps1'
  try { & $repair -RepairMarker;return } catch {Write-Host $_ -ForegroundColor Yellow}
  if(-not(Confirm-Action 'Offizielle Electron Runtime mit SHA256 von GitHub herunterladen und gezielt reparieren?')){return}
  & $repair -RepairMarker -InstallVerifiedRuntime
}
function ElectronStart {
  SyncAssets
  ElectronDependencies
  if($Config.launch_mode -ne 'python_backend') {throw 'Nur python_backend unterstuetzt; kein stiller anderer Einstieg'}
  Prepare
  $exe=(Join-Path $Root 'electron\node_modules\.bin\electron.cmd')
  if(-not(Test-Path -LiteralPath $exe)) { throw 'electron not installed' }
  $env:UNIVERSAL_PROJECT_ROOT=$Project
  $env:UNIVERSAL_PYTHON=$Py
  $env:UNIVERSAL_PYTHON_ENTRY=$Config.python_entry
  Run $exe @((Join-Path $Root 'electron'))
}
function Build([string]$Kind) {
  SyncAssets
  Tests
  ElectronDependencies
  if(-not(Confirm-Action "Windows-$Kind-Build starten? Projekt-Backend muss HTTP-Oberflaeche anbieten.")) {return}
  $env:UNIVERSAL_PROJECT_ROOT=$Project
  $env:UNIVERSAL_PYTHON=$Py
  $env:UNIVERSAL_PYTHON_ENTRY=$Config.python_entry
  $edir=Join-Path $Root 'electron'
  if(-not(Confirm-Action 'PyInstaller im isolierten venv installieren/aktualisieren?')) {throw 'PyInstaller approval required'}
  Run $Py @('-m','pip','install','--disable-pip-version-check','--upgrade','pyinstaller')
  Run $Py @((Join-Path $Root 'tools\pack_backend.py'))
  Run 'npm' @('run',$(if($Kind -eq 'portable'){'build:portable'}else{'build:setup'})) $edir
}
try {
  if($Action -ne 'menu') {switch ($Action.ToLowerInvariant()) {
    'scan' {Tools};'install' {InstallTool};'prepare' {Prepare};'test' {Tests};
    'run-python' {PythonStart};'run-electron' {ElectronStart};'portable' {Build 'portable'};
    'setup' {Build 'setup'};'setup-control' {SetupControl};default {throw "Unknown action: $Action"}
  };exit 0}
  while ($true) {
    Write-Host "`n===== UNIVERSAL PYTHON / ELECTRON BUILDKIT R01 =====" -ForegroundColor Magenta
    Write-Host '1  Toolcheck (read-only)'
    Write-Host '2  Tool installieren/aktualisieren (einzeln mit Freigabe)'
    Write-Host '3  Projektumgebung vorbereiten'
    Write-Host '4  Python-Projekt starten'
    Write-Host '5  Tests ausfuehren'
    Write-Host '6  Electron Vollbild starten (Backend + UI)'
    Write-Host '7  Portable EXE bauen (mit Runtime-Gate)'
    Write-Host '8  Windows Setup bauen (mit Runtime-Gate)'
    Write-Host '0  Beenden'
    $choice=Read-Host 'Auswahl'
    try { switch($choice) {
      '1' {Tools};'2' {InstallTool};'3' {Prepare};'4' {PythonStart};
      '5' {Tests};'6' {ElectronStart};'7' {Build 'portable'}; '8' {Build 'setup'};
      '0' {exit 0};default {Write-Host 'Unbekannte Auswahl.'}
    }} catch {Write-Host "ERROR: $_" -ForegroundColor Red; $_ | Out-File -Append -Encoding utf8 (Join-Path $LogDir 'errors.log')}
  }
} catch {Write-Host "ERROR: $_" -ForegroundColor Red;exit 1}
