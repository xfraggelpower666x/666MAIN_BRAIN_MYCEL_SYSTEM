param([switch]$RepairMarker,[switch]$InstallVerifiedRuntime)
$ErrorActionPreference='Stop'
$Root=Split-Path -Parent $PSScriptRoot
$Pkg=Join-Path $Root 'electron\node_modules\electron'
$Manifest=Join-Path $Pkg 'package.json'
$Exe=Join-Path $Pkg 'dist\electron.exe'
$Marker=Join-Path $Pkg 'path.txt'
if(-not (Test-Path -LiteralPath $Manifest)){throw 'Electron npm-Paket fehlt; bestehendes Paket wird nicht ersetzt.'}
$version=(Get-Content -Raw -LiteralPath $Manifest | ConvertFrom-Json).version
if($version -notmatch '^\d+\.\d+\.\d+$'){throw 'Unbekannte Electron-Paketversion'}
if((Test-Path $Exe) -and ((Get-Item $Exe).Length -gt 1000000)){
  $actual=if(Test-Path $Marker){[IO.File]::ReadAllText($Marker)}else{''}
  if($actual -cne 'electron.exe'){
    if(-not $RepairMarker){throw 'Electron path.txt fehlerhaft. Gezielt reparieren (nach Zustimmung).'}
    [IO.File]::WriteAllText($Marker,'electron.exe',[Text.Encoding]::ASCII)
    Write-Host 'R06.1: Electron path.txt ohne CRLF repariert.'
  }
  Write-Output $Exe
  exit 0
}
if(-not $InstallVerifiedRuntime){throw 'Electron Runtime fehlt; kein automatischer Download.'}
if(-not [Environment]::Is64BitOperatingSystem){throw 'Windows x64 erforderlich.'}
$asset="electron-v$version-win32-x64.zip"
$base="https://github.com/electron/electron/releases/download/v$version"
$tmp=Join-Path ([IO.Path]::GetTempPath()) ('666-buildkit-electron-'+[Guid]::NewGuid().ToString('N'))
[void][IO.Directory]::CreateDirectory($tmp)
try {
  $shaFile=Join-Path $tmp 'SHASUMS256.txt';$archive=Join-Path $tmp $asset
  Invoke-WebRequest -UseBasicParsing -Uri "$base/SHASUMS256.txt" -OutFile $shaFile
  $line=Get-Content $shaFile | Where-Object {$_ -match ([regex]::Escape($asset)+'\s*$')} | Select-Object -First 1
  if(-not $line){throw 'SHA256 des offiziellen Electron-Pakets fehlt'}
  $expected=($line -split '\s+')[0].Trim().ToLowerInvariant()
  if($expected -notmatch '^[a-f0-9]{64}$'){throw 'SHA256-Referenz ungueltig'}
  Invoke-WebRequest -UseBasicParsing -Uri "$base/$asset" -OutFile $archive
  $hash=(Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
  if($hash -cne $expected){throw 'Electron SHA256 stimmt nicht; keine Runtime-Aenderung'}
  $staged=Join-Path $tmp 'dist';Expand-Archive -LiteralPath $archive -DestinationPath $staged
  if(-not (Test-Path (Join-Path $staged 'electron.exe'))){throw 'Electron-Archiv enthaelt keine electron.exe'}
  $dist=Join-Path $Pkg 'dist';$backup=Join-Path $Pkg ('dist.before-repair-'+[Guid]::NewGuid().ToString('N'))
  if(Test-Path $dist){Move-Item $dist $backup}
  try{Move-Item $staged $dist;[IO.File]::WriteAllText($Marker,'electron.exe',[Text.Encoding]::ASCII)}
  catch{if(Test-Path $dist){Remove-Item $dist -Recurse -Force};if(Test-Path $backup){Move-Item $backup $dist};throw}
  Write-Host 'Offizielle Electron-Runtime SHA256-verifiziert installiert. Alte Dist bleibt als Backup.'
  Write-Output (Join-Path $dist 'electron.exe')
}finally{if(Test-Path $tmp){Remove-Item $tmp -Force -Recurse -ErrorAction SilentlyContinue}}
