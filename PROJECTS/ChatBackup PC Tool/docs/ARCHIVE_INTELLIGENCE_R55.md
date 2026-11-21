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
- Die Funktion ist ausschließlich lesend. Sie verändert weder Checkpoint noch SQLite-Index noch ZIP-Originale.
- Relocation ist eine **Empfehlung**, keine automatische Reparatur oder Änderung der Herkunftszuordnung.

## Direkter Aufruf

```powershell
python app/archive_source_relocation.py "C:\\ChatGPT-Exporte" "C:\\Archiv\\catalog.sqlite3.batch-checkpoint.json"
```

Mit `--flat` nur das oberste Verzeichnis durchsuchen. Standard ist rekursives Suchen.

## Abnahme

- `python -m pytest -q tests/test_archive_source_relocation.py`
- Isolierte lokale Entwickler-Regression: 10/10 PASS vor Windows-Re-Audit; plattformübergreifender Re-Audit nach Security-Fix offen.
- Vollständige Repository-Regression/Windows-Geräteabnahme und GitHub-Readback gesondert nachweisen.
- Keine Current-Pointer-Mutation vor bestandenem Gesamt-Readback.

## Nächste sinnvolle Recherchepunkte

1. Benutzerbestätigte Checkpoint-Neuzuordnung mit Pre-Change-Backup und Versionskonfliktkontrolle.
2. Große Quellenbestände: Bounded Hashing und kontrollierte Abbruchsignale.
3. Chat-Verzweigungsnavigation anhand belegter Parent-IDs.
4. Kontextbezogene Suche mit lokaler Datenschutzsteuerung.
