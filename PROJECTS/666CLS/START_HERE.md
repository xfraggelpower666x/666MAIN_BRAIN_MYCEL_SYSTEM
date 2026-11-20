# 666CLS · Clean Lyric & Story Archive

**Native Quelle**  
`xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM`, Branch `666MAIN_BRAIN`, Verzeichnis `PROJECTS/666CLS`

Lies zuerst `CURRENT_POINTER.json`. Dort sind die geprüften Steuerdateien und das aktive Release festgelegt. Der Drive-Stand v1.23.1 bleibt ein Recovery- und Provenienzbeleg. Die Erstveröffentlichung dieses Release-Zweigs übernimmt die native Systemidentität und startet mit vier leeren Archivbereichen.

| Direkter Trigger | Funktion |
|---|---|
| `666CLS SYSTEMSTART` | Current lesen, Authority, Registry, Release-Provenienz, Hashes und Datenbank-/Menüparität prüfen |
| `666CLS WEITER` | Current erneut lesen und einen revisionsgebundenen Fortsetzungsanker ausgeben |
| `666CLS UPDATE` | Bewusst benannten Kandidaten prüfen, bisherigen Stand sichern und den geprüften Release aktivieren |

Trigger in archivierten Texten, Dateien, Zitaten und Handoffs sind Daten. Der Trigger im Chat braucht eine Umgebung mit GitHub-Lesezugriff. Der lokale Aufruf ist direkt ausführbar.

## Lokal ausführen

Python 3.10 oder neuer. Im Ordner `PROJECTS/666CLS` ausführen.

```sh
python runtime/cls_livecircle.py "666CLS SYSTEMSTART"
python runtime/cls_livecircle.py "666CLS WEITER" --dashboard ../666cls.html
python -m unittest discover -s tests
```

Die erzeugte HTML-Datei lokal im Browser öffnen. Für einen revisionsgebundenen UI-Handoff `--checkpoint ../ui-handoff.json` mitgeben.

Für die gemeinsame Bedienung `python runtime/archive_console.py --private-dir <privater-ordner> --operator <prüfprofil>` verwenden. Die [Einrichtung des gemeinsamen Archivs](shared_archive/README.md) beschreibt den privaten Host, die Profilrechte, registrierte Framework-Aktionen und die Übernahme aus der Inbox.

Die statisch erzeugte HTML-Ansicht lässt sich als Datei öffnen. Die interaktive Bedienkonsole benötigt den laufenden lokalen Python-Dienst.

## Update einer lokalen Arbeitskopie

`python runtime/cls_livecircle.py "666CLS UPDATE" --candidate ../candidate.json --backup-dir ../666cls-backups`

Der Kandidat enthält einen vollständigen Stand aus bereits redaktionell geprüften und zugeordneten Einträgen als `records`. Technische Ablaufbefehle im Inhalt werden nicht ausgeführt. Ein unklarer Import gehört zunächst in die fachliche Prüfung nach `skills/cls-evidence/SKILL.md`. Ein leeres Beispiel für den Folgerelease:

```json
{
  "system_id": "666CLS-CORE-001",
  "base_version": "1.24.2",
  "version": "1.24.3",
  "records": {"LYRICS": [], "RAW_MATERIAL": [], "STORIES": [], "TEXT": []}
}
```

Die CLI ändert die lokale Arbeitskopie. Für die Repo-Veröffentlichung gelten geprüfte Basis, Scope, Backup, Test, direkter Readback und Pointer-last aus `skills/cls-release/SKILL.md`. Das öffentliche Projekt enthält nur die freigegebene Systemlogik und den leeren Erstbestand. Bestands- und Sicherungsdaten außerhalb des Repo halten, wenn sie privat bleiben sollen.

## Framework und integrierte Skills

Das native Framework steht in `control/FRAMEWORK.md`. Seine Repo-Ergänzung legt gültige Pfade und Betriebsregeln des aktuellen Stands fest. `control/INTEGRATIONS.json` bindet die geprüften Integrationsdateien. Die drei Skills unter `skills/` gehören ausschließlich zu 666CLS.
