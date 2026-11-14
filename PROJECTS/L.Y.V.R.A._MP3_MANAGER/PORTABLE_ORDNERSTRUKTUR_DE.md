# L.Y.V.R.A. - MP3 MANAGER v2.32 — Portable Ordnerstruktur

Nach `L.Y.V.R.A._MP3_MANAGER.bat build` wird unter `dist/L.Y.V.R.A._MP3_MANAGER/` ein vollständiger portabler Ordner erzeugt. Den gesamten Ordner kopieren, nicht nur die EXE. Im Ordner `L.Y.V.R.A._MP3_MANAGER.bat` zum Starten, Prüfen und für die Audio-Tools verwenden.

```text
dist/
  L.Y.V.R.A._MP3_MANAGER/
    L.Y.V.R.A._MP3_MANAGER.exe
    _internal/              (PyInstaller-Python und Runtime-Dateien)
    assets/                 (Originalgrafiken, Icon, Banner)
    tools/
      ffmpeg.exe
      ffprobe.exe
    BEDIENUNGSANLEITUNG_DE.md
    MANUAL_EN.md
    README.txt
    L.Y.V.R.A._MP3_MANAGER.bat
    PORTABLE_VERIFY.ps1
    PORTABLE_STATUS.txt
```

`tools/ffmpeg.exe` und `tools/ffprobe.exe` werden beim Build aus vorhandenen lokalen Installationen kopiert. Ohne diese Programme wird der Build als unvollständig gemeldet. Die Python-Virtualenv bleibt außerhalb des portablen Ausgabeordners. Es findet kein automatischer Download ohne Zustimmung statt.

**Wichtig:** Dieser Build wird auf Windows mit installiertem PyInstaller ausgeführt; das Projekt-ZIP enthält keine bereits kompilierte Windows-EXE und keine FFmpeg-Binärdateien.
