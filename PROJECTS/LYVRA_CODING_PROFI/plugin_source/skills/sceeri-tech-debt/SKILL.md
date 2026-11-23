---
name: sceeri-tech-debt
description: "Erfasst und priorisiert belegte technische Schulden in Code, Architektur, Tests, Abhängigkeiten, Dokumentation und Betrieb."
---

# Technische Schulden

1. Erfasse pro Befund Fundstelle, beobachtete Reibung, betroffene Abläufe, Risiko beim Aufschub und kleinstes sinnvolles Arbeitspaket.
2. Schätze Auswirkung, Risiko und Aufwand jeweils von 1 bis 5 und begründe sie. Ein möglicher Prioritätswert ist `(Auswirkung + Risiko) × (6 − Aufwand)`. Dokumentiere bei fehlender Evidenz eine offene Schätzung. Akute Störungen oder verbindliche Fristen zuerst behandeln.
3. Ordne Befunde zu Arbeitspaketen mit Abhängigkeiten und messbarer Abnahme. Beispiele sind weniger Abfragen pro Request, weniger flüchtige Testfehler oder kürzere Recovery-Zeit. Bei Leistungsangaben Messbedingungen festhalten.
4. Liefere eine priorisierte Liste mit Aufwand, Nutzen, Beleg und nächster Aktion. Für gezielte Reparaturen verwende den [bestehenden Review-Ablauf](../sceeri-code-review-and-refactor/SKILL.md).
