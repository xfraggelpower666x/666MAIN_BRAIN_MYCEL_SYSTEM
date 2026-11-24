# 666 AUTO-DJ STUDIO - scoped Electron runtime recovery
# Adapted from the user's 666 FULL LYRICS INTELLIGENCE R06.1 installer.
# Does not change system Node.js, global npm config or any AutoDJ source/audio assets.
[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$ProjectRoot)
$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$pkg = Join-Path $ProjectRoot 'node_modules/electron'
$manifest = Join-Path $pkg 'package.json'
if(-not (Test-Path -LiteralPath $manifest -PathType Leaf)){throw 'Electron npm package.json missing: install project dependencies first'}
if(-not [Environment]::Is64BitOperatingSystem){throw 'Electron Windows x64 build needs a 64-bit Windows host'}
$version = (Get-Content -LiteralPath $manifest -Raw | ConvertFrom-Json).version
if($version -notmatch '^([3-9][0-9]|[1-9][0-9]{2,})\.\d+\.\d+$'){
 throw "Unrecognized or unsupported Electron version: $version"
}
# Bound the recovered binary to the app's declared direct Electron dependency.
$appPkg=Join-Path $ProjectRoot 'package.json'
if(-not (Test-Path -LiteralPath $appPkg -PathType Leaf)){throw 'AutoDJ package.json missing'}
$declared=(Get-Content -LiteralPath $appPkg -Raw | ConvertFrom-Json).devDependencies.electron
if($declared -cne $version){throw "Electron dependency mismatch: declared $declared, installed $version. Do not overwrite current files."}
$asset = "electron-v$version-win32-x64.zip"
$baseUrl = "https://github.com/electron/electron/releases/download/v$version"
$tmp = Join-Path ([System.IO.Path]::GetTempPath()) ('666-autodj-electron-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tmp -Force | Out-Null
$existing = Join-Path $pkg 'dist'
$marker = Join-Path $pkg 'path.txt'
$backup = Join-Path $pkg ('dist.before-electron-repair-'+[guid]::NewGuid().ToString('N'))
$oldMarkerExists = Test-Path -LiteralPath $marker -PathType Leaf
$oldMarker = if($oldMarkerExists){[System.IO.File]::ReadAllBytes($marker)}else{$null}
$didSwap = $false
try {
 $archive = Join-Path $tmp $asset
 $checksPath = Join-Path $tmp 'SHASUMS256.txt'
 [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
 Write-Host "Downloading official Electron $version checksum manifest..." -ForegroundColor Cyan
 try {Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/SHASUMS256.txt" -OutFile $checksPath -TimeoutSec 90}
 catch {throw "Electron checksum download failed: $($_.Exception.Message)"}
 $lines = @(Get-Content -LiteralPath $checksPath | Where-Object {$_ -match ('^[a-fA-F0-9]{64}\s+\*?'+[regex]::Escape($asset)+'\s*$')})
 if($lines.Count -ne 1){throw "Expected exactly one official SHA256 entry for $asset"}
 $expected=($lines[0] -split '\s+')[0].ToLowerInvariant()
 if($expected -notmatch '^[a-f0-9]{64}$'){throw 'Malformed official SHA256'}
 Write-Host "Downloading official Electron runtime: $asset" -ForegroundColor Cyan
 try {Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/$asset" -OutFile $archive -TimeoutSec 300}
 catch {throw "Electron runtime download failed: $($_.Exception.Message)"}
 $actual=(Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
 if($actual -ne $expected){throw "Electron checksum mismatch. Expected $expected, got $actual. No installation performed."}
 $unpacked=Join-Path $tmp 'dist'
 Expand-Archive -LiteralPath $archive -DestinationPath $unpacked -Force
 $newExe=Join-Path $unpacked 'electron.exe'
 if(-not (Test-Path -LiteralPath $newExe -PathType Leaf)){throw 'Verified Electron ZIP lacks electron.exe'}
 if((Get-Item -LiteralPath $newExe).Length -le 1000000){throw 'Verified Electron executable unexpectedly small'}
 if(Test-Path -LiteralPath $existing){Move-Item -LiteralPath $existing -Destination $backup}
 try {
  Move-Item -LiteralPath $unpacked -Destination $existing
  $didSwap = $true
  # path.txt is consumed as a literal filename; PowerShell Set-Content CRLF breaks it.
  [System.IO.File]::WriteAllText($marker,'electron.exe',[System.Text.Encoding]::ASCII)
  $installedExe=Join-Path $existing 'electron.exe'
  if(-not (Test-Path -LiteralPath $installedExe -PathType Leaf) -or ([System.IO.File]::ReadAllText($marker) -cne 'electron.exe')){
   throw 'Electron runtime validation failed after swap'
  }
 } catch {
  if($didSwap -and (Test-Path -LiteralPath $existing)){Remove-Item -LiteralPath $existing -Recurse -Force}
  if(Test-Path -LiteralPath $backup){Move-Item -LiteralPath $backup -Destination $existing}
  if($oldMarkerExists){[System.IO.File]::WriteAllBytes($marker,$oldMarker)}
  elseif(Test-Path -LiteralPath $marker){Remove-Item -LiteralPath $marker -Force}
  throw
 }
 Write-Host "Electron $version installed and SHA256 verified. System Node untouched." -ForegroundColor Green
 if(Test-Path -LiteralPath $backup){Write-Host "Previous dist preserved: $backup" -ForegroundColor DarkGray}
} finally {
 if(Test-Path -LiteralPath $tmp){Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue}
}
