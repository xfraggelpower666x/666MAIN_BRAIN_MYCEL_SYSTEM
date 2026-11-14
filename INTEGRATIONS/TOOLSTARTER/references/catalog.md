# Werkzeugkatalog

Wähle anhand belegter Dateien, Aufrufe oder ausdrücklich gewünschter Zielarchitektur. Nutze die Karte `toolstarter` für Integration und die Fachkarten nur bei Bedarf.

| Beleg oder Aufgabe | Karte |
|---|---|
| Windows-Starter, Batch-Migration, Diagnose, Selbstheilung | [ToolStarter](cards/toolstarter.json) |
| `pyproject.toml`, Python-Entry-Point, Python-Lockfile | [Python und Paketmanager](cards/python.json) |
| `package.json`, JS/TS-Build, Node-Version, npm-/pnpm-/Yarn-Lockfile | [Node.js und Paketmanager](cards/node-npm.json) |
| Electron-App, Desktop-Runtime, Electron-Builder-Konfiguration | [Electron](cards/electron.json) |
| Konvertierung, Audiostreams, Medienformate, FFmpeg-Aufrufe | [Audio und Video](cards/audio-video.json) |
| GUI, Electron-Renderer, Qt/Tk, HTML/CSS, Accessibility | [Grafische Oberfläche](cards/gui.json) |
| Bilddateien, SVG, Thumbnail- oder Renderpipeline | [Bild und Grafik](cards/graphics.json) |
| `.git`, `.gitattributes`, Submodule | [Git und Git LFS](cards/git.json) |
| PowerShell-Skripte, WinGet, Windows-Umgebung | [Windows-Systemwerkzeuge](cards/windows-tools.json) |
| Java-Projekt, Maven/Gradle-Wrapper, JDK-Toolchain | [Java und JVM](cards/java.json) |
| `.sln`, `.csproj`, `global.json` | [.NET](cards/dotnet.json) |
| `CMakeLists.txt`, native Erweiterung, MSBuild | [Native Builds](cards/native-build.json) |
| `Cargo.toml`, `go.mod`, Rust- oder Go-Compiler | [Rust und Go](cards/rust-go.json) |
| Dockerfile, Compose-Datei oder expliziter Containerbetrieb | [Container](cards/containers.json) |
| DB-Treiber, Migrationen, deklarierter lokaler Datendienst | [Datenbanken](cards/data-tools.json) |
| Vorhandene Tests, statische Analyse, CI-Gates | [Test und Qualität](cards/quality.json) |
| Installer, Archiv, eingebettete Ziel-Runtimes | [Paketierung](cards/packaging.json) |

## Kartenvertrag v1

Jede Karte enthält `schema_version`, `id`, `name`, `evidence`, `roles`, `check`, `repair`, `delivery` und `acceptance`. Eine Rolle bezeichnet einen möglichen Einsatz auf Build-, Entwicklungs- oder Zielhost. Ermittle die tatsächliche Rolle aus dem Projekt. Die Texte sind ausführungsneutrale Arbeitsanweisungen. Leite konkrete Befehle und Pfade aus den Projektquellen ab.

## Code und Profile

- [Native Windows-Batch](../assets/toolstarter/STARTEN.bat), [PowerShell](../assets/toolstarter/STARTEN.ps1), [leeres Standardprofil](../assets/toolstarter/tools.json)
- [Audio-Profil](../assets/toolstarter/examples/audio.example.json), [Electron-Profil](../assets/toolstarter/examples/electron.example.json), [Paket-Profil](../assets/toolstarter/examples/package.example.json)
- Die Adapter im Python-Kern sind `exe`, `audio`, `npm` und `electron`. Für andere Karten `exe` mit einer geeigneten Probe und bei Bedarf einem projektspezifischen Reparaturhook nutzen. Die Karten ergänzen den Agenten um Fachwissen. Ein Werkzeug ist erst nach erfolgreicher Probe nutzbar.
