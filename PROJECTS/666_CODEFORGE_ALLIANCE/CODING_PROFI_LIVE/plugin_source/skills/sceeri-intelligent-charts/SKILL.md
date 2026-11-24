---
name: sceeri-intelligent-charts
description: Erstellt datengetreue Charts für Vergleiche, Verläufe, Zusammenhänge und Anteile und macht Quell-, Einheiten- und Datenlücken sichtbar.
---

# Intelligent Charts

Öffne `L.Y.V.R.A. CODING PROFI — INTELLIGENT CHARTS` mit dem Modus `charts` der [Intelligent UI](../sceeri-visual-intelligent-ui/SKILL.md). Übernimm belegte Zahlen samt Zeilenbezeichnung, Einheit, Quelle und gegebenenfalls Revision. Werte aus einem Screenshot sind nur dann Zahlenwerte, wenn sie ablesbar sind. Schematische Kurven bleiben qualitativ. Eine genannte Quelle gilt bis zum Readback als Quellangabe.

- Vergleich in Kategorien → Balken mit Nullbezug. Behalte Vorzeichen und Einheiten.
- Verlauf → Linie in der bekannten Eingabereihenfolge. Markiere Auslassungen als Lücken. Bei ungleichen Zeitabständen, die relevant sind, verwende einen Renderer mit proportionaler Zeitachse oder gib den Abstand in der begleitenden Tabelle an.
- Zusammenhang → Streudiagramm mit numerischen X- und Y-Werten. Eine Korrelation liefert eine prüfbare Hypothese.
- Anteile → Anteilsbalken auf Basis einer vollständigen positiven Summe nichtnegativer Werte. Bei offener Summe bleibt die Wertetabelle sichtbar.

Das [Datenformat](../sceeri-visual-intelligent-ui/references/ui-contract.md#optionale-begleitdaten) kann bis zu 40 Zeilen direkt an die UI geben. Bei größerem Umfang, mehreren Reihen oder proportionaler Zeitachse nutze das geeignete Host-Chart oder die projektseitige Visualisierung mit passender Skala. Kein automatisches Füllen, Abschneiden oder Erfinden. Chart- und Textausgabe verwenden dieselbe belegte Datenbasis. Bei falscher Einheit oder widersprüchlicher Quelle frage nach der kleinsten Gegenprobe und aktualisiere die Darstellung danach.
