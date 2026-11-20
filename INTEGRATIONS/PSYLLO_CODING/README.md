# PSYLLO Coding · Projektgebundene Prüfungen und Workbench

Die ergänzten Werkzeuge laufen im Coding-Projekt. Der native Whole-LiveCircle und seine System-Trigger verwenden weiterhin die vorhandenen Verträge.

| Werkzeug | Normaler Einstieg | Abnahme |
| --- | --- | --- |
| Git-Checkpoint | `python checkpoint/scripts/checkpoint_review.py checkpoint.json binding.json --git-repo <verifizierter-checkout> --include-worktree` | Commit-Abstammung, Index, Arbeitsbaum, ungetrackte Pfade und Konflikte |
| Laufbelege | `python run/scripts/check_run_evidence.py vertrag.json receipt.json artefakte/` | Unabhängiges Soll gegen Ergebniscommit, Status und tatsächliche SHA-256-Artefakte |
| Workbench | `python workbench/scripts/render_ui.py workbench/template/view.example.json workbench.html --standalone` | Projektansichten, Visualformen, Charts, abhängige Aktionsvorschläge und Daemon |

Software-Voraussetzung ist Python 3.10 oder höher. Der Git-Prüfer braucht einen verfügbaren, bereits geprüften Git-Checkout. In reinem Remote-Kontext macht er keine Aussagen zum lokalen Arbeitsbaum. Bindung und Checkpoint stammen aus getrennten Quellen. Bei unklarem Write erfolgt zuerst Ziel-Readback. Der Agentenlaufprüfer überprüft vorhandene Belege und startet keinen Agenten. Workbench-Ausgaben geben keine Ausführungsfreigabe.

Herkunft der allgemeinen Mechanik: Coding Profi 0.87.0. Die beigefügte UI-Vorlage 0.85.1 belegt den Ausgangspunkt des neutralen Renderers. Die geprüften neueren UI-Dateien erhalten die exakte Wiederaufnahme einer Form. Native Namen und Aufrufwege sind PSYLLO-spezifisch.

Lokale Regressionen mit `python -m unittest discover -s checkpoint/tests`, `python -m unittest discover -s run/tests` und `python -m unittest discover -s workbench/tests`. Fresh-Chat- und interaktive Host-Abnahme bleiben separat.
