# Vollständigkeitsprüfung v0.17.0 bis v0.27.0

## Ergebnis

Alle zehn gelieferten Versionsarchive wurden vollständig geöffnet, auf ZIP-Integrität geprüft und mit den vorhandenen Release-Dateien bytegenau verglichen. Jede darin enthaltene Skill-ID ist in v0.27.0 vorhanden. Die erneut bereitgestellte ChatGPT Skills Library stimmt bytegenau mit dem bereits in v0.25.0 ausgewerteten Archiv überein. Die [Facettenkarte](facetten.md) enthält alle 28 öffentlichen Werkzeugnamen aus v0.21.0. Die zwölf Quellen sind in der [Herkunft](herkunft.md#chatgpt-skills-library-und-uca-audit) zugeordnet.

| Version | ZIP-Bytes | Dateien | Facetten |
| --- | ---: | ---: | ---: |
| 0.17.0 | 426559 | 128 | 41 |
| 0.18.0 | 428268 | 129 | 42 |
| 0.19.0 | 432064 | 131 | 42 |
| 0.20.0 | 451946 | 138 | 43 |
| 0.21.0 | 458291 | 143 | 48 |
| 0.22.0 | 67059 | 61 | 50 |
| 0.23.0 | 82210 | 77 | 66 |
| 0.24.0 | 87839 | 81 | 70 |
| 0.25.0 | 98291 | 94 | 82 |
| 0.26.0 | 107914 | 102 | 90 |

## Erklärung der Paketgröße

Die Änderung fand zwischen v0.21.0 (458.291 Byte) und v0.22.0 (67.059 Byte) statt. Dabei entfielen 88 bisherige Dateipfade und es kamen sechs hinzu. Drei eingebettete Referenzarchive belegten allein 255.929 komprimierte Bytes. Zusätzlich entfielen MCP-Konfiguration, Python-/Java-/JavaScript-Implementierungen, HTML-Widgets, Testcode und frühere Referenz- und Vorlagendateien. Der Stand mit rund 98 kB ist v0.25.0 (98.291 Byte), bereits nach dem Formatwechsel.

Die Wiederherstellung in v0.27.0 betrifft Arbeitsabläufe und Nachweisregeln. Die alten ZIPs bleiben Referenz für exakten Laufzeitcode, Originaltests und Fixtures. Browser-UI, automatische Ausführung, Host-Anbindungen und dauerhafte Speicherung erfordern tatsächliche Host-Funktionen. Diese Fähigkeiten können im Chat beschrieben, begleitet oder anhand echter Host-Belege geprüft werden. Das Paket enthält keine eigenen ausführbaren Komponenten.

## Nachgetragene Inhalte

- Kopierbare Arbeitsvorlagen und durchgehender mehrsprachiger Handoff-Fall.
- Konsistenzprüfung von Quellständen, Freeze und Recovery, Chat-Workbench-Aktionen, Regelkarte und SCEVI-Statusdarstellung.
- Manuelle Abnahmeszenarien für die noch ausstehende Host-Prüfung.

## Zuordnung der 88 entfallenen Pfade

Die Zuordnung weist den Bezug zum Chat-Ablauf aus. Historische Quelltests und Artefakte gelten nur für die damalige Ausgabe.

| Pfad aus v0.21.0 | Einordnung | Bezug im Chat-Paket |
| --- | --- | --- |
| `mappings.example.json` | Mapping, Branding und Quellprüfung | [Bezug](../skills/sceeri-brand-identity/SKILL.md) |
| `mcp.json` | Werkzeugregistrierung oder Laufzeitvoraussetzung, Zuordnung als Fachablauf | [Bezug](facetten.md) |
| `references/SCEVI_SEMANTIC_VISUAL_INTELLIGENCE_SKILL_R01.zip` | Historisches Original separat | [Bezug](herkunft.md) |
| `references/coding-agent-handoff-r01/00_START_HIER.md` | Übergabe oder Standvergleich | [Bezug](checkpoint.md) |
| `references/coding-agent-handoff-r01/01_AGENT_AUFTRAG.md` | Übergabe oder Standvergleich | [Bezug](checkpoint.md) |
| `references/coding-agent-handoff-r01/02_SCEERI_UND_CODEBAU.md` | Übergabe oder Standvergleich | [Bezug](checkpoint.md) |
| `references/coding-agent-handoff-r01/03_PARALLEL_UND_REHYDRATION.md` | Übergabe oder Standvergleich | [Bezug](checkpoint.md) |
| `references/coding-agent-handoff-r01/04_ABNAHME_UND_VISUELLE_FUEHRUNG.md` | Übergabe oder Standvergleich | [Bezug](checkpoint.md) |
| `references/coding-agent-handoff-r01/05_QUELLEN_UND_READBACK.md` | Übergabe oder Standvergleich | [Bezug](checkpoint.md) |
| `references/coding-agent-handoff-r01/CODING_AGENT_HANDOFF_R01.zip` | Historisches Original separat | [Bezug](herkunft.md) |
| `references/coding-agent-handoff-r01/beispiele/01_PROJEKTAUFTRAG.json` | Übergabe oder Standvergleich | [Bezug](checkpoint.md) |
| `references/coding-agent-handoff-r01/beispiele/02_CHECKPOINT.json` | Übergabe oder Standvergleich | [Bezug](checkpoint.md) |
| `references/coding-agent-handoff-r01/beispiele/03_DURCHGEHENDER_FALL.md` | Übergabe oder Standvergleich | [Bezug](checkpoint.md) |
| `references/parser-workflow.md` | Parser-, Isolations- oder Reparaturablauf | [Bezug](parser-und-repair.md) |
| `references/project-workspaces.md` | Quellzugriff und Scope-Abgleich als Chatablauf | [Bezug](../skills/sceeri-project-workspaces/SKILL.md) |
| `references/provenance-and-licensing.md` | Historische Herkunft und Inventar | [Bezug](herkunft.md) |
| `references/python-workbench.md` | Chat-Workbench, Bedienung hostabhängig | [Bezug](../skills/sceeri-workbench-host-acceptance/SKILL.md) |
| `references/release-verification-v0.6.0.md` | Historischer Test oder Fixture, fachliche Prüffälle als Chat-Abnahme | [Bezug](chat-abnahme.md) |
| `references/scevi-integration.md` | Anzeige und Semantik, Laufzeitrenderer ersetzt | [Bezug](../skills/sceeri-scevi-visual-intelligence/SKILL.md) |
| `references/standalone-projects.md` | Getrennter Vergleich von Basis und Kandidat | [Bezug](../skills/sceeri-local-project-independence/SKILL.md) |
| `references/test-output.txt` | Historischer Test oder Fixture, fachliche Prüffälle als Chat-Abnahme | [Bezug](chat-abnahme.md) |
| `references/tool-facets.md` | Werkzeugregistrierung oder Laufzeitvoraussetzung, Zuordnung als Fachablauf | [Bezug](facetten.md) |
| `references/uca-r02/INTEGRATION_CONTRACT.md` | Historischer Beleg oder lesende Prüflogik | [Bezug](uca-r02-nachweise.md) |
| `references/uca-r02/R02_AUDIT.md` | Historischer Beleg oder lesende Prüflogik | [Bezug](uca-r02-nachweise.md) |
| `references/uca-r02/SHA256SUMS.txt` | Historischer Beleg oder lesende Prüflogik | [Bezug](uca-r02-nachweise.md) |
| `references/uca-r02/UNIVERSAL_CODE_AGENT_R01_DEV_ORIGINAL.zip` | Historisches Original separat | [Bezug](herkunft.md) |
| `references/uca-r02/capabilities.csv` | Historischer Beleg oder lesende Prüflogik | [Bezug](uca-r02-nachweise.md) |
| `references/uploaded-archive-inventory.json` | Historische Herkunft und Inventar | [Bezug](herkunft.md) |
| `runtime/coding_dashboard.html` | Anzeige und Semantik, Laufzeitrenderer ersetzt | [Bezug](../skills/sceeri-scevi-visual-intelligence/SKILL.md) |
| `runtime/coding_dashboard.py` | Anzeige und Semantik, Laufzeitrenderer ersetzt | [Bezug](../skills/sceeri-scevi-visual-intelligence/SKILL.md) |
| `runtime/graph_cli.py` | Quellgraph und Wirkungsprüfung | [Bezug](../skills/sceeri-uca-r02-integration/SKILL.md) |
| `runtime/python_app.py` | Chat-Workbench, Bedienung hostabhängig | [Bezug](../skills/sceeri-workbench-host-acceptance/SKILL.md) |
| `runtime/python_workbench.html` | Chat-Workbench, Bedienung hostabhängig | [Bezug](../skills/sceeri-workbench-host-acceptance/SKILL.md) |
| `runtime/requirements.txt` | Werkzeugregistrierung oder Laufzeitvoraussetzung, Zuordnung als Fachablauf | [Bezug](facetten.md) |
| `runtime/server.py` | Werkzeugregistrierung oder Laufzeitvoraussetzung, Zuordnung als Fachablauf | [Bezug](facetten.md) |
| `runtime/standalone.py` | Getrennter Vergleich von Basis und Kandidat | [Bezug](../skills/sceeri-local-project-independence/SKILL.md) |
| `runtime/uca_r02.py` | Historischer Beleg oder lesende Prüflogik | [Bezug](uca-r02-nachweise.md) |
| `runtime/uca_r04/code_agent/__init__.py` | Quellgraph und Wirkungsprüfung | [Bezug](../skills/sceeri-uca-r02-integration/SKILL.md) |
| `runtime/uca_r04/code_agent/__main__.py` | Quellgraph und Wirkungsprüfung | [Bezug](../skills/sceeri-uca-r02-integration/SKILL.md) |
| `runtime/uca_r04/code_agent/core.py` | Quellgraph und Wirkungsprüfung | [Bezug](../skills/sceeri-uca-r02-integration/SKILL.md) |
| `runtime/uca_r04/code_agent/operations.py` | Quellgraph und Wirkungsprüfung | [Bezug](../skills/sceeri-uca-r02-integration/SKILL.md) |
| `runtime/uca_r04/code_agent/parsers/JavaAstInspector.java` | Quellgraph und Wirkungsprüfung | [Bezug](../skills/sceeri-uca-r02-integration/SKILL.md) |
| `runtime/uca_r04/code_agent/parsers/typescript_ast.cjs` | Quellgraph und Wirkungsprüfung | [Bezug](../skills/sceeri-uca-r02-integration/SKILL.md) |
| `runtime/uca_r04/code_agent/r03_cli.py` | Quellgraph und Wirkungsprüfung | [Bezug](../skills/sceeri-uca-r02-integration/SKILL.md) |
| `runtime/uca_r04/code_agent/r04_cli.py` | Quellgraph und Wirkungsprüfung | [Bezug](../skills/sceeri-uca-r02-integration/SKILL.md) |
| `runtime/uca_r04/code_agent/r04_graph.py` | Quellgraph und Wirkungsprüfung | [Bezug](../skills/sceeri-uca-r02-integration/SKILL.md) |
| `runtime/uca_r04/code_agent/r04_operations.py` | Quellgraph und Wirkungsprüfung | [Bezug](../skills/sceeri-uca-r02-integration/SKILL.md) |
| `runtime/uca_r04/code_agent/source_graph.py` | Quellgraph und Wirkungsprüfung | [Bezug](../skills/sceeri-uca-r02-integration/SKILL.md) |
| `schemas/handoff.schema.json` | Übergabe oder Standvergleich | [Bezug](checkpoint.md) |
| `skills/sceeri-scevi-visual-intelligence/assets/theme.json` | Anzeige und Semantik, Laufzeitrenderer ersetzt | [Bezug](../skills/sceeri-scevi-visual-intelligence/SKILL.md) |
| `templates/ai-coding/.cursor/rules/sceeri-governance.mdc` | Textvorlage | [Bezug](chat-arbeitsvorlagen.md) |
| `templates/ai-coding/.github/copilot-instructions.md` | Textvorlage | [Bezug](chat-arbeitsvorlagen.md) |
| `templates/ai-coding/AGENTS.md` | Textvorlage | [Bezug](chat-arbeitsvorlagen.md) |
| `templates/ai-coding/BUGFIX_PROMPT.md` | Textvorlage | [Bezug](chat-arbeitsvorlagen.md) |
| `templates/ai-coding/CLAUDE.md` | Textvorlage | [Bezug](chat-arbeitsvorlagen.md) |
| `templates/ai-coding/FEATURE_PROMPT.md` | Textvorlage | [Bezug](chat-arbeitsvorlagen.md) |
| `templates/ai-coding/FIVE_FIELD_PROMPT.md` | Textvorlage | [Bezug](chat-arbeitsvorlagen.md) |
| `templates/ai-coding/REFACTOR_PROMPT.md` | Textvorlage | [Bezug](chat-arbeitsvorlagen.md) |
| `templates/ai-coding/TEST_PROMPT.md` | Textvorlage | [Bezug](chat-arbeitsvorlagen.md) |
| `templates/ai-coding/TOOL_COMPATIBILITY.md` | Textvorlage | [Bezug](chat-arbeitsvorlagen.md) |
| `templates/ai-coding/UI_PROMPT.md` | Textvorlage | [Bezug](chat-arbeitsvorlagen.md) |
| `templates/linguistic/rules.example.json` | Regelmodell und Chat-Simulation | [Bezug](../skills/sceeri-linguistic-programming/SKILL.md) |
| `templates/python_module.py` | Textvorlage | [Bezug](chat-arbeitsvorlagen.md) |
| `tests/fixtures/sample.html` | Historischer Test oder Fixture, fachliche Prüffälle als Chat-Abnahme | [Bezug](chat-abnahme.md) |
| `tests/fixtures/sample.java` | Historischer Test oder Fixture, fachliche Prüffälle als Chat-Abnahme | [Bezug](chat-abnahme.md) |
| `tests/test_code_assistant_v04.py` | Historischer Test oder Fixture, fachliche Prüffälle als Chat-Abnahme | [Bezug](chat-abnahme.md) |
| `tests/test_engineering.py` | Historischer Test oder Fixture, fachliche Prüffälle als Chat-Abnahme | [Bezug](chat-abnahme.md) |
| `tests/test_engineering_v06.py` | Historischer Test oder Fixture, fachliche Prüffälle als Chat-Abnahme | [Bezug](chat-abnahme.md) |
| `tests/test_handoff_v08.py` | Historischer Test oder Fixture, fachliche Prüffälle als Chat-Abnahme | [Bezug](chat-abnahme.md) |
| `tests/test_mcp_v010.py` | Historischer Test oder Fixture, fachliche Prüffälle als Chat-Abnahme | [Bezug](chat-abnahme.md) |
| `tests/test_multilang_v05.py` | Historischer Test oder Fixture, fachliche Prüffälle als Chat-Abnahme | [Bezug](chat-abnahme.md) |
| `tests/test_package.py` | Historischer Test oder Fixture, fachliche Prüffälle als Chat-Abnahme | [Bezug](chat-abnahme.md) |
| `tests/test_prompt_package.py` | Historischer Test oder Fixture, fachliche Prüffälle als Chat-Abnahme | [Bezug](chat-abnahme.md) |
| `tests/test_scevi_linguistic_v07.py` | Historischer Test oder Fixture, fachliche Prüffälle als Chat-Abnahme | [Bezug](chat-abnahme.md) |
| `tests/test_workspace_v09.py` | Historischer Test oder Fixture, fachliche Prüffälle als Chat-Abnahme | [Bezug](chat-abnahme.md) |
| `tools/engineering/JavaAudit.java` | Parser-, Isolations- oder Reparaturablauf | [Bezug](parser-und-repair.md) |
| `tools/engineering/html_tree.py` | Parser-, Isolations- oder Reparaturablauf | [Bezug](parser-und-repair.md) |
| `tools/engineering/isolation.py` | Parser-, Isolations- oder Reparaturablauf | [Bezug](parser-und-repair.md) |
| `tools/engineering/javascript.cjs` | Parser-, Isolations- oder Reparaturablauf | [Bezug](parser-und-repair.md) |
| `tools/engineering/parsers.py` | Parser-, Isolations- oder Reparaturablauf | [Bezug](parser-und-repair.md) |
| `tools/engineering/workflow.py` | Parser-, Isolations- oder Reparaturablauf | [Bezug](parser-und-repair.md) |
| `tools/sceeri_code.py` | Mapping, Branding und Quellprüfung | [Bezug](../skills/sceeri-brand-identity/SKILL.md) |
| `tools/sceeri_dashboard.py` | Anzeige und Semantik, Laufzeitrenderer ersetzt | [Bezug](../skills/sceeri-scevi-visual-intelligence/SKILL.md) |
| `tools/sceeri_engineering.py` | Parser-, Isolations- oder Reparaturablauf | [Bezug](parser-und-repair.md) |
| `tools/sceeri_handoff.py` | Übergabe oder Standvergleich | [Bezug](checkpoint.md) |
| `tools/sceeri_multilang_audit.py` | Sprachinventar und Abdeckungsgrenzen | [Bezug](../skills/sceeri-code-engineering/SKILL.md) |
| `tools/sceeri_rules.py` | Regelmodell und Chat-Simulation | [Bezug](../skills/sceeri-linguistic-programming/SKILL.md) |
| `tools/sceeri_workspace.py` | Quellzugriff und Scope-Abgleich als Chatablauf | [Bezug](../skills/sceeri-project-workspaces/SKILL.md) |
