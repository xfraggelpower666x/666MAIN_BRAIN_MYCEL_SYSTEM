# FULL LYRICS INTELLIGENCE R06 — Windows

1. ZIP vollständig entpacken.
2. `STARTEN.bat` doppelklicken.
3. Option `1` zum Starten.
4. Falls Electron noch nicht installiert ist: npm-Installation bestätigen und anschließend gezielte **offizielle GitHub-Runtime-Reparatur** bestätigen.

## Was anders ist

- Nur **eine** Batch als Einstieg.
- Wenn npm `electron@35.7.5` wegen `allow-scripts` nicht vollständig installiert: offizielles Electron-Windows-x64-Archiv direkt aus `github.com/electron/electron/releases` laden, anhand `SHASUMS256.txt` prüfen, in das bestehende npm-Electron-Paket einsetzen und `path.txt` korrigieren. Nur nach deiner Zustimmung.
- Python-Bridge-Absturz durch fehlende Timeout-Variablen behoben.
- Datenbankbrowser: mehrere Datensätze auswählen, Projekt/Kategorie in einem Schritt korrigieren, ZIP exportieren oder nach Bestätigung archivieren.
- R02-Original bleibt im Sicherungs-ZIP und wird nie automatisch verändert.
- Keine komplette npm-Neuinstallation wenn Paket bereits vorhanden. Keine automatischen Node-/Python-Upgrades.

**Hinweis:** Diese Lieferung ist ein Windows-Quellpaket. Die tatsächliche Electron-Ausführung auf deinem Windows-PC wurde hier nicht beobachtet. Der Starter benötigt beim ersten Runtime-Download Internetzugang zu GitHub Releases.


## R06.1 Electron ENOENT-Pfad-Reparatur

Der R06-Installer hat `node_modules/electron/path.txt` mit PowerShell `Set-Content` geschrieben.
Das haengt `\r\n` an `electron.exe` an. Electron/Node liest diese Datei unveraendert
und versucht dann, `electron.exe\r\n` zu starten (ENOENT).

**R06.1 schreibt `path.txt` jetzt mit .NET `File.WriteAllText` ohne Zeilenende.**
Der zentrale Launcher repariert auch ein bereits vorhandenes fehlerhaftes `path.txt`
automatisch, wenn die originale, SHA-256-gepruefte Electron-Runtime schon vorhanden ist.
Kein neuer Electron-Download und keine npm-Neuinstallation sind in diesem Fall noetig.

Start: ZIP komplett entpacken, `STARTEN.bat` starten, Option `1`.
Node/Python und das R02-Original werden nicht zurueckgesetzt.
Windows-Start muss auf dem Zielrechner bestaetigt werden.
