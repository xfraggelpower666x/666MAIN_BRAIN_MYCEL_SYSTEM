@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
echo.
echo ===========================================================
echo  666TRACKDESIGNHUB - SYSTEMPRUEFUNG ^& REPO-SICHERUNG
 echo  Nur lokale Pruefung. Kein automatischer GitHub-Write.
echo ===========================================================
echo.
where py >nul 2>&1
if not errorlevel 1 (
    set "PY=py -3"
) else (
    where python >nul 2>&1
    if errorlevel 1 (
       echo [BLOCKIERT] Python 3.10 oder neuer ist erforderlich.
       pause
       exit /b 2
    )
    set "PY=python"
)
:menu
echo.
echo   1 - Vollstaendige Current- und Subfacettenpruefung
echo   2 - Python-Regressionstests ausfuehren
echo   3 - Repo-Systembackup ZIP erstellen ^(ausserhalb Git-Repo^)
echo   4 - Hub-Monitor als lokale HTML-Datei erzeugen
echo   5 - Beenden
echo.
set /p SEL=Auswahl: 
if "%SEL%"=="1" (
    %PY% tools\verify_and_backup.py
    goto done
)
if "%SEL%"=="2" (
    %PY% -m unittest discover -s tests -v
    goto done
)
if "%SEL%"=="3" (
    where git >nul 2>&1
    if errorlevel 1 (
        echo [BLOCKIERT] Git for Windows fehlt.
        goto done
    )
    %PY% tools\verify_and_backup.py --backup-dir "%USERPROFILE%\Documents\666TDH_BACKUPS"
    goto done
)
if "%SEL%"=="4" (
    %PY% tdh.py 666TDH DASHBOARD --html "%TEMP%\666TDH_HUB_DASHBOARD.html"
    if not errorlevel 1 start "" "%TEMP%\666TDH_HUB_DASHBOARD.html"
    goto done
)
if "%SEL%"=="5" exit /b 0
echo [OFFEN] Ungueltige Auswahl.
goto menu
:done
echo.
pause
goto menu
