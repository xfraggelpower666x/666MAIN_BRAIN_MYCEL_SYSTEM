# 666 TOOLSTARTER · Universeller Einbau

© 2026 666SOUNDsDESIGn - FRAGGLEPOWER666 · Version 1.1.0

## 1. Projektvertrag erfassen

- Bestehende Batchdateien, normale Startbefehle, Arbeitsverzeichnis, Argumente, Exitcodes und Menüpunkte erfassen. Auch andere Aufrufer prüfen, etwa Verknüpfungen, CI und geplante Aufgaben.
- Die Werkzeuge auflisten, die das Projekt **beim Nutzer** ausführt oder lädt. Für jeden Eintrag die Architektur, Version oder Versionsgrenze, EXE, zusätzliche DLLs, Plugins, Daten, Konfigurationen, Lizenztexte und einen kurzen Funktionstest festlegen.
- Buildwerkzeuge wie npm, electron-builder und ISCC werden für den Build-PC eingetragen. Wenn eine Anwendung auf dem Zielsystem selbst Node, Java, Python oder ein anderes Programm startet, gehört dessen dort benötigte Runtime in die Nutzlast. Bei Electron gehört der komplette gepackte App-Ordner dazu.
- Pflichtwerkzeuge als solche kennzeichnen. Optional muss im Produkt tatsächlich optional sein.

## 2. Starter integrieren

1. `toolstarter.py`, `packaging_tools.py`, `tools.json` und `STARTEN.bat` in einen definierten Projektordner übernehmen. Die beiden Python-Dateien bleiben zusammen. `STARTEN.ps1` ist Teil des Entwicklungsstarters und muss neben der Batch liegen.
2. `project_root` relativ zum Profil setzen. Projektbezogene Binärordner unter `path_dirs` eintragen. Projektlokale Binaries werden im PATH der gestarteten Programme bevorzugt.
3. Für jedes benötigte Werkzeug einen Probe-Befehl und einen Reparaturweg eintragen. Ein EXE-Eintrag kann über WinGet oder einen projektspezifischen Hook repariert werden. Eigene Installationsskripte sollen versionierte, vertrauenswürdige Quellen, stillen Fehlercode und eine nachprüfbare Ausgabe verwenden.
4. Bestehende Befehlsfolgen in `before_actions` oder in benannte `actions` übertragen. Auf verriegelte Versionen und unveränderte Ausgabepfade achten. Für Windows-CMD-Wrapper den nativen Einstieg verwenden, beispielsweise `node cli.js` oder bei PowerShell `powershell -File scripts/setup.ps1`.
5. Mit `STARTEN.bat diagnose` beginnen. Fehlende oder defekte Komponenten über `repair` bzw. `run <aktion>` prüfen. Die Reihenfolge muss abhängige Werkzeuge nach ihren Voraussetzungen auflisten.
6. Gegenprobe für funktionierende Installation, fehlendes Werkzeug, defekte Runtime und Fehler-Exitcode durchführen.

## 3. Vorhandene Batchdateien zusammenführen

| Vorhandene Aufgabe | Ziel |
|---|---|
| Menü und Sprache | Graphisches ToolStarter-Menü, optional CLI-Parameter |
| Umgebungs- und Pfadauflösung | `path_dirs`, Profile und paketierte Runtime-Pfade |
| Versionsprüfung | `tools` mit konkretem Probe-Befehl oder Electron-Lock |
| Installationsroutine | Gezielter `repair`-Hook oder WinGet-Paket |
| Tests / Branding / Release-Gates | `before_actions` oder Befehlsfolge der Aktion |
| Player starten / Tests / Wartung / Build | Eigene Aktions-ID in `actions` |
| Alte Batch-Argumente | Entsprechende CLI-Aktion und ggf. Routing in der einzigen Batch |

Sichere die Originale vor der Migration außerhalb der ausgelieferten Dateien. Übersetze die Funktionen zuerst, aktualisiere die Aufrufer und teste sämtliche belegten Einstiegspunkte. Entferne ältere Start-Batches erst nach der Abnahme. Build-Hilfsskripte, die wirklich von der Anwendung oder vom Build aufgerufen werden, bleiben bis zur Migration ihrer Aufrufer erhalten.

## 4. Setup und Portable aus derselben Nutzlast bauen

1. Den selbsttragenden Anwendungsbuild im Windows-Build-Workflow erzeugen. Bei Electron den vollständigen Windows-App-Ordner mit Haupt-EXE, Resources und Electron-Runtime verwenden. Bei Python einen eingefrorenen App-Build mit seinen Assets erstellen oder einen ausdrücklich eingebetteten, lizenzkonformen Interpreter als Programmeinstieg konfigurieren.
2. Erforderliche, redistribuierbare Laufzeitwerkzeuge in versionierte Release-Eingabeordner ablegen. Für FFmpeg und FFprobe dieselbe Buildfamilie verwenden und Lizenz/Weitergabebedingungen für genau diesen Build erfüllen. Zusätzliche native Abhängigkeiten und Betriebssystemvoraussetzungen im Projekt dokumentieren.
3. `examples/package.example.json` kopieren und passend zum Originalprojekt ausfüllen. `include` übernimmt komplette Ordner bzw. Dateien. Das Ziel `.` kopiert einen Quellordner in die Paketwurzel. Die Ausgaben müssen außerhalb eines übernommenen Quellbaums liegen. `entry` bezeichnet die relative native Start-EXE. `entry_args` ist optional, z. B. ein Skriptpfad bei eingebettetem Interpreter.
4. Jede Pflicht-Runtime in `required_runtime_ids` aufführen. Je ID unter `runtime` Dateien, Lizenzdateien und ausführbare Probes definieren. Jede Probe braucht eine paketrelative `exe` sowie bei Bedarf `args` und `match`. Für echte Funktionsabnahme einen kurzen Headless-Modus in die App integrieren, der auch native Abhängigkeiten lädt und bei Fehlschlag mit einem Fehlercode endet. `path_dirs` und `runtime_environment` beziehen sich auf Dateien in der Nutzlast.
5. Auf dem Build-PC Inno Setup bereitstellen oder den absoluten Pfad zu `ISCC.exe` in `package.iscc` setzen. Dann `STARTEN.bat package both --profile mein-release.json` ausführen. ZIP, Setup und gemeinsames Manifest erscheinen unter `package.output_dir`. Beide Ausgaben aus dem gleichen Staging bauen, wenn sie exakt zusammengehören.
6. Beide Varianten in einer sauberen Windows-VM auf unterstützter Architektur installieren beziehungsweise entpacken. Ohne Netz, ohne projektbezogene PATH-Einträge und ohne die Buildwerkzeuge starten. Funktionstest für jede Pflicht-Runtime ausführen, bei FFmpeg beispielsweise eine Datei konvertieren und mit FFprobe prüfen. Die installierten und entpackten Dateien zusätzlich gegen das mitgelieferte SHA-256-Manifest vergleichen. Release nur mit dokumentiertem Ergebnis freigeben.

### Bestehender Builder und optionale Laufzeitadapter

Ein vorhandener Builder kann seinen vollständigen Anwendungsordner als Eingabe an den Paketbau übergeben. Wenn der vorhandene Installer weiter direkt verwendet werden soll, müssen erforderliche Laufzeitdateien auch in dessen eigener Build-Konfiguration eingetragen und geprüft werden. Die Zielanwendung bindet mitgelieferte Werkzeuge über paketrelative Pfade ein. Bei Electron kann die Anwendung dazu `process.resourcesPath` verwenden.

Für eine FFmpeg-Paketprüfung ergänze die Pflicht-ID `ffmpeg`, die beiden Binärdateien mit Lizenz und `runtime_environment` mit `FFMPEG_PATH` und `FFPROBE_PATH`. Der Paketbau führt dann den WAV-Funktionstest mit dem gebündelten Paar aus.

## 5. Electron und Selbstheilung

- Die Projektversion stammt aus `package-lock.json`. Die Routine vergleicht npm-Version und lokale Runtime damit. Electron 3.x und ältere Majors werden vor der Reparatur und vor `npm ci` abgelehnt, sofern das Projekt einen Electron-Eintrag im Starterprofil führt.
- Wenn das Zielprojekt eigene Electron-Check-/Repair-Hooks hat, können sie im Profil eingetragen werden. Ohne Reparaturhook verwendet die Routine das Installationsskript des lokal installierten Electron-Pakets. Die generische Reparatur sichert vorhandenes `dist` und `path.txt` und spielt beides bei einem Fehlschlag zurück.
- `check` und `diagnose` prüfen. `repair` repariert fehlerhafte konfigurierte Einträge. `run` repariert standardmäßig fehlerhafte Pflichtwerkzeuge und bricht ab, wenn eine Gegenprobe scheitert.
- Auf dem Zielsystem startet die paketierte Batch aus der mitgelieferten Nutzlast. Der Start installiert dort keine Buildwerkzeuge. Tools, die die App direkt startet, müssen vom App-Code aus dem mitgelieferten Verzeichnis aufgelöst werden.

Paketdiagnose auf dem Zielsystem über `STARTEN.bat --diagnose` aufrufen. Der mitgelieferte PowerShell-Check vergleicht die Dateien gegen das Manifest und schreibt sein Ergebnis in den lokalen Logordner. Er setzt die vorhandenen Windows-Ausführungsrichtlinien voraus. Der Datei-Check ergänzt die Funktionstests in der sauberen VM. Im Paketprofil prüft `electron_package` den Lockfile-Eintrag auch vor dem Paketbau. Die gestartete App muss im Headless-Test ihre tatsächliche Electron-Version aus `process.versions.electron` melden, etwa als `SMOKE_OK electron=VERSIONSNUMMER`. Der passende Regex liegt im Projektprofil, z. B. `^SMOKE_OK electron={electron_version}$`. Das Paketprofil setzt für `{electron_version}` die exakt erwartete Lockfile-Version ein.
