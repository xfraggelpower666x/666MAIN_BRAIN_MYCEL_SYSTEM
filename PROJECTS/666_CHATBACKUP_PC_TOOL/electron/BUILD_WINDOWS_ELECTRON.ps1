# Optional release candidate only; requires Node/npm and network-sourced Electron runtime.
[CmdletBinding()]param([ValidateSet('Setup','Portable','Both')][string]$Target='Setup')
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$python=Join-Path $root '.venv-build\Scripts\python.exe'
if(-not (Test-Path $python)){throw 'Python build environment missing. Use central menu option 5.'}
if(-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)){throw 'Node/npm missing; not part of offline Python toolchain'}
if(-not (Get-Command node.exe -ErrorAction SilentlyContinue)){throw 'Node.js fehlt'}
# Lockfile/Dependency-Identitaet vor dem teuren PyInstaller-Build nachweisen.
& node.exe (Join-Path $PSScriptRoot 'verify-build-inputs.cjs')
if($LASTEXITCODE -ne 0){throw 'Electron Build-Gate: Lockfile oder Abhaengigkeiten inkonsistent'}
& $python -m PyInstaller --noconfirm --clean --onefile --noconsole --paths (Join-Path $root 'app') --name 666_CHATBACKUP_BRIDGE --distpath (Join-Path $PSScriptRoot 'bin') (Join-Path $PSScriptRoot 'python_bridge.py')
if($LASTEXITCODE -ne 0){throw 'Python bridge PyInstaller failed'}
# Ein integrierter Electron-Build, zwei fachlich getrennte Python-Engines.
$studio=Join-Path $root 'addons\chatback_import_studio'
if(-not (Test-Path (Join-Path $studio 'engine_entry.py'))){throw 'Chatback Import Studio Quelle fehlt'}
& $python -m PyInstaller --noconfirm --clean --onefile --noconsole `
  --name ChatbackStudioEngine --distpath (Join-Path $PSScriptRoot 'bin') `
  --workpath (Join-Path $PSScriptRoot 'build-studio') `
  --specpath (Join-Path $PSScriptRoot 'build-studio-spec') `
  --paths $studio `
  --add-data "$(Join-Path $studio 'gui_index.html');." `
  --add-data "$(Join-Path $studio 'gui.js');." `
  --add-data "$(Join-Path $studio 'gui.css');." `
  (Join-Path $studio 'engine_entry.py')
if($LASTEXITCODE -ne 0 -or -not (Test-Path (Join-Path $PSScriptRoot 'bin\ChatbackStudioEngine.exe'))){throw 'Studio Python Engine Build fehlgeschlagen'}
Push-Location $PSScriptRoot
try {
  if(-not (Test-Path 'node_modules')){throw 'Electron dependencies missing: npm install requires explicit network consent'}
  & node.exe (Join-Path $PSScriptRoot 'verify-electron-runtime.js')
  if($LASTEXITCODE -ne 0){throw 'Electron runtime missing or broken. Use menu option E to approve repair.'}
  $buildStarted=[datetime]::UtcNow
  if($Target -eq 'Setup') { & npm.cmd run build:installer }
  elseif($Target -eq 'Portable') { & npm.cmd run build:portable }
  else { & npm.cmd run build:both }
  if($LASTEXITCODE -ne 0){throw 'Electron installer build failed'}
  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'VERIFY_WINDOWS_ARTIFACTS.ps1') -Target $Target -BuildStartedAt $buildStarted.ToString('o')
  if($LASTEXITCODE -ne 0){throw 'Windows Build Artefakt-Readback fehlgeschlagen'}
} finally {Pop-Location}
