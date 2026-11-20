# 666 ChatBackup · Archive Intelligence R5.1 · BATCH / FTS / VIEWER

STATUS=FEATURE_BRANCH_CANDIDATE
NATIVE_OWNER=666_CHATBACKUP_PC_TOOL
SOURCE_BRANCH=feature/chatbackup-archive-intelligence-r5-20261120
PFS_MUTATION=NONE
EXISTING_GUI_AND_SCRIPTABLE_REPLACEMENT=FORBIDDEN

## Neue additive Fähigkeiten

1. **Batch ZIP-Import:** Ein Verzeichnis mit eigenen ChatGPT-Export-ZIPs wird in stabiler Reihenfolge verarbeitet. Jedes Archiv wird vollständig geprüft und transaktional in den lokalen SQLite-Katalog geschrieben. Fehlerhafte Archive bleiben aus dem Checkpoint heraus.
2. **Checkpoint / WEITER:** Eine gesonderte JSON-Datei speichert erst nach erfolgreichem Import die SHA-256-Summe jedes kompletten Archivs. Bei erneutem Start werden unveränderte abgeschlossene Archive übersprungen; geänderte ZIPs neu verarbeitet. Kein Checkpoint wird als Datenbank-Ersatz interpretiert.
3. **FTS5:** Optionaler lokaler Volltextindex, der nach Batchimport erneuert wird. Kein API-Zugriff. Die FTS5-Suche ist eine Cache-Ableitung und kann neu erzeugt werden; ohne FTS5 bleibt die gewöhnliche Suchfunktion verfügbar.
4. **Archivviewer:** Nachrichten samt Rolle, Text, Elternbeziehung, Revision und Quelle lassen sich aus dem lokalen Katalog lesen. Die Visual-Parity mit der ChatGPT-Weboberfläche wird nicht behauptet.
5. **Bedienung:** Neue CLI-Kommandos sowie zusätzliche Schaltflächen in der separaten R5-Tkinter-Oberfläche. Die produktive v1.10.5-Oberfläche wird nicht geändert.

## Befehle

Aus dem Projektordner:

```powershell
python tools/archive_intelligence_cli.py batch "C:\Meine ChatGPT Exporte"
python tools/archive_intelligence_cli.py --db ".\local.sqlite3" batch "C:\Meine ChatGPT Exporte" --checkpoint ".\progress.json"
python tools/archive_intelligence_cli.py search-fast "Dark Techno"
python tools/archive_intelligence_cli.py view "CONVERSATION_ID"
```

Windows-Doppelklick für die optionale Oberfläche: `START_ARCHIVE_INTELLIGENCE.bat`.

## Schutz- und Integritätsgrenzen

- Quellen bleiben unangetastet; der Index und der Checkpoint sind lokale abgeleitete Dateien.
- Kein automatischer Import von HTML-only-Exporten, keine Cookie-/Session-Extraktion, kein Cloud- oder API-Zwang.
- Ein unterbrochener Dateiimport kann transaktional im Katalog enden. Der Checkpoint überspringt erst nach Commit. Wird die Checkpoint-Datei entfernt, wird der Import erneut geprüft und der bestehende Katalog dedupliziert.
- Der aktuelle ZIP-Reader lädt `conversations.json` noch vollständig innerhalb des Limits in den Arbeitsspeicher. **Streaming innerhalb eines einzelnen großen ZIPs** und Fortschritt innerhalb des ZIPs sind nicht implementiert.
- Die Oberfläche bietet kein garantiertes Abbrechen mitten in der laufenden ZIP-Verarbeitung; die Checkpoint-Wiederaufnahme erfolgt auf ZIP-Grenzen.
- Bei beschädigter oder fehlender Indexdatenbank mit bereits vorhandenem Checkpoint schlägt der Import bewusst fehl.
- FTS5 unterstützt nur die Texte, die im abgeleiteten Katalog gespeichert wurden. Bei unmittelbaren fremden Schreibzugriffen auf diesen Katalog kann der Index veralten; ein Batch-Rebuild aktualisiert ihn.

## Offene Host-Nachweise

- Aktueller Branch: GitHub-Python/Node-CI ist die technische Gegenprobe.
- Echte ChatGPT-Datenexports unterschiedlicher Generationen und Windows-Doppelklick müssen noch auf dem Zielgerät geprüft werden.
- Keine neue Windows-EXE veröffentlicht. Kein produktiver Freeze.

## Nächste sinnvolle Recherchepunkte

1. Streaming/fortschrittsfähiger JSON-Parser bei sehr großen offiziellen Exporten.
2. UI-gesteuertes Abbrechen, Status pro Archiv und sichere Wiederaufnahme.
3. FTS5-Filter für Zeiträume, Rollen und Gruppenchat-Teilnehmer.
4. Speicherpfad- und Archivverschlüsselung für sensible Gesprächsdaten.
5. Weiterentwicklung des visuellen Viewers mit Assets und Branch-Navigation.
