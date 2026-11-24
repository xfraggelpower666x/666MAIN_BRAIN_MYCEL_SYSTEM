---
name: sceeri-uca-r02-integration
description: "Überträgt R02-Prüfprinzipien in eigenständige Projekte mit Quellgraph, Impact, Patch-Abnahme, Recovery und getrennten Nachweisen."
---

# Universal Code Agent R02

1. Ermittle Projekt, Quellstand und Umfang. Prüfe Adapterbelege über [Integrationsabnahme](../sceeri-provider-integration-acceptance/SKILL.md).
2. Erstelle aus gelesenen Quellen einen Abhängigkeitsgraphen mit Datei, Symbol, Aufruf, Import, API, Event, Datenvertrag oder Bridge. Vermerke Fundstelle, Quellstand und Evidenz je Kante. Zeige von der geplanten Änderung erreichbare Verbraucher und Regressionen. Markiere dynamisch aufgelöste Abhängigkeiten und vermutete Kanten.
3. Prüfe Patch-Kandidaten in drei Ebenen. Struktur prüft Schnittstellen und Syntax, kausal-semantische Prüfung prüft Soll, Ist und betroffene Verträge, Recovery prüft Basis, Rückkehranker und Wiederanlauf.
4. Plane unabhängige Prüfungen derselben Basis. Bei Unterbrechung erhalte bestätigte Belege, offene Arbeit und nächste Schritte. Vergleiche vor Fortsetzung die frische Basis mit dem [Checkpoint-Vertrag](../../references/checkpoint.md).
5. Berichte Quelle, CI, Lieferung, Übernahme und Zielhost getrennt. Erfasse Testbelege je konkretem Lauf. Ein gelieferter Patch kann unabhängig von seiner Übernahme verifiziert sein.

Übertragene Prinzipien sind CodeForge-Impact, lesende SuperCodeForge-Mediation, CLIC-Checkpoints, MAIN-BRAIN-Abhängigkeiten und 666STREAM-Artefakt-Readback. Die historische Herkunft vermittelt keine fremde Ausführungsautorität.

Für gezielte Fragen an einen vorhandenen Graphen verwende [Graph Retrieval](../sceeri-graph-retrieval/SKILL.md). Zum Abgleichen der Graphbasis verwende [Projektwissen](../sceeri-knowledge-layer/SKILL.md).

## Historischer R02-Quellstand

Verwende die [R02-Nachweisübersicht](../../references/uca-r02-nachweise.md) zur Einordnung der historischen Befunde. Für neue Aussagen über einen Zielhost sind aktuelle, unabhängige Belege erforderlich.
