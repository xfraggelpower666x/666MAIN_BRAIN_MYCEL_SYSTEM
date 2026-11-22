[CmdletBinding()]
param([string]$SourceArchive='')
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$target=Join-Path $root 'build/runtime'
New-Item -Path $target -ItemType Directory -Force|Out-Null
$expected=@{
 'ffmpeg.exe'='1a65d5b0b10d8d9a81d2824a3538046a40ed3607c906b335a166add87613f705'
 'ffprobe.exe'='54b944d6095c4588d7548424d7acd5118390a9d4f01b1c92f841547fc9a7429c'
}
if(-not $SourceArchive){
 $candidates=@((Join-Path $root 'tools/source/666_AUTO_DJ_R02_WINDOWS_ABNAHME_GATE_R03.zip'),(Join-Path $root '666_AUTO_DJ_R02_WINDOWS_ABNAHME_GATE_R03.zip'))
 $SourceArchive=@($candidates|Where-Object {Test-Path -LiteralPath $_}|Select-Object -First 1)[0]
}
foreach($name in @('ffmpeg.exe','ffprobe.exe')){
 $out=Join-Path $target $name
 if((Test-Path -LiteralPath $out) -and (Get-FileHash -LiteralPath $out -Algorithm SHA256).Hash.ToLowerInvariant() -eq $expected[$name]){
  Write-Host "Verified cached $name";continue
 }
 if(-not $SourceArchive -or -not (Test-Path -LiteralPath $SourceArchive)){throw "Original R03 source archive required in tools/source; missing verified $name"}
 Add-Type -AssemblyName System.IO.Compression
 Add-Type -AssemblyName System.IO.Compression.FileSystem
 $zip=[System.IO.Compression.ZipFile]::OpenRead($SourceArchive)
 try{
  $entries=@($zip.Entries|Where-Object {$_.FullName -like "*/tools/ffmpeg/bin/$name"})
  if($entries.Count -ne 1){throw "Expected one $name binary in R03 archive"}
  $temp="$out.partial"
  if(Test-Path -LiteralPath $temp){Remove-Item -LiteralPath $temp -Force}
  [System.IO.Compression.ZipFileExtensions]::ExtractToFile($entries[0],$temp,$true)
  $hash=(Get-FileHash -LiteralPath $temp -Algorithm SHA256).Hash.ToLowerInvariant()
  if($hash -ne $expected[$name]){Remove-Item -LiteralPath $temp -Force;throw "Hash mismatch $name"}
  Move-Item -LiteralPath $temp -Destination $out -Force
 }finally{$zip.Dispose()}
 & $out -version|Select-Object -First 1
 if($LASTEXITCODE -ne 0){throw "$name version check failed"}
}
Write-Host 'FFmpeg and FFprobe verified for embedding.'
