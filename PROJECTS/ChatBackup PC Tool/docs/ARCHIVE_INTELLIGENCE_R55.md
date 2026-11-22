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

## Nachrichtennavigation (additive R5.5-Erweiterung)

- Der neue Reiter **Search navigation** zeigt die bisherigen Textsuche-Ergebnisse als anklickbare Treffer mit Titel, Rolle, Herkunft und Vorschau. Der alte rohe JSON-Ergebnisreiter bleibt vorhanden.
- Doppelklick oder **Open selected message** liest die vollständige Nachricht mittels `conversation_id` und `message_id` aus dem bestehenden SQLite-Katalog; keine Rekonstruktion aus abgeschnittenen Snippets.
- Der Viewer zeigt die markierte Originalnachricht samt maximal zwei chronologisch benachbarten Nachrichten je Seite, Parent-ID, Vor/Zurück-Tasten sowie hervorgehobenen wörtlichen Treffern.
- Die Navigation beruht auf der durch `conversation_view` gespeicherten Nachrichtenfolge. Parent-IDs sind nur Belegkontext; verzweigte Chatpfade werden nicht als unbestätigte lineare Unterhaltung ausgegeben.
- Reine Offline-Leseoperationen auf dem lokalen Katalog. Keine Mutation von ChatGPT-Original-ZIPs, Checkpoints, Exportdateien oder fremden nativen Projekten.
- Tests in `tests/test_archive_message_navigation.py` prüfen exakte IDs, Trefferpositionen, Kontextgrenzen, wörtliche Hervorhebung und SQLite-Suchergebnis-zu-Volltext-Readback.
- Der kompilierte Windows-EXE-Host und die tatsächliche visuelle Tkinter-Bedienung müssen separat auf einem echten Desktop geprüft werden; CI kann dies nicht ersetzen.

## Parent-/Child-Zweignavigation

- Im bestehenden Volltext-Viewer stehen jetzt **Parent**, **Go to child** (direkte Kinder) und **Switch branch** (Geschwisterantworten) bereit; die bisherige chronologische Vor-/Zurück-Navigation bleibt erhalten.
- Die Beziehungen stammen ausschließlich aus den im SQLite-Katalog bereits vorhandenen `message_id` / `parent_id`. Die grafische Auswahl verwendet die exakt gespeicherten IDs, niemals Treffer-Snippets oder Textähnlichkeiten.
- Mehrere direkte Kinder werden einzeln auswählbar; echte alternative Antworten werden als Geschwisterzweige gezeigt.
- Fehlende Eltern-IDs, Selbstreferenzen und zyklische Parent-Ketten werden als Warnungen behandelt. Keine künstliche Kante, keine automatische Zusammenführung von Zweigen.
- Parent-IDs außerhalb des indexierten Nachrichtenbestands können aus strukturell nicht indexierten Export-Knoten stammen; diese sind offen statt als gelöschte Nachrichten behauptet.
- GUI-Readback im echten Windows-Tkinter-Host bleibt getrennt von CI-Codeabnahme.

## Interaktive Baumansicht (additive R5.5-Erweiterung)

- **Explore branch tree** im bestehenden Conversation Viewer öffnet ein eigenständiges Tkinter-Fenster mit den indexierten Parent-/Child-Beziehungen und deren tatsächlichen `message_id`-Werten.
- **Aufklappbare Knoten:** direkte Antworten werden bei Bedarf geladen, jeweils in Seiten von 120 Nachrichten. Damit erzeugen große Unterzweige nicht sofort Tausende UI-Zeilen.
- **Doppelklick oder Jump to selected message** öffnet die gewählte Nachricht im bereits vorhandenen Volltext-Viewer. **Show original selected message** bringt den Ausgangstreffer im Baum wieder in Sicht.
- **Diagnose:** nicht auflösbare Eltern werden als eigene diagnostische Wurzeln dargestellt; zyklische Beziehungen werden im Sichtbaum gekappt und mit `CYCLE_EDGE_OMITTED_FROM_TREE` gekennzeichnet, ohne die Quelle zu verändern.
- **Determinismus:** jede gespeicherte Nachricht erscheint genau einmal; Reihenfolge entspricht der bestehenden lokalen Index-Reihenfolge. Weder Lücken noch Zweige werden durch Textähnlichkeit erraten.
- **Performance:** einmaliger linearer Zyklus-Scan in `archive_message_navigation.branch_index`; iterative Abstammung, rekursionsfreies UI-Laden, begrenzte Nachrichtenvorschau.
- **Tests:** `tests/test_archive_branch_tree.py` prüft exakte Wege, Mehrfachzweige, fehlerhafte Parent-IDs, Zyklen, 2.500 Nachrichtenknoten und den GUI-Import ohne Bildschirm.
- **Abnahmegrenze:** CI prüft Modul-/Importverträge und Datenbeziehungen; die visuelle Bedienung der kompilierten Windows-EXE bleibt gesondert `READBACK_PENDING`.

## Native Python-Suche im Gesprächsbaum (R5.5 Weiterentwicklung)

- Im tatsächlichen `tools/archive_branch_tree_ui.py` existiert nun ein Eingabefeld für **Message-ID oder Text**, mit **Search tree** und Ergebnisliste.
- Der Suchkern `app/archive_branch_tree.search_branch_tree` durchsucht die aus `ArchiveCatalog` via `conversation_view` geladenen, real indexierten Nachrichten; Ergebnis enthält **exakte Message-ID**, Original-Index, Rolle, Auszug und den aus der Parent-Registry aufgelösten Pfad.
- Doppelklick in der Suchliste oder **Open selected tree-search result** klappt den zugehörigen Pfad im Baum auf und springt im bestehenden Textviewer zur gefundenen Nachricht.
- Die Suche hat eine harte Ausgabegrenze (standardmäßig maximal 200 Treffer; Core unterstützt Offset/Limit). Sie erfindet keine Beziehungen und schreibt weder Exportdateien noch Datenbankinhalte.
- Tests: `tests/test_archive_branch_tree.py` prüft Suche nach Text/ID, reale Pfadauflösung, Pagination, Eingabegrenzen, Read-only-Verhalten und UI-Verkabelung.
- Suchtreffer über 200 werden über die **Vorherige/Nächste-Seite-Steuerung** der echten Tkinter-Baumoberfläche erreicht. Die UI nutzt dabei die Core-Parameter `limit` und `offset` ohne erneuten ZIP-Import.
- Nur Code-/CI-Tests gelten als verifiziert; realer Tkinter-/Windows-EXE-Bedientest bleibt getrennt offen.

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
