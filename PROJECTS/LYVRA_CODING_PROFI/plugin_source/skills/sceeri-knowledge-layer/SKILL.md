---
name: sceeri-knowledge-layer
description: "Erstellt und aktualisiert einen belegten Wissensstand für Code, Dokumente, Daten und Medienmetadaten und beantwortet Projektfragen daraus."
---


# Projektwissen aufbauen und abfragen

Verwende diese Facette, wenn Projektwissen erstellt, nach einer Unterbrechung abgeglichen oder für eine konkrete Frage genutzt werden soll. Erfasse Projekt-ID, ausgewählten Scope, Quellen, Revision, bekannte Lücken und die letzte bestätigte Wissensbasis.

| Lage | Arbeitsmodus |
| --- | --- |
| Erster Stand oder vollständiger Neuaufbau beauftragt | Inventar und Beziehungen aus den tatsächlich verfügbaren Quellen neu erfassen |
| Passender unterbrochener Auftrag | Checkpoint mit frischer Basis vergleichen und offene Quellen fortsetzen |
| Geänderte Revision | Betroffene Dateien, entfernte Einträge, ihre Beziehungen und abhängige Antworten neu prüfen |
| Gleicher belegter Quellumfang und gleiche Revision | Bestehenden Stand wiederverwenden und Befund dokumentieren |
| Unvollständige oder widersprüchliche Quellen | Letzten gültigen Stand als historisch kennzeichnen, Lücken benennen und neue Belege getrennt führen |

Erstelle einen kopierbaren Bericht mit Projektstruktur, Konventionen, Dokumentenindex, Datenübersicht, Medienmetadaten und belegtem Graphen, soweit Material vorliegt. Trenne tatsächlich gelesene Medien von bloßen Dateinamen oder Metadaten. Halte pro Eintrag Pfad, Revision und Beleg fest. Markiere einen partiellen Index als PARTIAL.

Bei einer Projektfrage verwende zuerst [Graph Retrieval](../sceeri-graph-retrieval/SKILL.md). Fällt der Graph aus oder ist er veraltet, nutze belegte Struktur, Konventionen und lesbare Quellen. Gib an, welche Basis die Antwort trägt und was ein neuer Abgleich klären würde. Speichern und Readback werden separat belegt, wenn sie beauftragt und im Host möglich sind.

## Revisionsgebundene Wissensbasis

Ordne Wissensstände einer Projekt-ID und Commit-ID zu. Verwende einen belegten exakten Stand zuerst. Wenn dieser fehlt, nutze einen kompatiblen Vorfahren als historischen Hintergrund und prüfe betroffene Fakten im aktuellen Diff. Ein fremder Branch oder unvollständiger Index bleibt getrennt. Für eine lesende Frage gelten gestagte, ungestagte und ungetrackte Änderungen nur im tatsächlich verfügbaren Umfang. Benenne Lücken.

Bei einem beauftragten Refresh prüfe Scope, Revision und den Zustand der Arbeitskopie. Wähle exakte Wiederverwendung, passenden Resume, inkrementelle Aktualisierung oder Neuaufbau. Behandle Löschungen und betroffene Beziehungen ausdrücklich. Bewahre den letzten nutzbaren Stand bis zur vollständigen Prüfung. Bei wechselndem HEAD wiederhole betroffene Reads vor Abschluss. Der Chat behauptet weder automatische Refreshs noch dauerhafte Pointer-Änderungen ohne beobachteten Nachweis.
