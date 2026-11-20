@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title L.Y.V.R.A. Audio-Tools Reparatur
if exist "tools\ffmpeg.exe" if exist "tools\ffprobe.exe" (
  echo [PASS] Audio-Tools lokal vorhanden.
  "tools\ffmpeg.exe" -hide_banner -encoders | findstr /i "libmp3lame"
  pause
  exit /b 0
)
where ffmpeg >nul 2>&1 && where ffprobe >nul 2>&1 && (
  echo [PASS] FFmpeg und FFprobe aus PATH vorhanden.
  ffmpeg -hide_banner -encoders | findstr /i "libmp3lame"
  pause
  exit /b 0
)
echo [OFFEN] FFmpeg / FFprobe fehlt.
echo [HINWEIS] Die Installation ueber winget benoetigt Internet und ausdrueckliche Zustimmung.
where winget >nul 2>&1 || (echo winget nicht vorhanden. Lege ffmpeg.exe und ffprobe.exe selbst in tools. & pause & exit /b 2)
choice /C JN /M "FFmpeg via winget installieren (nur nach deiner Zustimmung)"
if errorlevel 2 exit /b 3
winget install --id Gyan.FFmpeg --exact --accept-source-agreements --accept-package-agreements
if errorlevel 1 (echo [FEHLER] Installation fehlgeschlagen. & pause & exit /b 4)
echo [INFO] Falls PATH noch nicht aktualisiert wurde, CMD neu starten.
pause
