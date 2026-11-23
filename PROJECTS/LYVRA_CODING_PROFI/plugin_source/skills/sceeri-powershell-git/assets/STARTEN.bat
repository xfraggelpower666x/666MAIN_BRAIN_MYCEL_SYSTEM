@echo off
setlocal DisableDelayedExpansion
set "SCRIPT=%~dp0Git-Workflow.ps1"
set "RC=2"
if not exist "%SCRIPT%" (
    >&2 echo Git-Workflow.ps1 was not found next to STARTEN.bat.
    goto finish
)
where.exe pwsh.exe >nul 2>&1
if errorlevel 1 goto windows_powershell
pwsh.exe -NoLogo -NoProfile -File "%SCRIPT%" %*
set "RC=%errorlevel%"
goto finish

:windows_powershell
set "PS51=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%PS51%" (
    >&2 echo PowerShell was not found.
    goto finish
)
"%PS51%" -NoLogo -NoProfile -File "%SCRIPT%" %*
set "RC=%errorlevel%"

:finish
if "%~1"=="" pause
exit /b %RC%
