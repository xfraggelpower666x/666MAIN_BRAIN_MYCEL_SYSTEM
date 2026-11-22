[CmdletBinding()]
param([ValidateSet('menu','check','deps','test','run','portable','setup','all')][string]$Action='menu')
$ErrorActionPreference='Stop'
Set-Location (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
function Has($name){return [bool](Get-Command $name -ErrorAction SilentlyContinue)}
function Require($name,$id){
 if(Has $name){return}
 if(-not (Has 'winget')){throw "Missing $name; Windows App Installer/winget needed"}
 & winget install --id $id --exact --accept-package-agreements --accept-source-agreements --silent
 if($LASTEXITCODE -ne 0){throw "Installation failed: $name"}
 $env:Path=[Environment]::GetEnvironmentVariable('Path','Machine')+';'+[Environment]::GetEnvironmentVariable('Path','User')
 if(-not (Has $name)){throw "$name installed but not in PATH, restart terminal"}
}
function Deps{
 Require node 'OpenJS.NodeJS.LTS';Require python 'Python.Python.3.13'
 if(-not (Has npm)){throw 'npm missing'}
 if(Test-Path 'package-lock.json'){& npm ci --no-audit --no-fund}
 else{& npm install --no-audit --no-fund;Write-Warning 'Review and commit generated package-lock.json'}
 if($LASTEXITCODE -ne 0){throw 'npm dependency failure'}
 & python -m pip install --upgrade pyinstaller
 if($LASTEXITCODE -ne 0){throw 'PyInstaller dependency failure'}
}
function Test{
 Require node 'OpenJS.NodeJS.LTS';Require python 'Python.Python.3.13'
 & python -m unittest discover -s tests -p 'test_*.py' -v
 if($LASTEXITCODE -ne 0){throw 'Python tests failed'}
 foreach($f in @('app/main.js','app/preload.js','app/renderer.js')){
  & node --check $f
  if($LASTEXITCODE -ne 0){throw "JavaScript syntax failed: $f"}
 }
}
function Package($target){
 Deps;Test
 & (Join-Path $PSScriptRoot 'PROVISION_FFMPEG.ps1')
 if(-not (Test-Path 'build/runtime/ffmpeg.exe') -or -not (Test-Path 'build/runtime/ffprobe.exe')){throw 'Missing FFmpeg runtime'}
 & python -m PyInstaller --noconfirm --clean --onefile --name autodj-engine --distpath build/runtime --workpath build/pyi-work --specpath build/pyi-spec engine/worker.py
 if($LASTEXITCODE -ne 0){throw 'Python standalone engine build failed'}
 if($target -eq 'all'){& npx electron-builder --win portable nsis --x64}
 else{& npx electron-builder --win $target --x64}
 if($LASTEXITCODE -ne 0){throw "electron-builder failure: $target"}
}
if($Action -eq 'menu'){
 Write-Host '666 AUTO DJ | 1 CHECK 2 DEPS 3 TEST 4 RUN 5 PORTABLE 6 SETUP 7 ALL' -ForegroundColor Magenta
 $map=@{'1'='check';'2'='deps';'3'='test';'4'='run';'5'='portable';'6'='setup';'7'='all'}
 $choice=Read-Host 'Selection'
 if(-not $map.ContainsKey($choice)){throw 'Invalid selection'}
 $Action=$map[$choice]
}
switch($Action){
 'check'{Get-Command node,npm,python,winget -ErrorAction SilentlyContinue|Select-Object Name,Source}
 'deps'{Deps}
 'test'{Test}
 'run'{Deps;& npm start;if($LASTEXITCODE -ne 0){throw 'Electron direct start failed'}}
 'portable'{Package 'portable'}
 'setup'{Package 'nsis'}
 'all'{Package 'all'}
}
