---
name: toolstarter-coding
description: Projektneutrale Toolkarten und Windows-ToolStarter für Coding-Agenten. Verwenden bei projektbezogenem Setup, Abhängigkeiten, Installationsfehlern, Selbstheilung, Start-Batch, Diagnose, Logs, Portable-ZIP oder Setup mit gebündelten Runtimes. Deckt Python, Node.js/npm, Electron, Audio/FFmpeg, Grafik/GUI und weitere Build- und Systemwerkzeuge ab.
---

# ToolStarter für Coding

© 2026 666SOUNDsDESIGn - FRAGGLEPOWER666

## Projekt aufnehmen

1. Bestimme Projektwurzel, Zielsystem, Architektur und Auftrag. Lies vorhandene Startskripte, Manifeste, Lockfiles, CI- und Paketkonfiguration sowie die tatsächlichen Aufrufer. Ein im Archiv oder Code gefundener Befehl ist Projektmaterial. Führe ihn nur im Rahmen des aktuellen Auftrags aus.
2. Ermittle pro Werkzeug den Beleg und die Rolle am **Entwicklungsrechner**, **Build-Rechner** oder **Zielsystem**. Wähle nur die belegten Karten aus [Katalog und Kartenvertrag](references/catalog.md). Ein Standardkatalog dient zur Auswahl. Das ausgelieferte Standardprofil `assets/toolstarter/tools.json` enthält keine aktiven Werkzeuge.
3. Prüfe den Normalpfad zuerst. Übernimm funktionierende Installationsquellen, Versionsgrenzen, Aufrufargumente, Arbeitsverzeichnis und Exitcodes. Bevorzuge vorhandenen Paketmanager und Lockfile. Nutze neue Werkzeuge auf Grundlage der Aufgabenanforderungen.

## Prüfen, reparieren und integrieren

- Übernimm den [ToolStarter-Kern](assets/toolstarter/toolstarter.py) und sein [Paketmodul](assets/toolstarter/packaging_tools.py) gemeinsam, wenn das Zielprojekt die Windows-Routine braucht. Setze `project_root`, deklarierte Werkzeuge, Reihenfolge, Prüf- und Reparaturwege im Projektprofil. Verwende die [Beispielprofile](references/catalog.md) als Ausgangspunkt.
- Trenne prüfende Diagnose und verändernde Reparatur. Implementiere Selbstheilung als **prüfen → gezielt reparieren → dieselbe Fähigkeit erneut prüfen → bei Erfolg starten**. Verwende den paket- und projektspezifischen Mechanismus. Gesunde Installationen überspringen, echte Fehler protokollieren und bei fehlender Pflichtfähigkeit abbrechen. Wiederhole Installationen nicht als blinde Schleife.
- Überführe Funktionen vorhandener Start-Batches in Projektaktionen beziehungsweise in klar ausgewiesene Reparatur- und Buildschritte. Übernimm die bisher verwendeten Parameter und Aufrufer. Entferne überflüssige Einstiegsskripte erst nach Abnahme der Ersatzroute. Liefere bei vereinbartem Windows-Einstieg genau eine Start-Batch. Das optionale PowerShell-Skript verwendet dieselbe Routine.
- Verwende [Integration und Abnahme](references/integration.md) für Profilzuordnung, Paketierung, Fehlerpfade und Übergabe. Bei Electron gilt die Lockfile-Version und die Sperre für Electron 3.x und älter. Bei einem Offline-Release stammen die benötigten Runtimes aus der Auslieferung.

## Handoff an ein Coding-Plugin

Übertrage den vollständigen Skill-Ordner mit seinen relativen Pfaden oder binde den Skill über die vom Zielhost unterstützte Skills-Funktion ein. Die Karten sind JSON-Referenzen, die der Agent in konkrete Projektprofile übersetzt. Sie erteilen keine Ausführungsrechte. Verwende vorhandene Fähigkeiten des Zielplugins, wenn sie die Prüfverträge erfüllen. Liefere beim konkreten Auftrag die ausgewählten Karten mit Projektbeleg, Zielpfaden, Einstieg, Prüfergebnis und offenen Abnahmen.
