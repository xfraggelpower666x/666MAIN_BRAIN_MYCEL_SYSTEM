---
name: sceeri-graph-retrieval
description: "Beantwortet Projektfragen mit einem belegten Teilgraphen, semantischen Tripeln, Fundstellen und sichtbaren Abdeckungslücken."
---


# Graph Retrieval

1. Kläre Frage, Projekt, Quellstand und zulässigen Umfang. Nutze gelieferte Knoten und Kanten, exportierte Graphdaten oder direkt gelesene Quellen. Bei fehlender Frage oder Graphbasis benenne die Lücke und nutze gegebenenfalls [Projektwissen](../sceeri-knowledge-layer/SKILL.md) als Rückfallweg.
2. Suche Startknoten anhand von Symbolen, Pfaden, Synonymen und Bezeichnern aus der Frage. Behandle Treffer als Kandidaten. Verfolge relevante Beziehungen mit expliziter Richtung und vermeide Wiederholungen in Zyklen. Zwei Beziehungsschritte sind der Standard. Begründe eine Erweiterung und halte das Ergebnis auf die Frage begrenzt.
3. Prüfe jede verwendete Kante gegen Quellstelle oder vorliegenden Graphbeleg. Gleiche widersprüchliche Identitäten und Kanten über Pfad, Symbol, Relation und Revision ab. Kennzeichne fehlende Endpunkte und dynamische Auflösung. Ein thematischer Treffer begründet keine Abhängigkeit.
4. Liefere Antwort, Tripel aus Subjekt, Relation und Objekt, die entscheidenden Knoten und Kanten sowie Evidenz je Pfad. Übernimm Retrieval-ID und Ursprung, wenn belegt, und markiere gekürzte Ergebnisse oder fehlende Belege. Für Änderungsfolgen verknüpfe bestätigte Kanten mit [Impact und Abnahme](../sceeri-uca-r02-integration/SKILL.md).

## Sprachübergreifende Abdeckung

Notiere je Datei Sprache, Paket oder Modul, Symbole, Importart, Einstieg und Testbezug. Behandle Go-Module, Python-Imports sowie statische, dynamische und CommonJS-Referenzen in JS/TS nach ihren jeweiligen Regeln. Unterscheide Parser, Heuristik, generischen Fallback und Parse-Fehler. Weise offene Typ- und sprachübergreifende Symbolauflösung ausdrücklich aus. Für einen messbaren Vergleich nutze [Graph-Benchmark](../sceeri-graph-benchmark/SKILL.md).
