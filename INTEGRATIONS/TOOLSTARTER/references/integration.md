# Integration und Abnahme

## Profil für die Entwicklung

Kopiere den ToolStarter-Kern mit seiner Batch und setze `project_root` relativ zum Speicherort des Profils. Gib lokale Binärordner unter `path_dirs` an. Lege Pflichtdateien unter `required_files` fest. Definiere unter `tools` eindeutige IDs, `required` und über `after` die vorher geprüften Abhängigkeiten. Aktivierte Tools ohne `required` gelten als Pflichtwerkzeuge. Verwende `before_actions` für tatsächlich vorhandene Projektprüfungen. Definiere Start und Build unter `actions` als Befehlsarrays. Bewahre Arbeitsverzeichnis, Argumente, Ausgaben und Exitcodes.

- `exe` verwendet `names` und bei Bedarf `args`, `match` und einen belegten `repair`-Hook oder `winget`.
- `audio` prüft FFmpeg/FFprobe mit einer WAV-Gegenprobe und reicht die geprüften Pfade über `FFMPEG_PATH` und `FFPROBE_PATH` weiter.
- `npm` prüft den npm-Baum und optional exakte Versionen in `locked_packages`. Dieser Adapter setzt ein npm-Lockfile voraus. Für pnpm/Yarn den im Projekt belegten Manager und dessen eigene Probe beziehungsweise Reparatur verwenden.
- `electron` verwendet die Lockfile-Version. Optionale `check`- und `repair`-Hooks kommen aus dem Zielprojekt.
- `STARTEN.bat diagnose --profile mein-projekt.json` protokolliert die Diagnose. `repair` repariert fehlerhafte deklarierte Einträge. `run <aktion>` versucht standardmäßig die Selbstheilung für Pflichtwerkzeuge. Bei `self_heal_on_run: false` sind Prüfung und Reparatur getrennte Schritte. Die Logdateien liegen unter `%LOCALAPPDATA%\666SOUNDsDESIGn\ToolStarter\logs`.

## Auslieferung

Nutze einen vorhandenen Windows-Anwendungsbuild als Eingabe. Erfasse unter `required_runtime_ids` jede zur Laufzeit erforderliche, mitzuliefernde Komponente. Jede entsprechende Zeile unter `runtime` braucht `files`, `licenses` und ausführbare `probes`. Erfasse transitive Dateien wie DLLs, Plugins und Daten im Kopierplan unter `include`. Die Start-EXE wird unter `entry` eingetragen. Die Zielanwendung muss ihre Hilfsprogramme aus der Installation oder dem entpackten Ordner auflösen. Bei Electron kann sie dazu `process.resourcesPath` verwenden.

Bei einem Electron-Paket setze `electron_package` und verwende in der Probe `{electron_version}` als Platzhalter im Regex für die tatsächliche Version der gepackten App. Für den FFmpeg-Funktionstest verwende Pflicht-ID `ffmpeg` und konfiguriere `runtime_environment` mit `FFMPEG_PATH` und `FFPROBE_PATH`.

Baue mit `STARTEN.bat package both --profile release.json` beide Ausgaben aus derselben Nutzlast. Für Setup benötigt der Windows-Build-Host Inno Setup. Prüfe Inhalt und SHA-256-Manifest, starte Portable und Setup auf einer sauberen, unterstützten Windows-Zielumgebung ohne projektbezogene PATH-Einträge und führe jede geforderte Funktion aus. `STARTEN.bat --diagnose` im ausgelieferten Paket prüft Dateiintegrität. Betriebssystemfunktionen und nicht redistribuierbare Komponenten werden als Zielvoraussetzungen ausgewiesen. Führe Lizenzpflichten je konkretem verteiltem Build auf.

## Übergabe

Gib Projektwurzel, ausgewählte Karten mit Belegen, Rollen, Versionen, Start- und Reparaturbefehle, Logpfad, Artefakte sowie den Abnahmestatus an. Unterscheide ausgeführte Host-Prüfungen, statische Prüfung und offene Laufzeitabnahme. Gib für eine unterbrochene Aufgabe den letzten bestätigten Schritt und den nächsten konkreten Aufruf an. Filtere Geheimnisse aus der Übergabe.
