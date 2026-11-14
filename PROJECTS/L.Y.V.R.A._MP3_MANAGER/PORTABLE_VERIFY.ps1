# Windows PowerShell 5.1 / read-only Portable-Ordner-Abnahme
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$missing = @()
foreach ($rel in @('L.Y.V.R.A._MP3_MANAGER.exe','_internal','assets\app.ico','assets\banner.png','assets\logo.png', 'tools\ffmpeg.exe','tools\ffprobe.exe','BEDIENUNGSANLEITUNG_DE.md','MANUAL_EN.md')) {
  $path=Join-Path $root $rel
  if (-not (Test-Path -LiteralPath $path)) { $missing += $rel; Write-Host "MISSING $rel" }
  else { Write-Host "PASS $rel" }
}
if ($missing.Count -gt 0) { Write-Host 'PORTABLE_INVALID'; exit 2 }
try {
  $ffmpeg = Join-Path $root 'tools\ffmpeg.exe'
  $ffprobe = Join-Path $root 'tools\ffprobe.exe'
  $encoders = & $ffmpeg -hide_banner -encoders 2>&1 | Out-String
  if ($LASTEXITCODE -ne 0 -or $encoders -notmatch '(?m)^\s*[A-Z\.]{6}\s+libmp3lame\s') { throw 'libmp3lame nicht nutzbar' }
  $probeVersion = & $ffprobe -version 2>&1 | Out-String
  if ($LASTEXITCODE -ne 0 -or $probeVersion -notmatch 'ffprobe version') { throw 'ffprobe nicht nutzbar' }
  Write-Host 'PORTABLE_AUDIO_TOOLS_PASS'
  Write-Host 'WINDOWS_PORTABLE_FILE_AND_AUDIO_TOOLS_PASS'
  Write-Host 'EXE_GUI_AND_AUDIO_WORKFLOW_NOT_TESTED_BY_THIS_SCRIPT'
  exit 0
} catch {
  Write-Host ('PORTABLE_AUDIO_TOOLS_FAIL: ' + $_.Exception.Message)
  exit 3
}
