# G-Helper 0.294 – Komplettpaket

Das ZIP vollständig entpacken. Der Ordner enthält die Build-Skripte aus dem GitHub-Projekt, das Original-Quellarchiv, alle drei Hersteller-Installer und die fertige G-Helper-Setup-EXE.

- **Installieren:** `output\GHelper-0.294-Offline-Setup-x64.exe` starten. Diese Datei enthält die Installationsvoraussetzungen und funktioniert offline. Die Setup-EXE ist unsigniert. Der native Windows- und Treibertest auf ASUS-Hardware steht aus.
- **Neu bauen:** `GHELPER_BUILD.bat` doppelklicken und **1** wählen. Alle Projekteingaben liegen bereits in `eingaben\`. Die Werkzeugprüfung und der NuGet-Restore können Internetzugang benötigen. Ein erfolgreicher Neubau derselben Version ersetzt die bisherige Setup-EXE und ihre Prüfsumme in `output\`.
- **Weiterbearbeiten:** Die Projektanleitung steht in [README.md](README.md), die Build-Eingaben in `build-config.json` und der Prüfstand in [AUDIT.md](AUDIT.md).

## Vollständige Kopie auf GitHub

Im lokalen Checkout des Branches `666MAIN_BRAIN` den Inhalt dieses Ordners nach `PROJECTS/GHelper-Windows-Installer/` kopieren. Vor dem Überschreiben bearbeiteter Dateien den lokalen Stand vergleichen. Die Build-Skripte sind bereits im Repository vorhanden. Für eine vollständige Kopie ergänze die vier Dateien unter `eingaben/` und die zwei Dateien unter `output/`.

Im Repo-Ordner die folgenden Dateien gezielt mit Git hinzufügen. `-f` nimmt die aufgeführten Dateien trotz der lokalen Ignore-Regeln auf.

```powershell
git add -f -- PROJECTS/GHelper-Windows-Installer/eingaben/g-helper-0.294.src.zip PROJECTS/GHelper-Windows-Installer/eingaben/PawnIO_setup.exe PROJECTS/GHelper-Windows-Installer/eingaben/ASUSSystemControlInterfaceV3.exe PROJECTS/GHelper-Windows-Installer/eingaben/windowsdesktop-runtime-10.0.15-win-x64.exe
git add -f -- PROJECTS/GHelper-Windows-Installer/output/GHelper-0.294-Offline-Setup-x64.exe PROJECTS/GHelper-Windows-Installer/output/GHelper-0.294-Offline-Setup-x64.exe.sha256
```

Danach die ausgewählten Dateien committen und zum Branch `666MAIN_BRAIN` pushen. Das Ziel-Repository ist öffentlich.
