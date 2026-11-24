# Integration und Abnahme

## Profil für die Entwicklung

Kopiere den ToolStarter-Kern als interne Build-Hilfe und übernimm kompatible Funktionen seiner Batch in den einzigen Projektstarter und setze `project_root` relativ zum Speicherort des Profils. Gib lokale Binärordner unter `path_dirs` an. Lege Pflichtdateien unter `required_files` fest. Definiere unter `tools` eindeutige IDs, `required` und über `after` die vorher geprüften Abhängigkeiten. Aktivierte Tools ohne `required` gelten als Pflichtwerkzeuge. Verwende `before_actions` für tatsächlich vorhandene Projektprüfungen. Definiere Start und Build unter `actions` als Befehlsarrays. Bewahre Arbeitsverzeichnis, Argumente, Ausgaben und Exitcodes.

- `exe` verwendet `names` und bei Bedarf `args`, `match` und einen belegten `repair`-Hook oder `winget`.
- `audio` prüft FFmpeg/FFprobe mit einer WAV-Gegenprobe und reicht die geprüften Pfade über `FFMPEG_PATH` und `FFPROBE_PATH` weiter.
- `npm` prüft den npm-Baum und optional exakte Versionen in `locked_packages`. Dieser Adapter setzt ein npm-Lockfile voraus. Für pnpm/Yarn den im Projekt belegten Manager und dessen eigene Probe beziehungsweise Reparatur verwenden.
- `electron` verwendet die Lockfile-Version. Optionale `check`- und `repair`-Hooks kommen aus dem Zielprojekt.
- `STARTEN.bat diagnose --profile mein-projekt.json` protokolliert die Diagnose. `repair` repariert fehlerhafte deklarierte Einträge. `run <aktion>` versucht standardmäßig die Selbstheilung für Pflichtwerkzeuge. Bei `self_heal_on_run: false` sind Prüfung und Reparatur getrennte Schritte. Die Logdateien liegen unter `<Projektordner>\logs\`.

## Auslieferung

Nutze einen vorhandenen Windows-Anwendungsbuild als Eingabe. Erfasse unter `required_runtime_ids` jede zur Laufzeit erforderliche, mitzuliefernde Komponente. Jede entsprechende Zeile unter `runtime` braucht `files`, `licenses` und ausführbare `probes`. Erfasse transitive Dateien wie DLLs, Plugins und Daten im Kopierplan unter `include`. Die Start-EXE wird unter `entry` eingetragen. Die Zielanwendung muss ihre Hilfsprogramme aus der Installation oder dem entpackten Ordner auflösen. Bei Electron kann sie dazu `process.resourcesPath` verwenden.

Bei einem Electron-Paket setze `electron_package` und verwende in der Probe `{electron_version}` als Platzhalter im Regex für die tatsächliche Version der gepackten App. Für den FFmpeg-Funktionstest verwende Pflicht-ID `ffmpeg` und konfiguriere `runtime_environment` mit `FFMPEG_PATH` und `FFPROBE_PATH`.

Baue mit `STARTEN.bat package both --profile release.json` beide Ausgaben aus derselben Nutzlast. Für Setup benötigt der Windows-Build-Host Inno Setup. Prüfe Inhalt und SHA-256-Manifest, starte Portable und Setup auf einer sauberen, unterstützten Windows-Zielumgebung ohne projektbezogene PATH-Einträge und führe jede geforderte Funktion aus. `STARTEN.bat --diagnose` im ausgelieferten Paket prüft Dateiintegrität. Betriebssystemfunktionen und nicht redistribuierbare Komponenten werden als Zielvoraussetzungen ausgewiesen. Führe Lizenzpflichten je konkretem verteiltem Build auf.

## Übergabe

Gib Projektwurzel, ausgewählte Karten mit Belegen, Rollen, Versionen, Start- und Reparaturbefehle, Logpfad, Artefakte sowie den Abnahmestatus an. Unterscheide ausgeführte Host-Prüfungen, statische Prüfung und offene Laufzeitabnahme. Gib für eine unterbrochene Aufgabe den letzten bestätigten Schritt und den nächsten konkreten Aufruf an. Filtere Geheimnisse aus der Übergabe.

## Direktstart ohne ausgelieferte Build-Batch

Setze im Paketprofil `"launch_mode": "direct"` innerhalb von `package`, falls die EXE ihre Ressourcen und Runtime selbstständig auflöst. Die Daten für gebündelte Proben bleiben im Profil. Verlege zum Start benötigte Argumente oder Umgebungslogik in die Anwendung oder wähle einen geeigneten nativen Packager. ToolStarter lehnt `entry_args` im Direktmodus ab. Das Portable-ZIP enthält den direkten EXE-Einstieg und sein Hash-Manifest. Das Setup legt eine Verknüpfung zur gleichen EXE an. Das Standardverhalten bestehender Profile ist `"launch_mode": "batch"`.

Die zentrale Entwicklungs-Batch ruft `toolstarter.py package portable` für `--package` und `toolstarter.py package setup` für `--setup` mit dem belegten Releaseprofil auf. Ein sachgerechter vorhandener Packager ist ebenfalls zulässig. Jede Aktion verarbeitet das geprüfte Release-Artefakt des ausgewählten Projekts und gibt Fehler bis zum Aufrufer zurück.

## Differentialprüfung eines gelieferten ToolStarter-Bundles

Ordne die acht Kern- und Profildateien eines ToolStarter-Uploads dem vorhandenen Starter unter `assets/toolstarter/` zu. Vergleiche Bytes und bei Textdateien zusätzlich die Unterschiede nach Normalisierung der Zeilenenden. Prüfe bei abweichendem Code zuerst, welche Funktionen im Projekt oder Plugin aktueller sind. Ein älteres Beispielprofil darf einen belegten Batch- oder Direct-Modus nicht still ersetzen.

Für eine beauftragte Aktualisierung prüfe Pflichtdateien, Diagnose und Fehlerweitergabe über die einzige Entwicklungs-Batch. Bei beauftragten Portable- oder Setup-Paketen prüfe die reale Ziel-EXE, die beiden unterstützten Starter-Modi und die aufs jeweilige Paket bezogenen Laufzeitproben. Die Prüfung eines Profils unter Linux liefert keinen Windows-Startnachweis.

## Veröffentlichung und Abbruch

Pro Ausgabestamm serialisiert ToolStarter die Publikation. Das externe Manifest wird nach den Artefakten ersetzt. Verwende es nur nach Hash- und Größenabgleich aller darin genannten Ausgaben. Als lokaler Prüfeinstieg steht im Modul `packaging_tools.py` die Funktion `verify_publication(receipt_path)` zur Verfügung.

Nach einem Abbruch kann der vorherige Beleg mit den Dateien nicht mehr übereinstimmen. Stelle den Satz per gemeinsamem Build wieder her. Bleibt die Veröffentlichungssperre nach einem Prozessabbruch liegen, prüfe, dass kein Build mehr schreibt, bevor du den leeren Sperrordner entfernst. Vorher vorhandene Einzelarchive werden als Geschwisterdatei nur übernommen, wenn der bisherige Fingerabdruck und ihr eigener Hash zur Nutzlast passen.

Die [Regressionstests](../tests/test_packaging_publication.py) sind mit `python -m unittest discover -s tests -v` aus dem Skill-Ordner ausführbar. Compiler und Runtime-Probe im Test sind Fixtures. Windows-Start und Installer werden im Zielhost abgenommen.
