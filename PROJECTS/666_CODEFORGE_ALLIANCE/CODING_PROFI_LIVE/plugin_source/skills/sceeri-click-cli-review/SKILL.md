---
name: sceeri-click-cli-review
description: "Auditiert vorhandene Click-CLIs auf Vertragsfehler, Ausgabe, Exit-Codes, Testbarkeit und Regressionen."
---


# Click-CLI prüfen

Inventarisiere Command-Baum, Entry Points, Callbacks und geteilten Kontext. Prüfe Typen, Optionsnamen, Required/Default-Verhalten, Dateipfade, Exit-Codes, stdout/stderr und Übersetzung fachlicher Fehler. Markiere inkompatible Flag- oder Ausgabeänderungen besonders, weil sie bestehende Skripte brechen können. Ordne Befunde nach Auswirkung und Quellstelle. Liefere pro Befund einen minimalen Diff und einen Test mit beobachtbarem Ergebnis. Kennzeichne Konventionen und ungetestete Befunde. Für neue Kommandos nutze [Click-Entwurf](../sceeri-click-cli/SKILL.md).
