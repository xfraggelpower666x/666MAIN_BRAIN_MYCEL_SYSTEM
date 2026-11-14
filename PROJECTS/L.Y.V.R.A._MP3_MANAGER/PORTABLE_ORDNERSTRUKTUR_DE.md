# L.Y.V.R.A. - MP3 MANAGER v2.32 — Portable Ordnerstruktur

Nach `BUILD_PORTABLE_EXE.bat` wird unter `dist/L.Y.V.R.A._MP3_MANAGER/` ein vollständiger portabler Ordner erzeugt. Den gesamten Ordner kopieren, nicht nur die EXE.

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
    REPARATUR_AUDIO_TOOLS.bat
    PORTABLE_STATUS.txt
```

`tools/ffmpeg.exe` und `tools/ffprobe.exe` werden beim Build aus vorhandenen lokalen Installationen kopiert. Ohne diese Programme wird der Build als unvollständig gemeldet. Die Quell-BAT-Dateien und Python-Virtualenv bleiben außerhalb des portablen Ausgabeordners. Es findet kein automatischer Download ohne Zustimmung statt.

**Wichtig:** Dieser Build wird auf Windows mit installiertem PyInstaller ausgeführt; das Projekt-ZIP enthält keine bereits kompilierte Windows-EXE und keine FFmpeg-Binärdateien.
