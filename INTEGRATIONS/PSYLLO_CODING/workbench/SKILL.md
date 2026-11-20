---
name: psyllo-coding-workbench
description: Erstellt die PSYLLO-Coding-Workbench mit belegten Projektaktionen, Visualformen, Charts und projektneutralem UI-Export.
---

# PSYLLO Coding Workbench

Bei `666 MAIN BRAIN CODING — WORKBENCH` nutze im bereits bestätigten Coding-Projekt die aktuelle Basis, vorhandene Belege und die nächste fachlich zulässige Aktion. Aus einem reinen UI-Aufruf folgt keine Freigabe. Ohne Projekt zeige den offenen Stand.

Erzeuge die Oberfläche mit `python scripts/render_ui.py projekt.json workbench.html --standalone`. Der lokale Executor braucht Python 3.10 oder höher. [Datenvertrag](references/ui-contract.md) und [Vorlage](template/README.md) dokumentieren Formfelder, Charts, Aktionen und Grenzen. Für ein neues Zielprojekt erzeuge die neutrale Vorlage über `python scripts/export_template.py <neuer-ordner>`. Weise eine nicht beobachtete ChatGPT-Host-Interaktion als offen aus.

UI-Handoffs können Modus, Ansicht und Visualform übernehmen. LiveCircle prüft vorher Projekt und Revision. Danach kann der Renderer einen kompatiblen Handoff mit `--checkpoint` lesen. Fachliche Pflichten, Projektzustand und Schreibfreigaben stammen weiterhin aus dem nativen Projektablauf.
