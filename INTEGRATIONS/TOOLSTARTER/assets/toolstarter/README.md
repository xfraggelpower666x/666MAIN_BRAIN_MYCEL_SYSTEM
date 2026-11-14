# 666 TOOLSTARTER v1.0.1

© 2026 666SOUNDsDESIGn - FRAGGLEPOWER666

Wiederverwendbarer Windows-Starter für Projektwerkzeuge. Voraussetzung ist Python 3.10 oder neuer. Das Fenster verwendet das bei CPython üblicherweise mitgelieferte Tcl/Tk. WinGet wird für die im Profil ausgewiesenen Systempakete verwendet.

## Schnellstart

1. ZIP vollständig entpacken und **STARTEN.bat** doppelklicken.
2. Bei Bedarf im Fenster neben der Aktionsauswahl von `en` auf `de` wechseln.
3. **Prüfen** ausführen. Das Standardprofil ist leer. Wähle dein eigenes Profil oder eine Vorlage aus `examples/`. Ein leeres Profil meldet, dass keine Werkzeuge konfiguriert sind.
4. **Installieren / reparieren** ausführen, falls ein benötigtes Werkzeug fehlt oder seinen Test nicht besteht. Dieser Modus darf auch fehlende optionale Werkzeuge aus dem Profil installieren.
5. Falls das gewählte Profil Projektaktionen definiert, eine Aktion auswählen und **Selbstheilung & Start** anklicken. Der Starter repariert fehlerhafte Pflichtwerkzeuge einmal, prüft sie erneut und startet erst danach die Befehle.

Das Fenster zeigt Werkzeugstatus, Prozessausgabe und Exitcodes live. Die Konsole eignet sich für Skripte und CI. Ein laufender Vorgang bleibt im Fenster geöffnet, bis der gestartete Prozess endet. Für reine Konsolennutzung genügt Python ohne Tcl/Tk. `STARTEN.ps1` bietet dieselben Argumente; es gelten die vorhandenen PowerShell-Ausführungsrichtlinien.

```bat
STARTEN.bat gui --lang de
STARTEN.bat check --lang de
STARTEN.bat repair --lang de
python toolstarter.py check --profile tools.json
.\STARTEN.ps1 check --lang de
```

Alle Batch-Modi laufen über **STARTEN.bat**. Ohne Argumente öffnet sie das Fenster. Mit Argumenten reicht sie den Exitcode für andere Skripte und CI weiter.

## Ein anderes Projekt anbinden

Kopiere `tools.json` als eigenes Profil und verwende es per Dateiauswahl oder `--profile`. Die Vorlagen `examples/audio.example.json`, `examples/electron.example.json` und `examples/package.example.json` werden nur bei ausdrücklicher Auswahl geladen. Passe beim Kopieren `project_root` an den neuen Speicherort an. Profilnamen, Projektpfade, Startbefehle, Versionen und Paketmetadaten stammen aus deinem Zielprojekt.

Das npm-Rezept verwendet bei fehlenden oder defekten Abhängigkeiten `npm ci`. Dabei wird das lokale `node_modules` anhand des Lockfiles neu installiert. Setze für Node ein projektspezifisches Versionskriterium in der Probe, wenn dein Projekt eine Mindestversion voraussetzt.

| Feld | Verwendung |
|---|---|
| `project_root` | Absolut oder relativ zum JSON-Profil. Enthält die Projektdateien und ist Arbeitsverzeichnis aller Befehle. |
| `path_dirs` | Zusätzliche lokale Binärordner. Im Standardprofil leer. |
| `required_files` | Relative Pflichtpfade, die vor der Arbeit geprüft werden. |
| `tools` | Werkzeugliste mit eindeutigen IDs. Abhängigkeiten unter `after` referenzieren vorherige Einträge. Mit `required: false` bleibt ein Fehlschlag optional. |
| `before_actions` | Befehle vor jeder Projektaktion, etwa Tests und Release-Prüfungen. |
| `actions` | Name, Befehlsfolge in `commands` und optional erwartete, nichtleere Dateien in `artifacts`. |
| `clean_electron_env` | Entfernt vererbte Electron- und npm-Plattform-/Architektur-Overrides für diese Prozesse. |

- **`exe`** braucht `names` mit Dateinamen im PATH oder lokalen Pfaden. `args` ist standardmäßig `["--version"]`. `match` kann die Ausgabe mit einem regulären Ausdruck prüfen. Für die Reparatur dienen `winget` oder ein eigenes `repair`-Befehlsarray.
- **`audio`** prüft FFmpeg und FFprobe, erzeugt eine kurze WAV-Datei im temporären Verzeichnis und liest Codec und Sample-Rate mit FFprobe zurück. Eine Kopie beider EXE-Dateien in einem lokalen Binärordner wird bevorzugt. Die geprüften Programme werden in den Projektprozess als `FFMPEG_PATH` und `FFPROBE_PATH` übernommen.
- **`npm`** prüft per `npm ls --all --include=dev`. Mit `locked_packages` kannst du exakte Paketversionen aus einem modernen npm-Lockfile, mit `files` projektlokale Shims oder andere Dateien einfordern.
- **`electron`** verwendet standardmäßig das Paket `electron`. `check` und `repair` binden die projektspezifischen Hooks ein. Ohne Reparaturhook wird das im installierten Paket vorhandene Installationsskript verwendet. Die bisherige Runtime wird bei einem fehlgeschlagenen generischen Reparaturversuch zurückgespielt. Vor der Freigabe muss die lokale EXE mit `--version` die passende Lockfile-Version melden.

Weiteres Werkzeug und Projektaktion, jeweils als Ausschnitt für `tools` und `actions`:

```json
{"id":"7zip","kind":"exe","names":["7z.exe","C:/Program Files/7-Zip/7z.exe"],"args":["i"],"match":"7-Zip","winget":"7zip.7zip"}
```

```json
{"diagnose":{"commands":[["@7zip","i"],["@python","scripts/diagnose.py"]]}}
```

Befehle sind JSON-Arrays mit einem Element je Argument. `@<Werkzeug-ID>` nutzt die konkret geprüfte EXE, `@python` den laufenden Python-Interpreter. Für PowerShell-Skripte verwende z. B. `["powershell","-NoProfile","-File","scripts/setup.ps1"]`. Verwende eigene Profile als ausführbare Projektkonfiguration nur aus vertrauenswürdigen Quellen. Die Routine ändert den PATH ihrer Kindprozesse, liest nach WinGet-Installationen den registrierten PATH neu und aktualisiert funktionsfähige Werkzeuge im Normalbetrieb nicht automatisch. WinGet kann je nach Paket eine Windows-Bestätigung oder neue Terminalsitzung erfordern.

## Abnahme

`check` installiert nichts und startet keine Projektaktionen. `repair` versucht pro fehlerhaftem Eintrag höchstens eine Reparatur und kontrolliert danach erneut. `run` versucht standardmäßig eine Reparatur für fehlerhafte Pflichtwerkzeuge und bricht bei einer fehlgeschlagenen Gegenprobe, einem Projektbefehl mit Fehlercode oder einer fehlenden erwarteten Build-Datei ab. Die projektlokale Datei `.toolstarter.lock` ist ein Betriebssystem-Lock für Reparaturen und Projektaktionen.

Der Windows-Doppelklickstart, WinGet-Installationen und Projektaktionen benötigen eine Abnahme auf Windows mit dem Zielprojekt.

## Diagnose und Log

```bat
STARTEN.bat diagnose --lang de
STARTEN.bat diagnose --profile .\examples\audio.example.json --lang de
```

Diagnose meldet Interpreter, Projektpfad, auffindbare Werkzeuge, Einzelprüfungen und Exitcode. Jeder Prüflauf, Reparaturversuch, Start und Paketbau schreibt ein eigenes UTF-8-Log nach `%LOCALAPPDATA%\666SOUNDsDESIGn\ToolStarter\logs`. Die Oberfläche öffnet den Ordner über **Logs öffnen**. Häufige Zugangsdatenmuster werden gefiltert. Projektpfade und Programmausgaben können private Angaben enthalten. Vor einer Weitergabe das Log kontrollieren.

## Portable und Setup

Der Modus `package both` übernimmt einen vorhandenen, selbsttragenden Windows-Anwendungsbuild und vom Profil ausdrücklich ausgewiesene Runtime-Dateien. Er prüft die Laufzeitdateien aus der vorbereiteten Paketstruktur und erzeugt aus derselben Nutzlast ein Portable-ZIP und ein Inno-Setup. Der Aufruf der installierten oder entpackten App läuft über die mitgelieferte `STARTEN.bat`.

```bat
STARTEN.bat package both --profile mein-release.json --lang de
```

Auch `package portable` und `package setup` sind verfügbar. Die ZIP-Variante wird vollständig gegen das SHA-256-Manifest zurückgelesen. Für Setup wird der Compiler-Exitcode und die binäre Ausgabe geprüft. Die Installation und der Start auf einem sauberen Windows-System sind die abschließende Abnahme. Inno Setup wird nur auf dem Build-PC benötigt. Alle Dateipfade, mit denen die App zur Laufzeit arbeitet, müssen aus dem installierten Paket auflösbar sein.

Die universelle Übernahme, das neutrale Paketprofil und die Migration auf eine einzige Batch stehen in **HANDOFF.md**.

`self_heal_on_run: false` schaltet die Installation beim Projektstart für dieses Profil ab. **Installieren / reparieren** bleibt nutzbar. Ein explizites Electron-Profil mit Lockfile auf 3.x oder älter wird bereits vor npm oder Installationsbefehlen blockiert. Die Untergrenze ist eine Sperre gegen den alten Fallback. Die Wahl einer upstream-gepflegten Electron-Version bleibt Teil der Projektfreigabe.
