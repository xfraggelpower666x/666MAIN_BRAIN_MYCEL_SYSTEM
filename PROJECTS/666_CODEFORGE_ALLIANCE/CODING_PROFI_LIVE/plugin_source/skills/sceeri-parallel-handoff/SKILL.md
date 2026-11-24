---
name: sceeri-parallel-handoff
description: Plan parallel engineering strands, handle interruptions and rehydrate portable Coding Agent Handoff checkpoints within an explicitly selected project.
---

# Parallel Deployment und Wiederaufnahme

Nutze diese Facette für einen Handoff, Parallelplan oder Wiederaufnahme. Beginne mit Zielprojekt, Scope und verifiziertem Quellstand.

1. Wähle die nötigen Stränge aus Architektur, Linguistik, Fachcode, Schnittstellen, Regression und Kontinuität. Erhebe Abhängigkeiten, tatsächliche Lese- und Schreibbereiche und gemeinsame Verträge.
2. Gruppiere bereite Stränge in Wellen nach Abhängigkeiten und Lese- oder Schreibbereichen. Prüfe Aliase, Symlinks, gemeinsame Schnittstellen und Referenzen. Serialisiere konkurrierende Änderungen. Die Welle bleibt ein Plan, bis tatsächliche Aufrufe belegt sind.
3. Bei Unterbrechung sichere verifizierte Evidenz, offene Pflichten und Rückkehranker. Kläre ungewisse Schreibausgänge per direktem Readback. Lies bei Wiederaufnahme Current unabhängig und prüfe die Herkunft der Receipts.
4. Isoliere konfliktbetroffene Stränge. Führe bereite unabhängige Arbeit mit tatsächlich verfügbaren Werkzeugen fort. Melde ausgeführte Arbeit anhand beobachteter Belege.
5. Dokumentiere je Strang Status, Quellbezug, Ergebnis, nächste Aktion und Rückkehranker. Weise Quelle, lokalen Test und CI, Lieferung, Übernahme und Host jeweils getrennt aus.

Bei Unterbrechung liefere einen kopierbaren Handoff. Prüfe vor Wiederaufnahme Projekt-ID, aktuelle Basis, vorhandene Belege und offene Schreibausgänge.

Für einen verbundenen Produkt-, Architektur- und Umsetzungshandoff nutze [Plan & Ship](../../references/produktplanung-und-engineering-handoff.md#plan--ship). Verwende vorhandene Quellrevisionen und Zuständigkeiten.

Verwende vor der Wiederaufnahme den [fachlichen Checkpoint-Abgleich](../../references/checkpoint.md#fachliche-prüfung-vor-der-wiederaufnahme). Wenn LiveCircle den Checkpoint im selben Turn bereits geprüft hat, nutze dessen Ergebnis und prüfe nur zusätzlich betroffene Fachbelege.

Führe je Strang die belegte Basis, Abhängigkeitsbarriere, letzte Nebenwirkung und den nächsten Rückkehranker. Übernimm ein Fertigsignal erst mit konkreter Quellrevision und zum Ergebnis passendem Ausführungs- oder Readback-Beleg. Nutze [Wiederaufnahme und Konflikte](../../references/coding-workflows.md#wiederaufnahme-und-konflikte) für Methodenwechsel und betroffene Nachweise.

Für neue Projekte und getrennte Stränge benutze die [Projekt- und Linienregeln](../../references/coding-profi-development.md). Entscheide anhand disponibler Ausführung und konfliktfreier Pfade. In einer Git-Arbeitskopie trenne parallele Writes bei Bedarf mittels separater Worktrees und eigener Arbeitsbranches. Wenn der Host nur einen Strang sicher schreiben kann, arbeite sequenziell und zeige dies als solche Ausführung. Cross-Projekt-Integration ist ein eigener Auftrag.
