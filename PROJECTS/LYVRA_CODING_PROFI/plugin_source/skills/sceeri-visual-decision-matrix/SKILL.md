---
name: sceeri-visual-decision-matrix
description: "Use for Decision Matrix visuals in L.Y.V.R.A. CODING PROFI: Optionen nach benannten Kriterien und ausschließlich belegten Werten vergleichen."
---

# Decision Matrix

Nutze diesen Skill, wenn eine Decision Matrix-Darstellung verlangt wird. Zweck: Optionen nach benannten Kriterien und ausschließlich belegten Werten vergleichen. Zielverhältnis: 16:9.

## Ablauf
1. Übernimm nur vom Nutzer genannte oder aus der aktuellen Quelle nachgewiesene Inhalte. Fehlende Eingaben bleiben offen; ein Platzhalter ist keine Behauptung.
2. Layout: Spalten sind die drei Optionen, Zeilen die drei Kriterien. Jede Zelle enthält nur einen gelieferten Wert oder exakt „offen“. Bewertungsmaßstab, Gewichtung und Sieger nur zeigen, falls vom Nutzer geliefert.
3. Erzeuge das visuelle Ergebnis in der unterstützten Ausgabeform. Gib bei einem reinen Promptauftrag die Vorlage zum Ausfüllen oder mit belegten Werten ausgefüllt zurück.
4. Abnahme: Gleiche jede Zelle mit der Eingabe ab; fehlende Werte nicht schätzen, aus Nachbarzellen ableiten oder als Null behandeln.

## Kopierbare Vorlage

> Erstelle eine Entscheidungsmatrix für [Zielgruppe]. Vergleiche [Option A], [Option B] und [Option C] nach [Kriterium 1], [Kriterium 2] und [Kriterium 3]. Nutze nur meine Angaben. Markiere fehlende Werte mit „offen“. Format: 16:9.

## Gemeinsamer Arbeitsvertrag
- Nutze [visuelle Evidenz und Formate](../../references/visual-formats.md): erfasse Quelle, Inhalt, Lücken und Status vor dem Zeichnen. Wende bei Coding-Profi-Berichten zusätzlich den [SCEVI-Vertrag](../../references/scevi-visual-contract.md) an.
- Gib die passende Grafik direkt in einem vom Host unterstützten Format aus. Für präzise Beschriftung, Raster oder Pfeile nutze Markdown/Mermaid oder eine kontrolliert erzeugte Vektorgrafik. Für handschriftliche Wirkung darf eine Bildgenerierung verwendet werden; prüfe danach Text und inhaltliche Übereinstimmung. Ein bloßer Prompt ist nur dann das Ergebnis, wenn der Nutzer ausdrücklich einen Prompt verlangt.
- Liefere eine kurze Textalternative mit demselben Inhalt und nenne offene Daten, Quellenbezug und tatsächliche Prüfung. Farbe allein trägt keine Bedeutung; Sprache standardmäßig Deutsch, sofern der Nutzer nichts anderes wünscht.

