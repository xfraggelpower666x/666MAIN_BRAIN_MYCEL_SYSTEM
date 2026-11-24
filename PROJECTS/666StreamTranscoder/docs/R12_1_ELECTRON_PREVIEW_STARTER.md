# 666StreamTranscoder R12.1 · Electron Preview Starter
Status: SOURCE CODE COMMITTED · WINDOWS ELECTRON HOST OPEN · 3DX/RESIN 3 UNCHANGED.

## Basis & Quelle
- Native Projektbasis: `PROJECTS/666StreamTranscoder/` auf Branch `666MAIN_BRAIN`.
- Referenz: `PROJECTS/666_FULL_LYRICS_INTELLIGENCE/` R06.1, besonders `electron/main.cjs`, `preload.cjs`, `package.json`, `build/BUILD_WINDOWS.ps1` und `runtime/CURRENT.json`.
- Aus R06.1 stammen **Methoden**: sichere BrowserWindow-Konfiguration, isolierter Preload, separate Python-Bridge und späterer Portable-/NSIS-Build. Kein Lyrics-Code, keine Lyrics-Daten, keine fremde Authority übernommen.

## Neue R12.1-Lieferung
- `electron-ui/START_ELECTRON_PREVIEW.cmd`: Doppelklick-Start für Windows, prüft Node/npm, bietet einmalig explizite Zustimmung zur **lokalen** Electron-Paketinstallation, führt Syntax-/Sicherheitstests aus, startet die Vorschau.
- `electron-ui/tests/security.test.cjs`: fünf Node-Bordmittel-Tests für Security-Flags, isoliertes Preload, deaktivierte Steuerung, falsche Telemetrie und Präsentationsscope.
- `electron-ui/package.json`: neue `npm test`-Aktion, Version 0.1.1.
- **Kein Python erforderlich für die isolierte Electron-Vorschau.** Python und FFmpeg bleiben für die echte Radioengine erforderlich.
- **Keine** neuen Audioadapter, Serververbindungen, Windows-Gerätetreiber oder Python-Neustarts. Die bisherige PyInstaller-/Inno-Kette bleibt erhalten.

## Windows-Anwendung testen
1. GitHub-Projekt laden, `PROJECTS/666StreamTranscoder/electron-ui` öffnen.
2. `START_ELECTRON_PREVIEW.cmd` per Doppelklick starten.
3. Node.js/npm muss vorhanden sein. Bei fehlenden lokalen node_modules entscheidet der Nutzer selbst über `npm install`.
4. Die sichtbare Oberfläche ist eine **unverbundene Vorschau**, kein produktiver Streamer. Broadcast/Skip sind deaktiviert.
5. Für den Quelltest ohne Electron: `node --test tests/*.test.cjs`.

## Weitere verbindliche Gates
- Read-only Status-IPC aus **bestehendem** Python-Engine-Prozess und akzeptiertes Event-/Statusschema.
- Validierte Befehle erst nach Runtime-/Routing-/Regressionsabnahme, kein zweiter Stream-/FFmpeg-Prozess.
- Eigenständige Windows EXE, Setup und physische Audioabnahme stehen weiter aus.
- Native 666StreamTranscoder-Authority bleibt projektgebunden, LYVRA Coding Profi koordiniert nur die fachliche Zusammenarbeit.
