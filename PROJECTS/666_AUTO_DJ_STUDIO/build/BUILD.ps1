[CmdletBinding()]
param([ValidateSet('menu','check','deps','test','run','portable','setup','all')][string]$Action='menu')
$ErrorActionPreference='Stop'; Set-Location (Split-Path -Parent $PSScriptRoot)
function Has($name){return [bool](Get-Command $name -ErrorAction SilentlyContinue)}
function Require($name,$id) {
 if(Has $name){return}
 if(-not (Has 'winget')){throw "$name fehlt. Windows App Installer/winget erforderlich."}
 & winget install --id $id --exact --accept-package-agreements --accept-source-agreements --silent
 if($LASTEXITCODE -ne 0){throw "Installation $name fehlgeschlagen"}
 $env:Path=[Environment]::GetEnvironmentVariable('Path','Machine')+';'+[Environment]::GetEnvironmentVariable('Path','User')
 if(-not (Has $name)){throw "$name nicht im PATH; neues Terminal starten"}
}
function Deps {
 Require node 'OpenJS.NodeJS.LTS';Require python 'Python.Python.3.13'
 & npm install
 if($LASTEXITCODE -ne 0){throw 'npm install fehlgeschlagen'}
 & python -m pip install --upgrade pyinstaller
 if($LASTEXITCODE -ne 0){throw 'PyInstaller fehlgeschlagen'}
}
function Test {
 & python -m unittest discover -s tests -p test_engine.py -v
 if($LASTEXITCODE -ne 0){throw 'Python-Tests fehlgeschlagen'}
 foreach($f in @('app/main.js','app/preload.js','app/renderer.js')){& node --check $f;if($LASTEXITCODE -ne 0){throw "Syntaxfehler $f"}}
}
function Package($target) {
 Deps;Test
 New-Item -Force -ItemType Directory build/runtime|Out-Null
 foreach($tool in @('ffmpeg.exe','ffprobe.exe')){
  $src="tools/ffmpeg/$tool";if(-not (Test-Path $src)){throw "Verified FFmpeg missing: $src"}
  Copy-Item -LiteralPath $src -Destination "build/runtime/$tool" -Force
  & "build/runtime/$tool" -version|Select-Object -First 1
  if($LASTEXITCODE -ne 0){throw "$tool invalid"}
 }
 & python -m PyInstaller --noconfirm --clean --onefile --name autodj-engine --distpath build/runtime --workpath build/pyi-work --specpath build/pyi-spec engine/worker.py
 if($LASTEXITCODE -ne 0){throw 'Python Build failed'}
 if($target -eq 'both'){ & npx electron-builder --win portable nsis --x64 } else { & npx electron-builder --win $target --x64 }
 if($LASTEXITCODE -ne 0){throw "Package $target failed"}
}
if($Action -eq 'menu'){
 Write-Host '666 AUTO DJ | 1 CHECK 2 DEPS 3 TEST 4 RUN 5 PORTABLE 6 SETUP 7 ALL' -ForegroundColor Magenta
 $map=@{'1'='check';'2'='deps';'3'='test';'4'='run';'5'='portable';'6'='setup';'7'='all'}
 $choice=Read-Host 'Selection';if(-not $map.ContainsKey($choice)){throw 'Invalid selection'};$Action=$map[$choice]
}
switch($Action){
 'check' {Get-Command node,npm,python,winget -ErrorAction SilentlyContinue|Select-Object Name,Source}
 'deps' {Deps}
 'test' {Require node 'OpenJS.NodeJS.LTS';Require python 'Python.Python.3.13';Test}
 'run' {Deps;& npm start}
 'portable' {Package 'portable'}
 'setup' {Package 'nsis'}
 'all' {Package 'both'}
}
