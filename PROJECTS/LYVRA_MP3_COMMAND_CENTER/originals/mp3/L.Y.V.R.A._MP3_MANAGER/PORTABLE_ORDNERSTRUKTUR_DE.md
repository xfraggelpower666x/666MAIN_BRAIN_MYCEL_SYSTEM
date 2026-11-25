# L.Y.V.R.A. - MP3 MANAGER v2.38 — Portable Ordnerstruktur

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
    HOST_ABNAHME_WINDOWS.bat
    HOST_ABNAHME_WINDOWS.ps1
    PORTABLE_STATUS.txt
```

`tools/ffmpeg.exe` und `tools/ffprobe.exe` werden beim Build aus vorhandenen lokalen Installationen kopiert. Ohne diese Programme wird der Build als unvollständig gemeldet. Die Python-Virtualenv bleibt außerhalb des portablen Ausgabeordners. Es findet kein automatischer Download ohne Zustimmung statt.

**Wichtig:** Dieser Build wird auf Windows mit installiertem PyInstaller ausgeführt; das Projekt-ZIP enthält keine bereits kompilierte Windows-EXE und keine FFmpeg-Binärdateien.


## Windows-Abnahme

1. Führe im Paketordner `L.Y.V.R.A._MP3_MANAGER.bat verify` aus. Der Check prüft die mitgelieferten Windows-Dateien, Restoration-Lab-Quelldateien und eine kurze Testkodierung mit dem gebündelten libmp3lame.
2. Starte optional `HOST_ABNAHME_WINDOWS.bat` für einen datierten lokalen JSON-Bericht über die sichtbaren Monitore, Koordinaten, den gemeldeten DPI-Wert und die gebündelten Tool-Dateien.
3. Starte die EXE. Verschiebe Hauptfenster, Monitor und Dateimanager zwischen zwei Monitoren mit unterschiedlicher Skalierung. Prüfe Größe, Position und Bedienbarkeit auf beiden Bildschirmen.
4. Ziehe aus dem Explorer eine WAV und eine MP3 mit Leerzeichen im Namen in den Audio-Browser. Prüfe Typfilter, Auswahl und Exportordner.
5. Exportiere eine bekannte Problemstelle mit **Maximum Quality**. Vergleiche die Original-WAV mit der dekodierten neuen MP3 an derselben Stelle bei angeglichenem Abhörpegel. Halte Zeitmarken und hörbare Unterschiede fest.
