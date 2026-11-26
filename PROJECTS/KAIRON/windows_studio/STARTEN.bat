@echo off
setlocal
cd /d "%~dp0"
set "WSCRIPT=%SystemRoot%\System32\wscript.exe"
if not exist "%WSCRIPT%" (
  echo Windows Script Host wurde nicht gefunden.
  echo Bitte STARTEN.vbs direkt mit wscript.exe starten.
  pause
  exit /b 1
)
"%WSCRIPT%" //B //Nologo "%~dp0STARTEN.vbs"
exit /b 0
