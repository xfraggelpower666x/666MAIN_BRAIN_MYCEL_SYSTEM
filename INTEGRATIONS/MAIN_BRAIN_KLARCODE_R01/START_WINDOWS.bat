@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py -3 -m unittest discover -s tests -v
) else (
  python -m unittest discover -s tests -v
)
if errorlevel 1 (
 echo TESTS FEHLGESCHLAGEN. KEINE AUTOMATISCHE INSTALLATION ODER MUTATION.
 exit /b 1
)
echo Klarcode Manager R01: Python-Tests PASS. Siehe README fuer explizite Befehle.
endlocal
