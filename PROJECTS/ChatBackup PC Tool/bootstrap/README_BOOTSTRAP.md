# Automatischer Windows-Bootstrap — v1.10.5

`START_TOOL.bat` führt zuerst `bootstrap/bootstrap.ps1` aus.

Der Bootstrap prüft für den Quellstart:

- unterstützte Python-Version
- verfügbares Tkinter/Tcl-Tk
- notwendige Python-Runtime-Pakete aus `requirements-runtime.txt`
- aktuell: Pillow für Chat-Bildvorschau und JPG/PNG/WebP/GIF/BMP-Decoding

Fehlende oder veraltete Runtime-Pakete werden automatisch per pip aktualisiert. Node.js und NPM sind weiterhin `NOT_REQUIRED` und werden weder installiert noch verändert.

Beim EXE-Build wird zusätzlich eine isolierte `.venv-build` erzeugt und sowohl `requirements-runtime.txt` als auch `requirements-build.txt` installiert.

Die PowerShell-Datei bleibt wegen Windows PowerShell 5.1 absichtlich ASCII-only im Quelltext, mit UTF-8-BOM und CRLF.


## v1.5.2 Patch-Update-Sicherheit
Bereits kompatibles Python darf den normalen Start nicht wegen eines optionalen Patchupdates blockieren. Direkte python.org-Fallbacks verwenden nur Versionen, fuer die der passende Windows-Installer tatsaechlich erreichbar ist; Source-only-Releases werden nicht als Windows-Installer behandelt.
