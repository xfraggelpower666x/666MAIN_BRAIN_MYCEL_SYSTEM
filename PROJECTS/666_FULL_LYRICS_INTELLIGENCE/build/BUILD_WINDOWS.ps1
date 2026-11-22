param([ValidateSet('check','run','portable','setup','all')][string]$Action='all')
$ErrorActionPreference='Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
function Require($Name){if(-not (Get-Command $Name -ErrorAction SilentlyContinue)){throw "Missing required tool: $Name. Install it explicitly before building."}}
Require node;Require npm;Require py
& py -3 --version; if($LASTEXITCODE -ne 0){throw 'Python 3 unavailable'}
& node --version; if($LASTEXITCODE -ne 0){throw 'Node unavailable'}
if($Action -eq 'check'){Write-Host 'Tool check passed. No installation performed.';exit 0}
& py -3 tests/run_portable_regression.py; if($LASTEXITCODE -ne 0){throw 'Python regression failed'}
& node --check electron/main.cjs; if($LASTEXITCODE -ne 0){throw 'Main process syntax failed'}
& node --check electron/preload.cjs; if($LASTEXITCODE -ne 0){throw 'Preload syntax failed'}
& node --check renderer/app.js; if($LASTEXITCODE -ne 0){throw 'Renderer syntax failed'}
if(-not (Test-Path node_modules/electron)){throw 'npm dependencies missing. Run npm install explicitly.'}
if($Action -eq 'run') { & npm start;exit $LASTEXITCODE }
& py -3 -m PyInstaller --version | Out-Null
if($LASTEXITCODE -ne 0){throw 'PyInstaller missing. Install explicitly with py -3 -m pip install pyinstaller'}
New-Item -ItemType Directory -Force build/runtime | Out-Null
& py -3 -m PyInstaller --onefile --clean --noconfirm --name 666-catalog-bridge --distpath build/runtime --workpath build/pyi-work --specpath build/pyi-spec engine/bridge.py
if($LASTEXITCODE -ne 0 -or -not (Test-Path build/runtime/666-catalog-bridge.exe)){throw 'Python bridge build failed'}
$targets=@();switch($Action){portable{$targets=@('portable')};setup{$targets=@('nsis')};all{$targets=@('portable','nsis')}}
foreach($target in $targets){& npx --no-install electron-builder --win $target --x64;if($LASTEXITCODE -ne 0){throw "Electron target $target failed"}}
Write-Host 'Build artifacts in dist/. Verify both outputs on Windows before release.'
