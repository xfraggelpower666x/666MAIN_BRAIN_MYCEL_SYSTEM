# Sprachwahl und Build

Verwende diese Referenz beim bestehenden Coding-Profi-Routing für Anleitung, Unterstützung, Analyse, Review, Repair, Weiterentwicklung und Neubau. Übernimm den gedeuteten Auftrag aus der [NLP-Koordination](nlp-koordination.md). Wende die [Entscheidungs- und Lernschleife](coding-profi-zusammenspiel.md#entscheidungs--und-lernschleife) auf die Wahl und Korrektur von Sprach- und Build-Facetten an. Neue Quellbefunde präzisieren betroffene Teilabsichten oder Schnittstellen im gemeinsamen Arbeitsstand.

## Sprache, Aufgabe und Toolchain ermitteln

1. **Semantik.** Bestimme die gewünschte Arbeit und ihren Einstieg. Bei Bestand lies das nächstliegende Projektmanifest, Lockfile oder Toolchain-Pinning, Einstieg oder Aufrufer, betroffene Quellen, Tests und die zugehörige Build-Konfiguration. Bei neuen Projekten leite eine passende Wahl aus Ziel-OS, GUI, Schnittstellen, Laufzeit, Betrieb und Distributionsform ab. Halte vorgeschlagene Architektur getrennt vom belegten Bestand.
2. **Kausalität.** Verfolge den betroffenen Ablauf vom Einstieg bis zur Wirkung. Unterscheide Quellcode, generierten oder gebündelten Code, Testcode, Skripting und Auslieferung. Markiere je Komponente die maßgebliche Sprache, ihren Compiler oder Interpreter sowie Schnittstellen zu anderen Komponenten. Prüfe bei mehreren Sprachen die erreichbaren Übergänge, etwa JSON-Schema, HTTP, stdin/stdout, IPC, CLI, Dateiformat oder ABI. Nutze Parallel Development für unabhängige Stränge mit getrennten Schreibzielen. Gemeinsame Verträge, Generatoren und Paketausgaben brauchen eine abgestimmte Reihenfolge.
3. **Evidenz.** Eine Endung oder README-Zeile ist ein Hinweis. Aussagekräftiger sind targetgebundene Manifeste, Arbeitsverzeichnis, erreichbare Aufrufer, tatsächlich verwendete Compiler-Eingaben und beobachtete Aufrufe. Wenn Befunde auseinanderlaufen, prüfe die Quellzuordnung des konkreten Targets. Bei fehlendem Material markiere die Wahl als ABGELEITET oder OFFEN und bearbeite eindeutige Teile weiter. Dokumentiere nur entscheidende Fundstellen und Prüfergebnisse.
4. **Emergenz.** Verknüpfe Befunde aus mehreren Komponenten, wenn sie eine bessere Korrektur oder Gegenprobe nahelegen. Wenn etwa TypeScript-Typen stimmen und der Python-Dienst dennoch ein Feld zurückweist, prüfe zuerst den tatsächlich serialisierten Payload und den Consumer-Vertrag. Ändere Sprache, Toolchain oder Architektur bei Bestand nur, wenn der direkte Auftrag und die Belege es tragen. Aktualisiere die betroffene Route, wenn Gegenbelege zeigen, dass ein anderer Einstieg oder Codegenerator maßgeblich ist.

Aktiviere die spezialisierten Facetten für die betroffenen Pfade. Führe beim Verbund denselben Soll-Vertrag und eine gemeinsame Gegenprobe weiter. Der Sprachskill entscheidet über Implementierung und Prüfmethode seiner Komponente. Der direkte Auftrag bestimmt die Befugnis. Audit, Review und Analyse sind lesend.

## Fachfacetten

| Sprache oder Pfad | Typische Signale am betroffenen Target | Fachfacette |
| --- | --- | --- |
| Python | `pyproject.toml`, Lockfile, importierter Einstieg, aktive venv | [Python](../skills/sceeri-python-engineer/SKILL.md) |
| Java/JVM | Maven- oder Gradle-Modul, aktive Source Sets und JDK-Ziel | [Java](../skills/sceeri-java-engineer/SKILL.md) |
| HTML, CSS, Browser-JavaScript | Dokument, CSS-Einstieg, DOM-Aufrufer, Browser-Build | [Web](../skills/sceeri-web-engineer/SKILL.md) |
| Scriptable-JavaScript | iOS-App, Scriptable-APIs, Kurzbefehl oder Widget als belegter Einstieg | [Scriptable](../skills/sceeri-scriptable-ios/SKILL.md) |
| TypeScript, Node.js, JavaScript-Tooling | `tsconfig`, Workspace, package scripts, Exporte, Lockfile | [TypeScript und Node.js](../skills/sceeri-typescript-node/SKILL.md) |
| C#/.NET | `.csproj`, Solution, Ziel-Framework und Runtime-ID | [C#/.NET](../skills/sceeri-dotnet-engineer/SKILL.md) |
| C/C++ | CMake-Target, Compiler-Aufruf, Header, Linkziel | [C/C++](../skills/sceeri-c-cpp-engineer/SKILL.md) |
| Rust | `Cargo.toml`, Workspace, Traits, Target-Triple | [Rust](../skills/sceeri-rust-engineer/SKILL.md) |
| Go | `go.mod`, `go.work`, main-Paket, Build-Tags | [Go](../skills/sceeri-go-engineer/SKILL.md) |
| Kotlin | `.kt`-Source-Set, Kotlin- oder Android-Plugin | [Kotlin](../skills/sceeri-kotlin-engineer/SKILL.md) |
| Swift | `Package.swift`, Xcode-Scheme, Target | [Swift](../skills/sceeri-swift-engineer/SKILL.md) |
| Dart/Flutter | `pubspec.yaml`, Dart-Einstieg, Flutter-Plattform-Runner | [Dart/Flutter](../skills/sceeri-dart-flutter/SKILL.md) |
| PHP | `composer.json`, Autoload, PHP-Einstieg und Runtime | [PHP](../skills/sceeri-php-engineer/SKILL.md) |
| Ruby | `Gemfile`, Gemspec, Ruby-Einstieg | [Ruby](../skills/sceeri-ruby-engineer/SKILL.md) |
| SQL | Tatsächlicher DB-Dialekt, Migrationskette, aufrufender Code | [SQL](../skills/sceeri-sql-engineer/SKILL.md) |
| Bash/POSIX Shell | Aufrufer, Shebang, CI-Shell, Host | [Shell-Scripting](../skills/sceeri-shell-scripting/SKILL.md) |
| PowerShell | Hostversion, `.ps1`, Module, Aufrufart | [PowerShell](../skills/sceeri-powershell-scripting/SKILL.md) |
| Windows Batch/CMD | `.bat`, `.cmd`, Aufruf über `cmd.exe`, `STARTEN.bat` | [Windows Batch](../skills/sceeri-windows-batch-build/SKILL.md) |

Ordne weitere nachgewiesene Sprachen über [Code Engineering](../skills/sceeri-code-engineering/SKILL.md) und die vorhandenen Projektwerkzeuge ein.

## Build-Abgleich im selben Auftrag

- **Vor der Änderung** verfolge die relevante Route von Start, Test und Build bis zu Portable oder Setup, soweit diese für das Ziel existieren. Erfasse tatsächliche Aufrufer, Arbeitsverzeichnis, Zielarchitektur, Werkzeugversionen, Lockfiles, Eingaben, Ausgabepfade und Exitcode-Übergaben. Folge delegierten Skripten und prüfe generierte Quellen an ihrer Ursprungsdefinition. Bei Bestand kann der Abgleich ergeben, dass kein Folgepatch nötig ist.
- **Im gleichen Kandidaten** aktualisiere bei einem Änderungsauftrag die betroffenen Build- und Skriptpfade. Eine neue EXE-Bezeichnung kann beispielsweise Starter, CI-Artefakt und Installer-Eingabe betreffen. Eine reine fachliche Änderung ohne neue Build-Anforderungen erhält die bestehenden Aufrufer und Skripte. Bei Windows-Lieferung gilt der [eine Entwicklungsstarter](windows-auslieferungsprofile.md#ein-entwicklungsstarter) mit `--setup`. Interne Shell-, PowerShell- oder Python-Hilfen können von dort aufgerufen werden. ToolStarter bleibt beim Entwicklungs- und Build-Pfad.
- **Bei der Abnahme** prüfe dieselbe Revision über den dokumentierten Einstieg. Verwende die passenden Compiler-, Lint- und Tests, die Schnittstellen-Gegenprobe und die bestellten Paketaktionen. Prüfe echte Artefaktpfade, Architektur und Exitcodes. Weise statischen Befund, ausgeführten Test und Host-Abnahme getrennt aus. Bei fehlendem Windows-Host bleibt der native Batch- oder Setup-Lauf offen. Führe im Abschluss kurz auf, welcher Skriptpfad geprüft oder angepasst wurde und wo noch ein Nachweis fehlt.
