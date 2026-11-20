---
name: psyllo-coding-workbench
description: Erstellt die PSYLLO-Coding-Workbench mit belegten Projektaktionen, Visualformen, Charts und projektneutralem UI-Export.
---

# PSYLLO Coding Workbench

Bei `666 MAIN BRAIN CODING — WORKBENCH` nutze im bereits bestätigten Coding-Projekt die aktuelle Basis, vorhandene Belege und die nächste fachlich zulässige Aktion. Aus einem reinen UI-Aufruf folgt keine Freigabe. Ohne Projekt zeige den offenen Stand.

Erzeuge die Oberfläche mit `python scripts/render_ui.py projekt.json workbench.html --standalone`. Der lokale Executor braucht Python 3.10 oder höher. [Datenvertrag](references/ui-contract.md) und [Vorlage](template/README.md) dokumentieren Formfelder, Charts, Aktionen und Grenzen. Für ein neues Zielprojekt erzeuge die neutrale Vorlage über `python scripts/export_template.py <neuer-ordner>`. Weise eine nicht beobachtete ChatGPT-Host-Interaktion als offen aus.

UI-Handoffs können Modus, Ansicht und Visualform übernehmen. LiveCircle prüft vorher Projekt und Revision. Danach kann der Renderer einen kompatiblen Handoff mit `--checkpoint` lesen. Fachliche Pflichten, Projektzustand und Schreibfreigaben stammen weiterhin aus dem nativen Projektablauf.

## MYCEL R02 · native MAIN-BRAIN-Menü-/Guidance-Bridge

Für das verifizierte MAIN-BRAIN-Projekt verwendet das native MYCEL-Menü ergänzend [mycel_bridge.py](scripts/mycel_bridge.py) und die [R02-Einbauanleitung](README_MYCEL_R02.md). Der Adapter übersetzt sechs MYCEL-Ansichten sowie gebundene Guidance-State-Felder ins bestehende Workbench-JSON. Er ersetzt `render_ui.py` nicht. Projekt, Git-Revision und optionale Lineage sind vor jeder View-Wiederherstellung zwingend direkt zu prüfen. Das neue Schema `psyllo.ui-handoff.1` ist *nicht* der alte Renderer-Checkpoint `scevi.visual.handoff.1`. Kein automatischer Host-, GitHub- oder Fremdsystem-Write.
