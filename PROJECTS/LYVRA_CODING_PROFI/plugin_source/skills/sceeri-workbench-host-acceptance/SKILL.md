---
name: sceeri-workbench-host-acceptance
description: "Unterstützt Python schreiben, erstellen, reviewen, debuggen, refaktorieren und Laufnachweise im Chat."
---

# Python Workbench im Chat

| Aktion | Eingabe | Ausgabe |
| --- | --- | --- |
| Schreiben | Zweck, Ein- und Ausgabe, Python-Version | Vollständige kopierbare Datei, Aufruf und Beispiel |
| Projekt erstellen | Anforderungen, Stack und Einstieg | Dateibaum, vollständige Inhalte und Prüfplan |
| Debuggen | Code, Traceback, Soll/Ist und Umgebung | Ursachenbeleg, minimaler Diff und Regression |
| Refaktorieren | Original, Schwerpunkt und stabile Verträge | Vorher/Nachher, Auswirkungen und Prüfschritte |
| Review | Quelltext oder Diff | Befunde nach Schwere und Fundstelle, Syntax- und Verhaltensnachweise getrennt |
| Ausführung prüfen | Code, Testfall und zulässige Host-Umgebung | Beobachtetes Ergebnis und Exit-Status, sonst Status OFFEN mit Prüfplan |
| Arbeitsstand sichern oder laden | Gewählter Projektbezug und vorheriger Stand | Kopierbarer Dateisatz oder Handoff mit Versionsbezug und bestätigtem Readback |

Die Chat-Facette liefert Text und Dateiinhalte. Ausführung, Abbruch und dauerhafte Ablage sind nur nachweisbar, wenn eine passende Host-Aktion vorhanden ist und ihr Ergebnis beobachtet wurde. Bei einer verfügbaren Laufzeit nutze ausschließlich die freigegebene Umgebung und in dieser Umgebung ausführbare Testfälle. Berichte je Prüfung Eingabe, Kontext und beobachtetes Ergebnis.

## Chat-Arbeitsstand und Folgeaktionen

Halte Original, Kandidat, Dateiliste und Startdatei getrennt. Prüfe relative Pfade, doppelte Namen und vorhandene Startdatei. Liefere auf Wunsch einen kopierbaren Export, eine aus den sichtbaren Ständen gebildete Projektübersicht oder die Fortsetzung eines vom Nutzer bereitgestellten Stands. Erläutern, Typen ergänzen, Tests ergänzen, vereinfachen, Sicherheitsreview und optimieren sind einzeln wählbare Arbeitsaufträge. Sammle bei mehreren Änderungen Diffs und unabhängige Nachweise. Die [Abnahmefälle](../../references/chat-abnahme.md) zeigen die erwarteten Chat-Ausgaben.
