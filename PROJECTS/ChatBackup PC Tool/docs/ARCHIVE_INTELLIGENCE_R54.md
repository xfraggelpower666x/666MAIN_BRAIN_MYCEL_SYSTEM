# 666 CHATBACKUP · ARCHIVE INTELLIGENCE R5.4

Status: Entwicklungsbranch-Kandidat, kein unabhängiger Versionssprung der Windows-Hauptanwendung.
Scope: `PROJECTS/ChatBackup PC Tool/`. PFS und Scriptable bleiben unverändert.

## Ergänzungen

### Inkrementelle FTS5-Synchronisierung
- `app/archive_navigation.py::sync_fts` verwaltet `archive_fts_revisions` ausschließlich als ableitbaren Indexstand.
- Bei unveränderter Gesprächsrevision werden keine FTS-Zeilen ersetzt.
- Bei Änderung wird nur das betroffene Gespräch entfernt und neu indexiert; verwaiste Indexzeilen werden bereinigt.
- Ein vorhandener alter FTS-Index ohne Revisionsledger wird einmalig neu abgeglichen.
- Änderungen laufen innerhalb einer SQLite-Transaktion; bei nicht verfügbarer FTS5-Erweiterung bleibt die bisherige Suchfunktion verfügbar.
- `archive_extensions.search_fts` synchronisiert den abgeleiteten Index vor der Suche.

### Filter und Navigation
- `browse_conversations` liefert stabil sortierte, seitenweise Gespräche mit Titel, Quelle, Integritätsstatus und Nachrichtenanzahl.
- `search_filtered` unterstützt exakte Rollen-/Quellfilter sowie Zeitgrenzen und freie Textsuche; Eingaben werden per SQLite-Parametern gebunden.
- Die optionale Archivoberfläche zeigt eine eigene Treeview-Gesprächsliste, Quell- und Rollenfilter sowie „Next page“ und einen selektiven Gesprächsviewer.

### Quellenprüfung
- `audit_sources` vergleicht vorhandene Checkpoint-SHA-256 mit ZIP-Originalen.
- Ergebnisse: `VERIFIED`, `CHANGED`, `MISSING`; ein unvollständiger Bestand wird als `PARTIAL` gemeldet.
- Es erfolgt keine Mutation, Löschung oder automatische Wiederherstellung eines Originals.
- Die Prüfung benötigt Zugriff auf denselben Quellordner wie beim Batchimport. Quelle und Checkpoint bleiben lokale Benutzerdateien.

## CLI

```text
python tools/archive_intelligence_cli.py browse --limit 100 --offset 0
python tools/archive_intelligence_cli.py browse --source export.zip
python tools/archive_intelligence_cli.py search-filtered "Dark Techno" --role assistant
python tools/archive_intelligence_cli.py audit-sources "C:\ChatGPT Exporte" ".\index.sqlite3.batch-checkpoint.json"
```

## Grenzen und Abnahme
- Keine künstliche Behauptung, dass HTML-only-Exporte oder ChatGPT-Weboberfläche exakt rekonstruiert wurden.
- Die Datenbank ist weiterhin ein **lokaler, rebuildbarer** Index und keine originale Quelle.
- Für FTS5-Suche gelten die bisherigen Token-/Phrasenregeln; die neue gefilterte Suche verwendet parametrisierte literale Teilstrings.
- Echte Benutzerexporte sind hier nicht eingelesen; Tests verwenden synthetische Gesprächsobjekte.
- Die Haupt-GUI und die bisherige EXE-Spezifikation werden nicht verändert. Die optionale Archive-Intelligence-EXE erhält die Funktionen automatisch durch ihren bestehenden Buildpfad.

## Nächste sinnvolle Recherchepunkte

1. Dateimetadaten und Hashing zur Beschleunigung wiederholter Quellen-Audits, ohne Integrität zu überschätzen.
2. Komfortable Quellen-Neuzuordnung bei verschobenen ZIP-Ordnern.
3. Rollenübergreifende Pfad- und Branch-Navigation für verzweigte ChatGPT-Messages.
4. Quellenbezogene Ergebnisexporte mit verschlüsselter lokaler Ablage.
5. Windows-GUI-Accessibility, asynchrone Paginierung und Performance bei sehr großen Datenbanken.
