param([Parameter(Mandatory=$true)][string]$ProjectRoot)
$ErrorActionPreference='Stop'
$pkg=Join-Path $ProjectRoot 'node_modules\electron'
$manifest=Join-Path $pkg 'package.json'
if(-not (Test-Path $manifest)){throw 'Electron npm-Paket fehlt'}
$version=(Get-Content $manifest -Raw | ConvertFrom-Json).version
if($version -notmatch '^\d+\.\d+\.\d+$'){throw 'Ungueltige Electron-Version'}
if(-not [Environment]::Is64BitOperatingSystem){throw 'Windows x64 ist erforderlich'}
$asset="electron-v$version-win32-x64.zip"
$base="https://github.com/electron/electron/releases/download/v$version"
$tmp=Join-Path ([IO.Path]::GetTempPath()) ('666-electron-'+[Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tmp -Force | Out-Null
try {
 $archive=Join-Path $tmp $asset
 $shaFile=Join-Path $tmp 'SHASUMS256.txt'
 Write-Host 'Lade Electron direkt von der offiziellen GitHub-Releasequelle...' -ForegroundColor Cyan
 Invoke-WebRequest -Uri "$base/SHASUMS256.txt" -OutFile $shaFile -UseBasicParsing
 $targetLine=Get-Content $shaFile | Where-Object { $_ -match ([regex]::Escape($asset)+'\s*$') } | Select-Object -First 1
 if(-not $targetLine){throw 'SHA256 fuer Electron-Releasepaket nicht gefunden'}
 $expected=($targetLine -split '\s+')[0].Trim().ToLowerInvariant()
 if($expected -notmatch '^[a-f0-9]{64}$'){throw 'Ungueltiger SHA256-Referenzwert'}
 Invoke-WebRequest -Uri "$base/$asset" -OutFile $archive -UseBasicParsing
 $actual=(Get-FileHash -Path $archive -Algorithm SHA256).Hash.ToLowerInvariant()
 if($actual -ne $expected){throw 'SHA256-Konflikt: Electron-Download nicht installiert'}
 $unpacked=Join-Path $tmp 'dist'
 Expand-Archive -Path $archive -DestinationPath $unpacked -Force
 $exe=Join-Path $unpacked 'electron.exe'
 if(-not (Test-Path $exe)){throw 'Archiv enthält keine electron.exe'}
 $existing=Join-Path $pkg 'dist'
 # Existing nonworking runtime remains until the verified official payload is ready.
 $bak=Join-Path $pkg ('dist.before-repair-'+[Guid]::NewGuid().ToString('N'))
 if(Test-Path $existing){Move-Item -Path $existing -Destination $bak}
 try {
  Move-Item -Path $unpacked -Destination $existing
  [System.IO.File]::WriteAllText((Join-Path $pkg 'path.txt'), 'electron.exe', [System.Text.Encoding]::ASCII)
 }catch{
  if(Test-Path $existing){Remove-Item $existing -Recurse -Force}
  if(Test-Path $bak){Move-Item $bak $existing}
  throw
 }
 Write-Host "Electron $version Runtime installiert; SHA256 stimmt." -ForegroundColor Green
 if(Test-Path $bak){Write-Host "Vorheriger Runtime-Rest aufbewahrt unter: $bak" -ForegroundColor DarkGray}
}finally{if(Test-Path $tmp){Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue}}
