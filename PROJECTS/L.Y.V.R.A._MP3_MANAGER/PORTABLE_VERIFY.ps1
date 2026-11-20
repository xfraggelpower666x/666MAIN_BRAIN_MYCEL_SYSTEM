# Windows PowerShell 5.1 / read-only Portable-Ordner-Abnahme
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$missing = @()
foreach ($rel in @('L.Y.V.R.A._MP3_MANAGER.exe','assets\app.ico','assets\banner.png','assets\logo.png',
    'tools\ffmpeg.exe','tools\ffprobe.exe','BEDIENUNGSANLEITUNG_DE.md','MANUAL_EN.md',
    'L.Y.V.R.A._MP3_MANAGER.bat','PORTABLE_VERIFY.ps1','HOST_ABNAHME_WINDOWS.bat','HOST_ABNAHME_WINDOWS.ps1',
    '_internal\restoration_lab\__init__.py','_internal\restoration_lab\app.py',
    '_internal\restoration_lab\audio_input.py','_internal\restoration_lab\legacy_app.py',
    '_internal\restoration_lab\manual.py','_internal\restoration_lab\mastering_tools.py',
    '_internal\restoration_lab\metal_ui.py','_internal\restoration_lab\realtime.py',
    '_internal\restoration_lab\reference_engine.py','_internal\restoration_lab\studio_tools.py',
    '_internal\restoration_lab\studio_ui.py',
    '_internal\restoration_lab\assets\RestorationLab.png')) {
  $path = Join-Path $root $rel
  if ((Test-Path -LiteralPath $path -PathType Leaf) -and (Get-Item -LiteralPath $path).Length -gt 0) {
    Write-Host "PASS $rel"
  } else {
    $missing += $rel
    Write-Host "MISSING_OR_EMPTY $rel"
  }
}
if ($missing.Count -gt 0) { Write-Host 'PORTABLE_INVALID'; exit 2 }
$env:PATH = (Join-Path $root 'tools') + ';' + (Join-Path $env:SystemRoot 'System32') + ';' + $env:SystemRoot
try {
  $ffmpeg = Join-Path $root 'tools\ffmpeg.exe'
  $ffprobe = Join-Path $root 'tools\ffprobe.exe'
  foreach ($binary in @((Join-Path $root 'L.Y.V.R.A._MP3_MANAGER.exe'), $ffmpeg, $ffprobe)) {
    $stream = [System.IO.File]::OpenRead($binary)
    try {
      if ($stream.ReadByte() -ne 77 -or $stream.ReadByte() -ne 90) { throw "Windows-Dateisignatur fehlt: $binary" }
    } finally { $stream.Dispose() }
  }
  $encoders = & $ffmpeg -hide_banner -encoders 2>&1 | Out-String
  if ($LASTEXITCODE -ne 0 -or $encoders -notmatch '(?m)^\s*[A-Z\.]{6}\s+libmp3lame\s') { throw 'libmp3lame nicht nutzbar' }
  $probeVersion = & $ffprobe -version 2>&1 | Out-String
  if ($LASTEXITCODE -ne 0 -or $probeVersion -notmatch 'ffprobe version') { throw 'ffprobe nicht nutzbar' }
  & $ffmpeg -nostdin -v error -f lavfi -i 'anullsrc=r=44100:cl=stereo' -t 0.1 -c:a libmp3lame -f null -
  if ($LASTEXITCODE -ne 0) { throw 'libmp3lame-Testkodierung fehlgeschlagen' }
  Write-Host 'PORTABLE_AUDIO_TOOLS_PASS'
  Write-Host 'WINDOWS_PORTABLE_FILE_AND_AUDIO_TOOLS_PASS'
  Write-Host 'EXE_GUI_AND_AUDIO_WORKFLOW_NOT_TESTED_BY_THIS_SCRIPT'
  exit 0
} catch {
  Write-Host ('PORTABLE_AUDIO_TOOLS_FAIL: ' + $_.Exception.Message)
  exit 3
}
