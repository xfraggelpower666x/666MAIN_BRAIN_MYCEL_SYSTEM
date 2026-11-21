# 666 CHATBACKUP · ARCHIVE INTELLIGENCE R5.5 (Source Relocation)

Status: Entwicklungsbranch; keine Änderung am produktiven Current Pointer oder PC v1.10.5.
Scope: `PROJECTS/ChatBackup PC Tool/`. Archive Intelligence R5.4, Windows-Hauptanwendung, Scriptable, PFS und Originaldaten bleiben unverändert.

## Neu: Vorschläge zum Wiederfinden verschobener ZIP-Archive

- `app/archive_source_relocation.py::propose_relocations` untersucht eine bestehende Batch-Checkpoint-Datei und einen gewählten Quellordner.
- Ausschließlich lokale ZIP-Dateien werden anhand SHA-256 mit den Checkpoint-Hashes abgeglichen.
- `VERIFIED`: der ursprünglich angegebene Pfad hat korrekten Hash.
- `CHANGED`: der ursprüngliche Pfad existiert mit abweichendem Inhalt; keine automatische Umdeutung.
- `RELOCATED_CANDIDATE`: ursprünglicher Pfad fehlt, exakt ein anderer ZIP-Pfad hat denselben SHA-256.
- `AMBIGUOUS`: mehrere Kandidaten mit identischem Hash; manuelle Prüfung erforderlich.
- `MISSING`: kein passender Kandidat gefunden.
- Symlinks werden übersprungen; absolut beginnende und laufwerksbezogene Checkpoint-Pfade werden plattformunabhängig zurückgewiesen, Suchmenge ist auf 10.000 ZIPs begrenzt.
- R55-01: Iterativer, nicht-symlinkfolgender Verzeichnisscan mit Limit von 100.000 Einträgen (einschließlich Nicht-ZIPs); weiterhin höchstens 10.000 ZIP-Kandidaten.
- R55-02: Checkpoint-Eingabe auf 1 MiB begrenzt; beschädigtes JSON bzw. UTF-8 wird kontrolliert abgelehnt.
- R55-03: Zusätzliche Negativ- und Regressionstests für rekursive/flat Suche, Symlink-Verzeichnisse, Scan- und Byte-Limits, ungültige Hashwerte und JSON.
- Die Funktion ist ausschließlich lesend. Sie verändert weder Checkpoint noch SQLite-Index noch ZIP-Originale.
- Relocation ist eine **Empfehlung**, keine automatische Reparatur oder Änderung der Herkunftszuordnung.

## Bedienbare R5.5-Erweiterung

- In der bestehenden optionalen Archive-Intelligence-Oberfläche steht jetzt **Find moved ZIPs** bereit.
- Der neue Reiter **Source relocation** zeigt Original-Quellpfad, SHA-256-Prüfstatus und gefundene Kandidaten.
- Die bestehende Archive-Intelligence-CLI stellt zusätzlich `relocate-sources` bereit, mit optionalem `--flat`.
- Alles bleibt offline und lesend; keine Änderung von ZIPs, Checkpoint, Datenbank oder Hauptanwendung.

## Direkter Aufruf

```powershell
python app/archive_source_relocation.py "C:\\ChatGPT-Exporte" "C:\\Archiv\\catalog.sqlite3.batch-checkpoint.json"
```

Die direkte Modul-Funktion und `python tools/archive_intelligence_cli.py relocate-sources "C:\\ChatGPT-Exporte" "C:\\Archiv\\catalog.sqlite3.batch-checkpoint.json"` stehen beide zur Verfügung.

Mit `--flat` nur das oberste Verzeichnis durchsuchen. Standard ist rekursives Suchen.

## Abnahme

- Neue Bedienregressionen: `tests/test_archive_relocation_entrypoints.py` (CLI-End-to-End, Fehlerpfad, Flat-Modus, GUI-Import ohne Display). GitHub-CI-Readback für diesen Erweiterungs-HEAD erforderlich.

- Nach Härtung R55-01 bis R55-03: GitHub-CI-Re-Audit für den finalen Branch-HEAD erforderlich. Die unten genannten PASS-Werte stammen aus der vorherigen Revision und gelten nicht automatisch für den neuen HEAD.

- `python -m pytest -q tests/test_archive_source_relocation.py`
- GitHub-Actions-Regression: 11/11 PASS unter Linux und Windows im GitHub-Actions-Run #16 (ID 44850128628); vollständige Python-Regression 126/126 je Plattform; Basistests 16/16 je Plattform; Release Integrity PASS; Scriptable-Simulation Linux 6/6 + Security 11/11 PASS.
- GitHub-Actions-CI und SHA-geprüfte Branch-Dateien sind separat von echter Geräteabnahme zu bewerten. Realer Windows-PC-/iPhone-Host-Readback bleibt offen.
- GitHub-CI-Run: https://github.com/xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM/actions/runs/44850128628
- Keine Current-Pointer-Mutation vor bestandenem Gesamt-Readback.

## Nächste sinnvolle Recherchepunkte

1. Benutzerbestätigte Checkpoint-Neuzuordnung mit Pre-Change-Backup und Versionskonfliktkontrolle.
2. Große Quellenbestände: Bounded Hashing und kontrollierte Abbruchsignale.
3. Chat-Verzweigungsnavigation anhand belegter Parent-IDs.
4. Kontextbezogene Suche mit lokaler Datenschutzsteuerung.
