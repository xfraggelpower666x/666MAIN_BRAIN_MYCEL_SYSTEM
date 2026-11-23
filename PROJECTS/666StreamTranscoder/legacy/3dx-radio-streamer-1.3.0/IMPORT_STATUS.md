# Importstatus — 3DX Radio Streamer 1.3.0

Quelle: vom Nutzer bereitgestelltes `3dx-radio-streamer-1.3.0.zip`.
Upstream-Referenz: https://github.com/Deaeath/3dx-radio-streamer (Git-Blob-SHAs mit dem Archiv abgeglichen).

## GitHub-Projektverzeichnis
`PROJECTS/3dx-radio-streamer-1.3.0/` im Branch `666MAIN_BRAIN`.

- 41 originale UTF-8-Text- und Codedateien (Python, Batch, PowerShell, Inno Setup, Dokumentation, Tests, SVG).
- Keine Quelltextdateien stillschweigend ersetzt oder bearbeitet.
- 9 im ZIP enthaltene Binärassets (*.png, *.ico) konnten nicht direkt durch die verfügbaren GitHub-Textwerkzeuge übertragen. Diese Assets sind **nicht** Teil dieses GitHub-Imports.
- `tools/restore_original_assets.py` lädt nur diese 9 fehlenden Originaldateien mit unveränderter SHA-Prüfung aus dem öffentlichen Upstream nach; ein separater Git-Commit wäre nötig, um sie anschließend dauerhaft ins Repository einzubringen.
- Upstream besitzt zusätzlich `docs/images/host-it-myself.png`, die **nicht** Teil des Nutzerarchivs ist und daher bewusst nicht importiert wurde.

## Einstieg
`RadioStreamer.py` oder `Start-RadioStreamer.bat`.
`requirements.txt` enthält Laufzeitabhängigkeiten, `requirements-build.txt` die Build-Abhängigkeiten.

## Prüfungen
30 Python-Dateien des hochgeladenen ZIPs wurden lokal mit `compile(..., 'exec')` auf Syntax geprüft: 0 Syntaxfehler.
Keine native Windows-, UI-, Audio-, Netzwerk- oder Installer-End-to-End-Abnahme ausgeführt.
Keine Integration in die vorhandenen Projektfamilien; separater, eigenständiger Quellbaum.
