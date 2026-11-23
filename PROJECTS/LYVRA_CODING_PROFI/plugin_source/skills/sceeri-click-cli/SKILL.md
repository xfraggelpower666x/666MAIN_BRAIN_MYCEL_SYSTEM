---
name: sceeri-click-cli
description: "Entwirft und erstellt Python-CLIs mit Click, Subcommands, Eingabevalidierung und überprüfbarer Kommandozeilen-UX."
---


# Click-CLI entwerfen

1. Lege pro Kommando Nutzerziel, Argumente, Optionen, Standardwerte und Exit-Codes fest. Prüfe bestehende Namen, Alias- und Env-Kompatibilität. Definiere Beispiele für Hilfe, Erfolg und ungültige Eingabe.
2. Nutze Click-Gruppen, Parametertypen, Choices und Pfadprüfungen passend zum vorhandenen Projekt. Trenne CLI-Parsing, Fachlogik und formatierte Ausgabe. Strukturiere größere Command-Gruppen in klaren Modulen.
3. Nutze Click-Ausgabe für Menschen und maschinenlesbare Formate entsprechend Vertrag. Halte Diagnoseausgabe von Daten auf stdout getrennt und fordere interaktive Eingaben nur in geeigneten Kontexten.
4. Liefere auf Auftrag vollständige betroffene Dateien oder einen Diff, Installations- und Nutzungsweg des Zielprojekts. Prüfe Hilfe, Standardwerte, ungültige Eingaben, Exit-Codes und Ausgabe mit Clicks Test-Runner in freigegebener Umgebung.
