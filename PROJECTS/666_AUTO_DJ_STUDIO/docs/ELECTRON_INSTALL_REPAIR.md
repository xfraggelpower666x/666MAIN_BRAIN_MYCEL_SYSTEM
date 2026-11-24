# AUTO-DJ STUDIO — Electron-Installationsreparatur (2026-11-23)

## Belegter Fehler

Windows Option 3: npm meldet 384 installierte Pakete, aber `allowScripts`
überspringt `electron@35.7.5` postinstall. `npm start` scheitert in
`node_modules/electron/index.js` mit `Electron failed to install correctly`.
Das ist kein Fehler des AutoDJ Audio-Workers und keine FFmpeg-Störung.

## Minimalinvasive Korrektur

Nur `build/BUILD.ps1` geändert. Die bestehende BUILD.bat, Original-GUI,
Python-Engine, Electron-Oberfläche, FFmpeg, Covers und Assets bleiben
unverändert.

- Der Electron-Runtime-Check lädt `require('electron')` und prüft den realen
  ausführbaren Dateipfad.
- Fehlt die Electron-Laufzeit, wird ausschließlich das bereits installierte
  Skript `node_modules/electron/install.js` ausgeführt. Das kann den
  Electron-Binärdownload auslösen und benötigt gegebenenfalls Internet.
- Danach erfolgt erneut die Laufzeitprüfung; ohne erfolgreiches Ergebnis
  bricht das Skript mit klarer Fehlermeldung ab.
- Bei vorhandenem `node_modules` vermeidet Option 3 eine unnötige
  Neuinstallation sämtlicher npm-Pakete.
- PyInstaller wird für Option 3 nicht erneut installiert; es bleibt Teil
  der Packaging-Aktionen.

## Doppelklick

ZIP in einen frischen Projektordner entpacken (oder nur die korrigierte
`build/BUILD.ps1` in den vorhandenen Ordner übernehmen). Danach
`BUILD.bat` → `3`. Keine anderen Dateien entfernen.

## Abnahme

Quelländerung und ZIP-CRC geprüft. PowerShell und Electron-Ausführung auf
Windows wurden hier nicht ausgeführt; Host-Abnahme bleibt offen.
