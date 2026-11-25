# L.Y.V.R.A. MP3 MANAGER — Electron-Migrationskandidat C01

**Keine Ersetzung des Originals.** Die bestehende Anwendung `../L.Y.V.R.A._MP3_MANAGER/MP3_Manager.pyw` und ihre Medienengine bleiben unverändert. Starte das Original wie bisher mit `MP3_MANAGER_START.bat`.

## Windows-Start (Entwicklungsmodus)
1. Komplettes ZIP entpacken.
2. Node.js, Python 3, FFmpeg und FFprobe prüfen. Der Kandidat installiert keine Pakete ungefragt.
3. Im Ordner `ELECTRON_CANDIDATE` einmalig `npm install` (explizite Nutzerentscheidung, Netzwerk erforderlich).
4. Danach `START_ELECTRON_WINDOWS.bat`.
5. Bei fehlenden Python-Modulen `python -m pip install -r ../L.Y.V.R.A._MP3_MANAGER/requirements.txt` in der eigenen Projektumgebung.

## Ausführung und Grenzen
- Electron bietet Dateiauswahl, Ordnerscan, Codec-/Metadatenanzeige, vorhandenes `media_tools.export_media` für MP3/WAV, Fortschritt, Stopp, eigenes Monitorfenster.
- MP3-Export nutzt Original-FFmpeg-Aufruf (320 kbit/s, libmp3lame), **keine Normalisierung**.
- Das separate Fenster ist verschiebbar auf den zweiten Monitor, kein automatischer Monitorwechsel.
- Der MP4-Cover-Workflow, vollständige ID3-Metadatenbearbeitung, Audio Repair, Restoration Lab und eigenständiger EXE-Portabilitätsnachweis bleiben in Tkinter und sind **noch nicht Electron-feature-parity**.
- Der Electron-Package-Build mit `extraResources` benötigt weiterhin **einen systemweit verfügbaren Python-Interpreter**. Noch kein eigenständiges Windows Portable-Release.
- Kein Upload, keine Repo-Änderungen, keine Hintergrunddienste, keine automatische Softwareinstallation.
- `npm run check` prüft JS-Syntax und den realen Python/FFmpeg-Worker. Der Test kann unter Linux laufen, beweist aber keine Windows-Hostfunktion.

## R06.1-Referenz
`666 FULL LYRICS INTELLIGENCE` R06.1 repariert das CRLF-Zeilenende in `node_modules/electron/path.txt` via `File.WriteAllText`. Diese Lösung wird nicht ungeprüft kopiert; `npm install` oder ein vorhandener korrekter Electron-Start wird zunächst regulär überprüft. Keine Behauptung einer erfolgreichen Windows-Abnahme.

## Sicherheitsgrenzen
Context isolation + sandbox + Node integration AUS, IPC nur aus Main Frames, minimale Channels, Quellen nur nach Dateidialog/Scan, Zielordner nur nach Ordnerdialog. Nie `shell:true`; keine unbestätigten Überschreibungen; Originaldateien bleiben unverändert. Beim Stop sendet Electron einen kooperativen Cancel an Python. Das Verhalten bei erzwungenem Prozessende während eines Windows-FFmpeg-Laufs benötigt noch eine Host-Abnahme.
