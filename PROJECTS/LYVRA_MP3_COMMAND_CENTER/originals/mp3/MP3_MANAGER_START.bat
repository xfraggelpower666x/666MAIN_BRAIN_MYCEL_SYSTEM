@echo off
setlocal EnableExtensions DisableDelayedExpansion
if not exist "%~dp0L.Y.V.R.A._MP3_MANAGER\L.Y.V.R.A._MP3_MANAGER.bat" goto incomplete
if not exist "%~dp0Restoration-Lab-main\__init__.py" goto incomplete
call "%~dp0L.Y.V.R.A._MP3_MANAGER\L.Y.V.R.A._MP3_MANAGER.bat" %*
exit /b %errorlevel%
:incomplete
echo Bitte die ZIP zuerst vollstaendig mit Alle extrahieren entpacken.
pause
exit /b 2
