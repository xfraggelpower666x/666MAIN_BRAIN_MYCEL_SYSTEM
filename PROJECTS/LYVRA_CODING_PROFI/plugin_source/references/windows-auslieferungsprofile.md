# Windows-Auslieferungsprofile

Erzeuge die ausdrücklich beauftragten Windows-Auslieferungsartefakte. Bei einer vollständigen Windows-Paketlieferung baue Portable-ZIP und Offline-Installer getrennt aus demselben geprüften Quellstand je unterstützter Zielarchitektur. Verwende bestehende Packager- und Installer-Konfigurationen. Wenn ein Profil fehlt, ergänze es passend zum Zielprojekt. Die Entwicklungs-ZIP macht die passenden Build- und Prüfaktionen im dokumentierten Einstieg zugänglich. Nutze bei ToolStarter das [Paketprofil](../skills/toolstarter-coding/references/integration.md#auslieferung). Der Build erzeugt die Setup-Datei. Die Installation erfolgt als eigener Test.

## Gemeinsame Laufzeitdateien

Leite die benötigten Bestandteile aus tatsächlichem Startpfad, Konfiguration, Paketmanifest, Tool-Aufrufen und Tests ab. Inventarisiere Programmdateien, Python- oder andere Runtime-Bestandteile, Bibliotheken, Modelle, DLLs und tatsächlich verwendete Zusatzprogramme. Erfasse pro Bestandteil Version, Architektur, Bezugsquelle, Paketpfad und erlaubte Weitergabe. Lege nötige Lizenz- und Herkunftshinweise bei. Verwende dieselben geprüften Laufzeitdateien als Basis für beide Profile. Build-Werkzeuge verbleiben in der Entwicklungsumgebung, sofern sie zur Laufzeit nicht benötigt werden. Ist eine notwendige Komponente nicht beschaffbar oder nicht zur Weitergabe freigegeben, nenne sie und kennzeichne das betroffene Paket als unvollständig. Ein dokumentierter Mindeststand von Windows oder ein Gerätetreiber gehört in die Voraussetzungen.

## Portable-ZIP

Packe die vollständige Programmverzeichnisstruktur und alle weitergabefähigen Laufzeitdateien in ein versioniertes Portable-ZIP. Bei Ordner-Builds bleibt der komplette Ausgabeordner erhalten. Ein vorhandener Portable-Launcher verwendet auf das entpackte Paket bezogene Pfade und bevorzugt seine eigenen Zusatztools. Bei zentraler Entwicklungs-Batch startet die entpackte Anwendungs-EXE direkt. Beide Auslieferungsarten arbeiten aus ihrer eigenen Nutzlast. Richte Anwendungseinstellungen und Schreibpfade passend zum vorhandenen Portable-Modus ein. Prüfe auf einem unterstützten sauberen Windows ohne vorinstallierte Projekttools und bei getrennter Netzwerkverbindung. Teste Start und einen fachlichen Ablauf pro benötigtem Zusatztool. Teste einen entpackten Ordner auf einem Wechseldatenträger oder einen gleichwertigen verschobenen Pfad mit anderer Laufwerkskennung und Leerzeichen. Benenne, welche dieser Bedingungen tatsächlich geprüft wurden.

## Offline-Windows-Installer

Packe die Anwendung, ihre Laufzeitdateien und benötigten Zusatztools in die Setup-Datei oder den vollständigen gemeinsam ausgelieferten Offline-Setup-Ordner. Installiere app-lokale Werkzeuge in den Projektinstallationspfad. Verwende erforderliche weitergabefähige System-Runtimes aus dem enthaltenen Setup-Payload und beachte ihren dokumentierten Installationsumfang. Der normale Installationsweg darf keine Komponenten aus dem Netz nachladen. Verwende einen geeigneten Installationsumfang pro Nutzer oder pro Computer nach Projektbedarf und gib notwendige Rechte an. Prüfe Installationspfade, Programmeinstieg, fachliche Zusatztool-Aufrufe, Update über einen bestehenden Stand und Deinstallation auf einem unterstützten Windows. Erhalte Nutzerdaten beim Update und beim üblichen Deinstallationsablauf, soweit der bestehende Projektvertrag nichts anderes vorsieht.

## Getrennte Nachweise

Lies Inhalt und Version der beauftragten Artefakte zurück. Weise je Profil Build, Vollständigkeit der Laufzeitdateien, Offline-Start und Zusatztool-Funktion aus. Beim Installer kommen Installation und Deinstallation hinzu. Bei fehlendem Windows-Host bleibt die Laufzeitabnahme offen. Die Zieltool-Sprachauswahl bleibt English / Deutsch mit Englisch als Standard. Alle eigenen Batch-Ausgaben sind Englisch.

## Electron mit gebündelten Medientools

Bei einem [Electron-Projekt](../skills/sceeri-electron/SKILL.md) mit [FFmpeg und FFprobe](../skills/sceeri-ffmpeg/SKILL.md) prüfe den tatsächlichen Packager-Ausgabeordner. Beide Windows-Profile enthalten die passende Electron-Runtime und die benötigten FFmpeg-/FFprobe-Dateien. Führe auf einem geeigneten sauberen Windows ohne Medienwerkzeuge im PATH mindestens einen Probe-Aufruf und eine repräsentative Verarbeitung aus. Weise Artefaktpfad, Toolversion, getesteten Codec und geprüfte Ausgabe je Profil aus. Ein Test in der Entwicklungsumgebung belegt nur diesen Pfad.

## Ein Entwicklungsstarter

Erstelle für eine neue Windows-Anwendung oder die beauftragte Konsolidierung genau eine sichtbare `STARTEN.bat` im Entwicklungsprojekt. Doppelklick zeigt das englische Menü. Direkte Schalter starten dieselben Aktionen ohne Menü oder Pause. Binde vorhandene Aufrufer und gültige Argumente ein. Übernimm aus der Referenz die Aufgaben, Arbeitsverzeichnisbindung und Rückgabecodes. Leite Architektur, Namen, Werkzeuge, Pfade und Testaufrufe aus dem Projekt ab.

| Schalter | Aktion |
| --- | --- |
| `--start` | Die gebaute Windows-App starten |
| `--browser` | Vorhandenen Browserpfad starten, falls fachlich unterstützt |
| `--diagnose` | Voraussetzung oder Paket lesend prüfen |
| `--repair` | Deklarierten Fehler gezielt reparieren und erneut prüfen |
| `--build` | Windows-Release für die unterstützte Zielarchitektur erzeugen |
| `--test` | Relevante Projektprüfungen ausführen |
| `--package` | Portables ZIP aus der geprüften Nutzlast bauen |
| `--toolstarter` | Belegte Entwicklungswerkzeuge und Projektprofil prüfen |
| `--setup` | Ausführbare Windows-Setup-EXE aus der geprüften Nutzlast bauen |
| `--help` | Belegte Schalter und Nutzung anzeigen |

Das Menü bietet nur projektbezogen nutzbare Aktionen an. Für die beauftragte Windows-App sind Build, Tests und ausführbares Setup konkrete Lieferpfade. Diagnose ist lesend. Die Aktion Setup kompiliert und prüft die Setup-EXE. Installation und Deinstallation erfolgen in der Windows-Abnahme.

Nutze vorhandene Packager oder `package.launch_mode: "direct"` im [ToolStarter-Paketprofil](../skills/toolstarter-coding/references/integration.md#direktstart-ohne-ausgelieferte-build-batch). ToolStarter, Buildprofile und die Entwicklungs-Batch gehören in die Entwicklungsquellen. Portable und Installer erhalten die tatsächlich benötigte App-Nutzlast. Der installierte Shortcut zeigt auf die App-EXE. Für vorhandene Releaseprofile außerhalb der beauftragten Konsolidierung bleiben Aufrufe und Verpackungsverhalten erhalten.
