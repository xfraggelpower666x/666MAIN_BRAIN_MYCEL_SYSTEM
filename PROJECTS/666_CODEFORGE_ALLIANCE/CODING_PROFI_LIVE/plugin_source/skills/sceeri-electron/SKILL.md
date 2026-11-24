---
name: sceeri-electron
description: Entwickelt, auditiert und repariert Electron-Anwendungen mit Main, Preload, Renderer, IPC, Tests sowie Portable- und Installer-Builds.
---

# Electron Engineering

1. Ermittle Electron-, Node- und Paketmanager-Versionen, Lockfile, Main-Einstieg, Preload, Renderer, IPC, Build- und Packager-Konfiguration. Behalte vorhandene Forge-, Builder- oder andere Projektkonfiguration bei. Prüfe Entwicklungsstart und gepackten Start separat. Leite die unterstützten OS- und CPU-Ziele aus der Basis ab.
2. Ordne Änderungen der richtigen Prozessgrenze zu. Lasse privilegierte Datei- und Prozessarbeit in Main oder einem geeigneten Backend. Verwende einen eng gefassten Preload-Vertrag und validiere IPC-Sender, Parameter und erlaubte Zielpfade. Prüfe Kontextisolation, Sandbox, deaktivierte Node-Integration im Renderer, Navigation, neue Fenster und CSP anhand der verwendeten Electron-Version. Stelle UI-Fehler und Fortschritt über eng definierte Ereignisse bereit.
3. Prüfe Ressourcenpfade im Entwicklungs- und Paketbetrieb. Ermittle Ressourcen aus der Packager-Konfiguration und dem gepackten Layout. Stelle ausführbare Hilfstools in einem realen Ressourcenverzeichnis bereit, soweit das Projekt externe Prozesse startet. Verwende im installierten und portablen Build die zu diesem Layout passende Ressourcenauflösung, etwa über process.resourcesPath. Prüfe native Module auf Electron-ABI und Zielarchitektur und behandle benötigte Begleitdateien als Teil des Builds.
4. Nutze bei ausdrücklich beauftragter Paketierung für Windows die passenden [Auslieferungsprofile](../../references/windows-auslieferungsprofile.md). Nutze die englischen Aktionen in STARTEN.bat des Quellpakets. Die Zielapp bietet English / Deutsch mit Englisch als Standard. Bei FFmpeg oder FFprobe lade zusätzlich [FFmpeg](../sceeri-ffmpeg/SKILL.md).
5. Prüfe Main-Start, Renderer-Laden, IPC, Ressourcenauflösung und Fehlerpfade im normalen Einstieg. Unterscheide vorhandene Build-Datei, beobachteten Build und geprüften Start auf der Zielplattform. Bei einem nativen Modul oder externen Tool gehört ein fachlicher Smoke-Test in beide Windows-Profile.

Für das Windows-Starterprofil gilt [STARTEN.bat für Windows-Projekte](../../references/windows-starten-build.md). Bevorzuge bei geeigneter Zielarchitektur Electron mit lokalem BrowserWindow ohne WebView2 und ohne Electron-Webview-Tag. Prüfe den aktuellen Upstream-Support. Electron 3.x und älter sind gesperrt.
