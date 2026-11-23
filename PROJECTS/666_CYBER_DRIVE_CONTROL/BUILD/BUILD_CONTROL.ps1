# 666 Cyber Drive Control — central one-batch build host, never shipped in app.
# Only one BAT at project root; all actions here are developer-time operations.
[CmdletBinding()]
param([ValidateSet('Menu','BuildBoth')][string]$Action='Menu')
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$App = Join-Path $Root 'r19-electron'
$Legacy = Join-Path $Root 'r18-legacy'
$Venv = Join-Path $Root '.build-venv'
$Metrics = Join-Path $App 'build\engine\666CyberMetrics.exe'
$Reports = Join-Path $Root 'BUILD\REPORTS'
New-Item -ItemType Directory -Force $Reports | Out-Null
$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$Report = Join-Path $Reports "BUILD_$Stamp.log"
function Log([string]$msg) { $t="[$(Get-Date -Format 'HH:mm:ss')] $msg"; Write-Host $t; Add-Content -LiteralPath $Report -Value $t }
function Run([string]$file, [string[]]$arguments) {
  Log ("RUN: " + $file + ' ' + ($arguments -join ' '))
  & $file @arguments
  if ($LASTEXITCODE -ne 0) { throw "$file exited with $LASTEXITCODE" }
}
function Find-Command([string]$cmd) {
  $x=Get-Command $cmd -ErrorAction SilentlyContinue
  if ($x) { return $x.Source }; return $null
}
function Ensure-Winget { if (-not (Find-Command 'winget')) { throw 'winget unavailable. Install Microsoft App Installer or provision Node/Python manually.' } }
function Ensure-Node {
  $node=Find-Command 'node'; $npm=Find-Command 'npm.cmd'
  $ok=$false
  if ($node -and $npm) {
    # Native PowerShell argument quoting can strip JS string quotes on Windows.
    # Parse the stable CLI version text instead of relying on node -p.
    $v=(& $node --version | Select-Object -First 1)
    if ($LASTEXITCODE -eq 0 -and $v -match '^v([0-9]+)\.') {
      if ([int]$Matches[1] -ge 20) { $ok=$true }
    }
  }
  if (-not $ok) {
    Ensure-Winget
    Log 'Installing required Node.js LTS via winget.'
    Run 'winget' @('install','--id','OpenJS.NodeJS.LTS','-e','--accept-package-agreements','--accept-source-agreements')
    $env:Path=[Environment]::GetEnvironmentVariable('Path','Machine')+';'+[Environment]::GetEnvironmentVariable('Path','User')
  }
  if (-not (Find-Command 'npm.cmd')) { throw 'npm not available after installation. Reopen this build starter.' }
}
function Python-Base {
  $py=Find-Command 'py.exe'
  if ($py) {
    & $py -3.13 -c 'import sys; assert sys.version_info[:2] == (3,13)' 2>$null
    if ($LASTEXITCODE -eq 0) { return @($py,'-3.13') }
  }
  $p=Find-Command 'python.exe'
  if ($p) {
    & $p -c 'import sys; assert sys.version_info[:2] == (3,13)' 2>$null
    if ($LASTEXITCODE -eq 0) { return @($p) }
  }
  Ensure-Winget
  Log 'Installing Python 3.13 via winget (build host only).'
  Run 'winget' @('install','--id','Python.Python.3.13','-e','--accept-package-agreements','--accept-source-agreements')
  $env:Path=[Environment]::GetEnvironmentVariable('Path','Machine')+';'+[Environment]::GetEnvironmentVariable('Path','User')
  $py=Find-Command 'py.exe'
  if ($py) { return @($py,'-3.13') }
  throw 'Python 3.13 not resolvable: reopen starter, do not build partial package.'
}
function Ensure-Source {
  if (-not (Test-Path (Join-Path $Legacy 'src\klrw\drive_workspace.py')) -or
      -not (Test-Path (Join-Path $Legacy 'src\klrw\windows_logical_io.py')) -or
      -not (Test-Path (Join-Path $Legacy 'pyproject.toml'))) {
    throw 'BUILD_BLOCKED: Full original R18 source absent in r18-legacy. Import/verify source before packaging.'
  }
}
function Ensure-Dependencies {
  Ensure-Node
  $p = Python-Base
  if (-not (Test-Path (Join-Path $Venv 'Scripts\python.exe'))) {
    Log 'Creating isolated Python build environment.'
    Run $p[0] (@($p | Select-Object -Skip 1) + @('-m','venv',$Venv))
  }
  $script:BuildPython=Join-Path $Venv 'Scripts\python.exe'
  Run $script:BuildPython @('-m','pip','install','--upgrade','pip','setuptools','wheel')
  Run $script:BuildPython @('-m','pip','install','--upgrade','pyinstaller','psutil','pytest')
  # A lockfile is mandatory for reproducible Node release builds; create in build phase only.
  if (-not (Test-Path (Join-Path $App 'package-lock.json'))) {
    Push-Location $App
    try { Run 'npm.cmd' @('install','--package-lock-only','--ignore-scripts','--no-audit','--no-fund') }
    finally { Pop-Location }
  }
  Push-Location $App
  try { Run 'npm.cmd' @('ci','--no-audit','--no-fund') }
  finally { Pop-Location }
}
function Build-Engine {
  Ensure-Source
  if (-not $script:BuildPython) { Ensure-Dependencies }
  $dest=Join-Path $App 'build\engine'
  New-Item -Force -ItemType Directory $dest | Out-Null
  New-Item -Force -ItemType Directory (Join-Path $Root 'BUILD\work') | Out-Null
  # Build from real R18 source; dynamic import must be collected into the frozen sidecar.
  Run $script:BuildPython @('-m','PyInstaller','--noconfirm','--clean','--onefile',
     '--name','666CyberMetrics','--distpath',$dest,
     '--workpath',(Join-Path $Root 'BUILD\work'),
     '--specpath',(Join-Path $Root 'BUILD\work'),
     '--paths',(Join-Path $Legacy 'src'),
     '--hidden-import','klrw.drive_workspace','--hidden-import','klrw.windows_logical_io',
     '--collect-submodules','klrw',
     (Join-Path $App 'bridge\volume_metrics.py'))
  if (-not (Test-Path $Metrics)) { throw 'Metrics executable not found after PyInstaller build' }
}
function Check-Release {
  if (-not (Test-Path $Metrics)) { throw 'BUILD_BLOCKED: Python engine not bundled; run Build Engine first.' }
  if (-not (Test-Path (Join-Path $App 'node_modules\electron'))) { throw 'BUILD_BLOCKED: node_modules missing.' }
  Ensure-Source
}
function Verify-R18 {
  Ensure-Source
  if (-not $script:BuildPython) { Ensure-Dependencies }
  $verifier = Join-Path $Root 'scripts\VERIFY_R18_RELEASE.py'
  Run $script:BuildPython @($verifier)
  Push-Location $Legacy
  $oldPythonPath = $env:PYTHONPATH
  try {
    $env:PYTHONPATH = Join-Path $Legacy 'src'
    Run $script:BuildPython @('-m','pytest','-q','tests')
  } finally {
    $env:PYTHONPATH = $oldPythonPath
    Pop-Location
  }
}
function Build-Target([string]$target) {
  Ensure-Source
  Ensure-Dependencies
  Verify-R18
  # Validate the real R19 renderer preview contract before any packaging.
  Run 'node' @('--test',(Join-Path $Root 'tests\test_r19_renderer_contract.cjs'))
  # Run R19 D/E integration unit tests against the same R18 sources.
  $savedPythonPath = $env:PYTHONPATH
  try {
    $env:PYTHONPATH = (Join-Path $Legacy 'src') + ';' + (Join-Path $App 'bridge')
    Run $script:BuildPython @('-m','pytest','-q',(Join-Path $Root 'tests\test_r19_features.py'))
  } finally {
    $env:PYTHONPATH = $savedPythonPath
  }
  Build-Engine
  Check-Release
  if ($target -eq 'both') { Check-FrozenEngine }
  Push-Location $App
  try {
    Run 'npm.cmd' @('run',("dist:"+$target))
    Log ('Release files: '+(Join-Path $App 'dist'))
    if ($target -eq 'both') { Verify-ReleaseArtifacts }
  } finally { Pop-Location }
}
function Verify-ReleaseArtifacts {
  $dist=Join-Path $App 'dist'
  $outputs=@(Get-ChildItem -LiteralPath $dist -File -Filter '*.exe')
  foreach ($kind in @('PORTABLE','SETUP')) {
    $matches=@($outputs | Where-Object { $_.Name.EndsWith("-$kind.exe") })
    if ($matches.Count -ne 1) { throw "Expected exactly one $kind EXE; found $($matches.Count)" }
    $item=$matches[0]
    if ($item.Length -lt 1048576) { throw "Invalid $kind size" }
    $h=(Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash
    Log "RELEASE $kind $($item.Name) $($item.Length) SHA256=$h"
  }
}
function Check-FrozenEngine {
  $lines=@(& $Metrics --once)
  if ($LASTEXITCODE -ne 0) { throw "Frozen engine smoke failed: $LASTEXITCODE" }
  $valid=0
  foreach($line in $lines) {
    try { $event=$line | ConvertFrom-Json -ErrorAction Stop } catch { continue }
    if ($event.protocol -eq 'cyber-drive.metrics.v2' -and $event.status -eq 'ok') { $valid++ }
  }
  if ($valid -ne 1) { throw "Frozen engine expected one valid snapshot, found $valid" }
  Log 'Frozen engine smoke PASS'
}
function Open-Dev {
  Ensure-Source
  Ensure-Dependencies
  $env:KLRW_PYTHON=$script:BuildPython
  $env:KLRW_R18_SRC=(Join-Path $Legacy 'src')
  Push-Location $App
  try { Run 'npm.cmd' @('start') } finally { Pop-Location }
}
function Test-Compiled {
  Check-Release
  $candidates=Get-ChildItem -LiteralPath (Join-Path $App 'dist') -File -Filter '*.exe' -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match 'PORTABLE' } | Sort-Object LastWriteTime -Descending
  if (-not $candidates) { throw 'Portable EXE missing. Build portable before test.' }
  Log "Testing compiled portable executable: $($candidates[0].FullName)"
  Start-Process -FilePath $candidates[0].FullName -Wait
}
function Show-Menu {
  Write-Host ''
  Write-Host '================ 666 CYBER DRIVE CONTROL - BUILD HOST ================' -ForegroundColor Cyan
  Write-Host '1  Pruefen + fehlende Build-Tools installieren / aktualisieren'
  Write-Host '2  R19 unmittelbar als Entwickler-Version testen'
  Write-Host '3  Python-Engine fuer Portable/Setup einfrieren'
  Write-Host '4  Portable EXE bauen'
  Write-Host '5  Setup EXE bauen (Installationsverzeichnis frei waehlbar)'
  Write-Host '6  Portable + Setup bauen'
  Write-Host '7  Kompilierte portable EXE sofort starten/testen'
  Write-Host '8  Build- und Quellstatus anzeigen'
  Write-Host '9  Git-R18-Quellen verifizieren + Tests + Portable und Setup bauen'
  Write-Host '0  Beenden'
}
Log "Build host started; project $Root"
if ($Action -eq 'BuildBoth') {
  try {
    Build-Target 'both'
    Log 'Unattended Windows build succeeded'
    exit 0
  } catch {
    Log ("BUILD_BLOCKED: "+$_.Exception.Message)
    exit 1
  }
}
while ($true) {
  Show-Menu
  $choice=Read-Host 'Auswahl'
  try {
    switch ($choice) {
      '1' { Ensure-Dependencies; Log 'Dependency setup READY' }
      '2' { Open-Dev }
      '3' { Build-Engine }
      '4' { Build-Target 'portable' }
      '5' { Build-Target 'setup' }
      '6' { Build-Target 'both' }
      '7' { Test-Compiled }
      '8' { Log "R18 original source present: $(Test-Path (Join-Path $Legacy 'src\klrw\drive_workspace.py'))"; Log "Frozen engine present: $(Test-Path $Metrics)"; Log "Node: $(Find-Command 'node')"; Log "Build report: $Report" }
      '9' {
        Log 'R18 original sources are versioned in GitHub. No ZIP input is required.'
        Build-Target 'both'
        Log 'Build finished. Clean Windows host acceptance and installer validation still required.'
      }
      '0' { Log 'Exit'; exit 0 }
      default { Write-Host 'Unknown option.' }
    }
  } catch {
    Log ("ERROR: " + $_.Exception.Message)
    Write-Host 'BUILD_BLOCKED / ERROR — see BUILD\REPORTS.' -ForegroundColor Red
  }
}
