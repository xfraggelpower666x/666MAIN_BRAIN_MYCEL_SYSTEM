[CmdletBinding()]
param([ValidateSet('menu','check','deps','run','portable','setup','all','legacy')][string]$Action='menu')
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $root
function CheckCommand([string]$name){return [bool](Get-Command $name -ErrorAction SilentlyContinue)}
function EnsureCommand([string]$name,[string]$package){
 if(CheckCommand $name){return}
 if(-not (CheckCommand 'winget')){throw "$name missing. Windows App Installer (winget) must be installed first."}
 Write-Host "Provisioning $name with winget..." -ForegroundColor Cyan
 & winget install --id $package --exact --accept-package-agreements --accept-source-agreements --silent
 if($LASTEXITCODE -ne 0){throw "winget install $package failed"}
 $env:Path=[Environment]::GetEnvironmentVariable('Path','Machine')+';'+[Environment]::GetEnvironmentVariable('Path','User')
 if(-not (CheckCommand $name)){throw "$name installed but not in PATH. Restart BUILD.bat."}
}
# npm may suppress Electron postinstall via allowScripts. A successful npm install
# therefore does not guarantee the actual dist/electron.exe is present.
# Verify the actual unpacked Electron binary. A successful npm exit code is not enough.
function GetElectronExe {
 return (Join-Path $root 'node_modules/electron/dist/electron.exe')
}
function TestElectronRuntime {
 $electronEntry=Join-Path $root 'node_modules/electron/index.js'
 $runtimePointer=Join-Path $root 'node_modules/electron/path.txt'
 $exe=GetElectronExe
 if(-not (Test-Path -LiteralPath $electronEntry -PathType Leaf)){return $false}
 if(-not (Test-Path -LiteralPath $runtimePointer -PathType Leaf)){return $false}
 $runtimeName=[System.IO.File]::ReadAllText($runtimePointer)
 if($runtimeName -cne 'electron.exe'){return $false}
 return ((Test-Path -LiteralPath $exe -PathType Leaf) -and ((Get-Item -LiteralPath $exe).Length -gt 0))
}
function ShowElectronDiagnostics {
 $pkg=Join-Path $root 'node_modules/electron/package.json'
 $ptr=Join-Path $root 'node_modules/electron/path.txt'
 $exe=GetElectronExe
 Write-Host 'Electron runtime diagnostic:' -ForegroundColor Yellow
 Write-Host "  Package present: $(Test-Path -LiteralPath $pkg)"
 Write-Host "  Runtime pointer present: $(Test-Path -LiteralPath $ptr)"
 if(Test-Path -LiteralPath $ptr){Write-Host "  Runtime pointer value: $((Get-Content -LiteralPath $ptr -Raw).Trim())"}
 Write-Host "  Electron EXE present: $(Test-Path -LiteralPath $exe)"
 Write-Host "  Binary skip was set: $($script:ElectronSkipWasSet)"
 Write-Host "  Node: $(& node --version)"
 Write-Host '  Windows certificate/proxy/firewall and Electron download URL should be checked if the installer reported a download error.'
 Write-Host "  Expected binary path: $exe"
}
# Electron's zip extraction can exit successfully without path.txt/electron.exe on
# newer Node 24/26 runtimes. Use a scoped, verified official Node 22 runtime for
# install.js without replacing the user's globally installed Node version.
function GetElectronInstallerNode {
 $current=& node --version
 if($LASTEXITCODE -ne 0){throw 'Unable to determine Node.js version'}
 if($current -notmatch '^v(\d+)\.'){throw "Unrecognized Node.js version: $current"}
 if([int]$Matches[1] -lt 24){return (Get-Command node).Source}
 $toolRoot=Join-Path $root 'build/toolchains/node22'
 $node22=Join-Path $toolRoot 'node.exe'
 if(Test-Path -LiteralPath $node22 -PathType Leaf){
  $v=& $node22 --version
  if($LASTEXITCODE -eq 0 -and $v -match '^v22\.'){Write-Host "Using existing project-local $v for Electron extraction." -ForegroundColor Cyan;return $node22}
  throw "Local Node22 runtime has unexpected version ($v). Inspect $node22 instead of overwriting it."
 }
 $cache=Join-Path $root 'build/toolchains/downloads'
 New-Item -ItemType Directory -Path $cache -Force|Out-Null
 [Net.ServicePointManager]::SecurityProtocol=[Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
 $base='https://nodejs.org/dist/latest-v22.x/'
 Write-Host 'Node 24/26 detected. Retrieving official Node 22 SHA-256 manifest...' -ForegroundColor Cyan
 try{$checks=(Invoke-WebRequest -UseBasicParsing -Uri ($base+'SHASUMS256.txt') -TimeoutSec 90).Content}
 catch{throw "Unable to fetch official Node.js checksums from nodejs.org: $($_.Exception.Message)"}
 # v22.x Windows x64 archive; never accept arbitrary filenames from the remote manifest.
 $matching=@($checks -split "`n" | Where-Object {$_ -match '^([0-9a-f]{64})\s+(node-v22\.[0-9]+\.[0-9]+-win-x64\.zip)\s*$'})
 if($matching.Count -ne 1){throw 'Official Node.js SHA-256 manifest has no unique Node 22 Windows x64 ZIP entry.'}
 $line=$matching[0].Trim()
 if($line -notmatch '^([0-9a-f]{64})\s+(node-v22\.[0-9]+\.[0-9]+-win-x64\.zip)$'){throw 'Node.js checksum entry malformed'}
 $expected=$Matches[1].ToLowerInvariant();$filename=$Matches[2]
 $archive=Join-Path $cache $filename
 if((Test-Path -LiteralPath $archive) -and ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected)){
  throw "Cached Node.js archive hash mismatch: $archive (no automatic deletion)"
 }
 if(-not (Test-Path -LiteralPath $archive)){
  Write-Host "Downloading verified Node.js compatibility runtime: $filename" -ForegroundColor Cyan
  $partial=$archive+'.partial'
  if(Test-Path -LiteralPath $partial){throw "Incomplete prior download exists: $partial. Remove this partial file after inspection."}
  try{Invoke-WebRequest -UseBasicParsing -Uri ($base+$filename) -OutFile $partial -TimeoutSec 300}
  catch{throw "Node.js download failed: $($_.Exception.Message)"}
  if((Get-FileHash -LiteralPath $partial -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected){throw 'Official Node.js ZIP checksum mismatch. Temporary archive retained for inspection.'}
  Move-Item -LiteralPath $partial -Destination $archive
 }
 Add-Type -AssemblyName System.IO.Compression
 Add-Type -AssemblyName System.IO.Compression.FileSystem
 $zip=[System.IO.Compression.ZipFile]::OpenRead($archive)
 try{
  $entry=@($zip.Entries | Where-Object {$_.FullName -eq ($filename -replace '\.zip$','/node.exe')})
  if($entry.Count -ne 1){throw 'Official Node.js ZIP does not contain its expected node.exe entry'}
  New-Item -ItemType Directory -Path $toolRoot -Force|Out-Null
  $temp=Join-Path $toolRoot 'node.exe.partial'
  if(Test-Path -LiteralPath $temp){throw "Incomplete Node.js extraction exists: $temp"}
  [System.IO.Compression.ZipFileExtensions]::ExtractToFile($entry[0],$temp,$false)
  Move-Item -LiteralPath $temp -Destination $node22
 }finally{$zip.Dispose()}
 $verified=& $node22 --version
 if($LASTEXITCODE -ne 0 -or $verified -notmatch '^v22\.'){throw 'Verified Node.js ZIP did not yield a runnable Node 22 executable.'}
 Write-Host "Scoped Electron installer runtime ready: $verified. System Node $current unchanged." -ForegroundColor Green
 return $node22
}
function EnsureElectronRuntime {
 $exe=GetElectronExe
 $ptr=Join-Path $root 'node_modules/electron/path.txt'
 if((Test-Path -LiteralPath $exe -PathType Leaf) -and ((Get-Item -LiteralPath $exe).Length -gt 1000000)){
  # Correct R06.1's observed CRLF marker defect without downloading anything.
  if(-not (TestElectronRuntime)){
   Write-Host 'Electron executable exists: repairing missing/CRLF path.txt marker...' -ForegroundColor Yellow
   [System.IO.File]::WriteAllText($ptr,'electron.exe',[System.Text.Encoding]::ASCII)
  }
  if(TestElectronRuntime){Write-Host 'Electron executable and path.txt verified.' -ForegroundColor Green;return}
 }
 $pkg=Join-Path $root 'node_modules/electron/package.json'
 if(-not (Test-Path -LiteralPath $pkg -PathType Leaf)){
  throw 'Electron npm package missing. Install project dependencies (menu option 2).'
 }
 Write-Host 'Electron executable missing: applying verified R06.1 direct-release recovery.' -ForegroundColor Cyan
 $repair=Join-Path $PSScriptRoot 'INSTALL_ELECTRON_RUNTIME.ps1'
 if(-not (Test-Path -LiteralPath $repair -PathType Leaf)){throw "Electron repair script missing: $repair"}
 # Run in this PowerShell session so exact exceptions, failures and error codes reach BUILD.bat.
 & $repair -ProjectRoot $root
 if(-not (TestElectronRuntime)){
  ShowElectronDiagnostics
  throw 'Verified Electron installer returned but executable/path.txt validation failed.'
 }
 Write-Host 'Electron runtime repaired. Continuing the original AutoDJ build path.' -ForegroundColor Green
}
function EnsureNodeDependencies {
 EnsureCommand 'node' 'OpenJS.NodeJS.LTS'
 if(-not (CheckCommand 'npm')){throw 'npm missing after Node installation'}
 $electronEntry=Join-Path $root 'node_modules/electron/index.js'
 $builderEntry=Join-Path $root 'node_modules/electron-builder/package.json'
 if((-not (Test-Path -LiteralPath $electronEntry)) -or (-not (Test-Path -LiteralPath $builderEntry))){
  Write-Host 'Installing local Node development dependencies...' -ForegroundColor Cyan
  if(Test-Path 'package-lock.json'){ & npm ci --no-audit --no-fund }
  else{ & npm install --no-audit --no-fund }
  if($LASTEXITCODE -ne 0){throw 'npm installation failed'}
 }
 EnsureElectronRuntime
}
function EnsurePythonBuilder {
 EnsureCommand 'python' 'Python.Python.3.13'
 & python -m PyInstaller --version
 if($LASTEXITCODE -eq 0){return}
 & python -m pip install pyinstaller
 if($LASTEXITCODE -ne 0){throw 'PyInstaller installation failed'}
}
function EnsureDependencies {
 EnsureNodeDependencies
 EnsurePythonBuilder
}
function CheckRuntime{
 foreach($name in @('ffmpeg.exe','ffprobe.exe')){
  $binary=Join-Path $root "tools/ffmpeg/$name"
  if(-not (Test-Path $binary)){throw "Missing bundled tool: $name"}
  & $binary -version | Select-Object -First 1
  if($LASTEXITCODE -ne 0){throw "$name failed to start"}
 }
}
# Original R03 mode remains separate. Nothing is installed into the app itself.
function StartLegacyOriginal {
 $script=Join-Path $root 'legacy/tool.ps1'
 if(-not (Test-Path -LiteralPath $script)){throw 'Original legacy/tool.ps1 missing'}
 $legacyFFmpeg=Join-Path $root 'legacy/tools/ffmpeg/bin'
 New-Item -Path $legacyFFmpeg -ItemType Directory -Force | Out-Null
 foreach($name in @('ffmpeg.exe','ffprobe.exe')){
  $source=Join-Path $root "tools/ffmpeg/$name"
  if(-not (Test-Path -LiteralPath $source)){throw "Missing bundled $name"}
  $destination=Join-Path $legacyFFmpeg $name
  $expected=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
  if((-not (Test-Path -LiteralPath $destination)) -or ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash -ne $expected)){
    Copy-Item -LiteralPath $source -Destination $destination -Force
  }
  if((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash -ne $expected){throw "Legacy binary verification failed: $name"}
 }
 Write-Host 'Starting preserved original AutoDJ R03 (no Python/Electron needed)' -ForegroundColor Cyan
 & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $script
 if($LASTEXITCODE -ne 0){throw "Original AutoDJ exited with code $LASTEXITCODE"}
}
function Package([string]$target){
 EnsureDependencies
 CheckRuntime
 New-Item -Path 'build/runtime' -ItemType Directory -Force | Out-Null
 & python -m PyInstaller --noconfirm --clean --onefile --name autodj-engine --distpath build/runtime --workpath build/pyi-work --specpath build/pyi-spec engine/worker.py
 if($LASTEXITCODE -ne 0){throw 'PyInstaller build failed'}
 if($target -eq 'all'){ & npx electron-builder --win portable nsis --x64 }
 else{ & npx electron-builder --win $target --x64 }
 if($LASTEXITCODE -ne 0){throw "electron-builder failed ($target)"}
 Write-Host "Build complete. Check $root/dist" -ForegroundColor Green
}
if($Action -eq 'menu'){
 Write-Host ''
 Write-Host '666 AUTO DJ STUDIO // BUILD CONTROL' -ForegroundColor Magenta
 Write-Host '1 - Check dependencies and bundled FFmpeg'
 Write-Host '2 - Install/prepare developer dependencies'
 Write-Host '3 - Launch Electron directly for development'
 Write-Host '4 - Build portable EXE'
 Write-Host '5 - Build setup with directory selection'
 Write-Host '6 - Build portable EXE + setup'
 Write-Host '7 - Start ORIGINAL R03 AutoDJ (legacy GUI)' 
 $map=@{'1'='check';'2'='deps';'3'='run';'4'='portable';'5'='setup';'6'='all';'7'='legacy'}
 $selection=Read-Host 'Choose 1-7'
 if(-not $map.ContainsKey($selection)){throw 'Invalid choice'}
 $Action=$map[$selection]
}
switch($Action){
 'check' {foreach($name in @('node','npm','python','winget')){Write-Host "$name available: $(CheckCommand $name)"};CheckRuntime}
 'deps' {EnsureDependencies;CheckRuntime}
 'run' {EnsureNodeDependencies;CheckRuntime;& npm start;if($LASTEXITCODE -ne 0){throw 'Electron development start failed'}}
 'portable' {Package 'portable'}
 'setup' {Package 'nsis'}
 'all' {Package 'all'}
 'legacy' {CheckRuntime;StartLegacyOriginal}
}
