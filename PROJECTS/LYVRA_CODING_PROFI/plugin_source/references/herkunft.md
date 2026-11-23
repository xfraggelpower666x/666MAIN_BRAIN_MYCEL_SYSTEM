# Herkunft der Fachabläufe

Die drei Archive wurden als Referenz für eigenständig formulierte Anleitungen ausgewertet. Die Abläufe verwenden ausschließlich Daten und belegte Funktionen des gewählten Chats.

- **ultrathinker** · Temporal Semantics Guardian-0.3.0-v1(1).zip · Zeitsemantik und DST-Grenzfälle → [Chat-Facette](../skills/sceeri-temporal-semantics/SKILL.md). SHA-256 des Eingangsarchivs: `eadaaeb53387fcfa274445ea3591e02338a6e9775289a705cef85887ecfa5085`.
- **PromptGuard** · PromptGuard-1.4.0-v1(1).zip · LLM-Vertrauensgrenzen, Redaktion und Schutzverhalten → [Chat-Facette](../skills/sceeri-prompt-safety/SKILL.md). SHA-256 des Eingangsarchivs: `dc8e93b8653aa8a1cc3afda0d9339eb2dbff32fadcb20977b4c054913e5d93d8`.
- **AI Developer Productivity Dashboard** · AI-Developer-Productivity-main(1).zip · Datenaufbereitung, Kennzahlen und Chatberichte → [Chat-Facette](../skills/sceeri-developer-productivity/SKILL.md). SHA-256 des Eingangsarchivs: `c7c9bc4c588bc4938ca86ca3e948615d27f58a2ce38e8740f45cf6251d34a667`.

Historische Prinzipien aus SCEVI, Coding Agent Handoff R01, UCA R02/R04 und den Engineering-Workflows von Anthropic sind in den entsprechenden Facetten dokumentiert. Das Referenzmaterial verleiht keine Ausführungs- oder Schreibrechte.

## Python-Service-Vorlagen und RepoBrain-Projektstart

Die mitgelieferten Anleitungen und das Initialisierungsskript wurden als Fachquellen für die folgenden Chatabläufe ausgewertet.

| Gelieferte Vorlage | Chat-Facette |
| --- | --- |
| background-jobs-boundaries | [sceeri-background-jobs-boundaries](../skills/sceeri-background-jobs-boundaries/SKILL.md) |
| click-cli | [sceeri-click-cli](../skills/sceeri-click-cli/SKILL.md) |
| click-cli-linter | [sceeri-click-cli-review](../skills/sceeri-click-cli-review/SKILL.md) |
| code-quality | [sceeri-code-quality](../skills/sceeri-code-quality/SKILL.md) |
| dockerize-service | [sceeri-dockerize-service](../skills/sceeri-dockerize-service/SKILL.md) |
| fastapi-errors | [sceeri-fastapi-errors](../skills/sceeri-fastapi-errors/SKILL.md) |
| fastapi-init | [sceeri-fastapi-init](../skills/sceeri-fastapi-init/SKILL.md) |
| http-client-integration | [sceeri-http-client-integration](../skills/sceeri-http-client-integration/SKILL.md) |
| implementation-protocol | [sceeri-code-engineering](../skills/sceeri-code-engineering/SKILL.md) |
| pydantic-schemas | [sceeri-pydantic-schemas](../skills/sceeri-pydantic-schemas/SKILL.md) |
| pytest-service | [sceeri-pytest-service](../skills/sceeri-pytest-service/SKILL.md) |
| request-correlation | [sceeri-request-correlation](../skills/sceeri-request-correlation/SKILL.md) |
| settings-config | [sceeri-settings-config](../skills/sceeri-settings-config/SKILL.md) |
| sqlalchemy-models | [sceeri-sqlalchemy-models](../skills/sceeri-sqlalchemy-models/SKILL.md) |
| uv | [sceeri-uv](../skills/sceeri-uv/SKILL.md) |
| alembic-migrations | [sceeri-alembic-migrations](../skills/sceeri-alembic-migrations/SKILL.md) |
| temporal-review | [sceeri-temporal-semantics](../skills/sceeri-temporal-semantics/SKILL.md) |
| agent-repo-init | [sceeri-agent-repo-init](../skills/sceeri-agent-repo-init/SKILL.md) |
| init_project.py | [Quick-/Full-Projektstart](../skills/sceeri-agent-repo-init/SKILL.md) |

## RepoBrain und OpenSpec

| Eingangsdatei | Übernommener Gegenstand | Facette |
| --- | --- | --- |
| SKILL (6)(2).md | Repo-Initialisierung | [agent-repo-init](../skills/sceeri-agent-repo-init/SKILL.md) |
| tools (7).py | Initialisierungsoptionen und Ergebnis | [agent-repo-init](../skills/sceeri-agent-repo-init/SKILL.md) |
| agent_repo_init_core.py | Quick-/Full-Vertrag und Zielfestlegung | [agent-repo-init](../skills/sceeri-agent-repo-init/SKILL.md) |
| SKILL (1)(2).md | Wissensschicht | [knowledge-layer](../skills/sceeri-knowledge-layer/SKILL.md) |
| tools (3).py | Aktualisierung und lesende Abfrage | [knowledge-layer](../skills/sceeri-knowledge-layer/SKILL.md) |
| __init__ (2).py | Paketmarker der Wissensschicht | [knowledge-layer](../skills/sceeri-knowledge-layer/SKILL.md) |
| SKILL(4).md | Graph Retrieval | [graph-retrieval](../skills/sceeri-graph-retrieval/SKILL.md) |
| tools.py | Abfrage, Teilgraph und Herkunft | [graph-retrieval](../skills/sceeri-graph-retrieval/SKILL.md) |
| __init__.py | Paketmarker der Graph-Funktion | [graph-retrieval](../skills/sceeri-graph-retrieval/SKILL.md) |
| loader.py | Facetten-Erkennung und Routing | [code-assistant](../skills/sceeri-code-assistant/SKILL.md) |
| SKILL (4)(2).md | Rechercheanforderung | [research](../skills/sceeri-research/SKILL.md) |
| tools (5).py | Simulationsgrenze | [research](../skills/sceeri-research/SKILL.md) |
| openspec-proposal.md | Vorschlag | [openspec-change-lifecycle](../skills/sceeri-openspec-change-lifecycle/SKILL.md) |
| openspec-apply.md | Umsetzung | [openspec-change-lifecycle](../skills/sceeri-openspec-change-lifecycle/SKILL.md) |
| openspec-archive.md | Archivierung | [openspec-change-lifecycle](../skills/sceeri-openspec-change-lifecycle/SKILL.md) |

## ChatGPT Skills Library und UCA-Audit

Die zwölf Fachabläufe aus `chatgpt-skills-main.zip` wurden eigenständig als Textanleitungen formuliert. Archiv SHA-256: `848a2c669a78a6548a0a74af012ad0efdb00dc49f976159b34cf44dcdedccfb0`.

| Quellfacette | Chat-Facette |
| --- | --- |
| crypto-ta-analyzer | [Marktindikatoren aus OHLCV-Daten](../skills/sceeri-marktindikatoren/SKILL.md) |
| data-storyteller | [Datenanalyse, Statistik und Berichte](../skills/sceeri-datenanalyse/SKILL.md) |
| document-converter-suite | [Dokumentkonvertierung und PDF-Operationen](../skills/sceeri-dokumentkonvertierung/SKILL.md) |
| financial-calculator | [Finanzmathematik und Szenarien](../skills/sceeri-finanzmodellierung/SKILL.md) |
| geo-toolkit | [Geodaten und Karten](../skills/sceeri-geodaten/SKILL.md) |
| image-enhancement-suite | [Bildbearbeitung und Bildprüfung](../skills/sceeri-bildbearbeitung/SKILL.md) |
| mcp-builder | [MCP-Schnittstellen für Zielprojekte entwerfen](../skills/sceeri-mcp-entwurf/SKILL.md) |
| media-toolkit | [Audio- und Videobearbeitung](../skills/sceeri-medienbearbeitung/SKILL.md) |
| ocr-document-processor | [OCR und strukturierte Extraktion](../skills/sceeri-ocr/SKILL.md) |
| qr-code-generator | [QR-Codes und Druckabnahme](../skills/sceeri-qr-code/SKILL.md) |
| skill-creator | [Chat-Facetten entwerfen und prüfen](../skills/sceeri-facetten-entwurf/SKILL.md) |
| svg-precision-skill | [SVG-Geometrie und technische Vektorgrafiken](../skills/sceeri-svg-praezision/SKILL.md) |

Das [UCA-R02-Audit](uca-r02-nachweise.md) ergänzt die Herkunft und den Evidenzstand des vorhandenen UCA-Ablaufs.

## RepoBrain, OpenCode und weitere Fachquellen

| Archiv | Verwendete Inhalte | SHA-256 |
| --- | --- | --- |
| python-analise-chatgpt-assistente-main.zip | Verkaufsdaten und Datenschema | 5e6dcba9b67e6fdc5e957844b3bc9aac17814a3f9aa4ff30b6ee6876b99b877f |
| virtual-assistent-in-python-main.zip | Sprachpipeline und Rückfallpfade | 7971fce88dcef26f17810301a86191d5509b8b924bc3519ec619e9098b214c65 |
| opencode-dev.zip | Agent-Diagnose, Teststabilität, RTL und Effect; gezielte Auswertung der Entwicklungsskills | 69d2cdb197a38063044cd9c0beac799c1b5b08b72b4668483207c1d9fe44f7b0 |
| ai-coding-best-practices-main.zip | Sprachprofile, Java/Python/Web und Mermaid | 31bd31745a66882bfc052eff57893e5c487602c16bcc9be7c3b3a881c9be2619 |
| repobrain-0.3.1(1).zip | Basisvergleich, Sprachadapter und Wissensmodell | 3c3c9e36caffb79661a5b81019d26ee9ce04051588cb8fb7a23ae42b6816eeb9 |
| repobrain-main(1).zip | Revisionsbindung, inkrementeller Refresh und Benchmark-Methodik | 1b1e4344f85f7742d5d96d297aac212b286358d7cb735354b236a6596ad7ef1b |

RepoBrain: nach Entfernung des äußeren Verzeichnisnamens enthält der gelieferte Main-Snapshot 356 Dateien, der Stand 0.3.1 enthält 276. Main enthält 80 zusätzliche Dateien und 72 gemeinsame Pfade mit abweichenden Bytes. Das beschreibt die gelieferten Archive. Die Main-Änderungen werden als Revisions- und Prüfprinzipien übernommen, ohne Aussage zu einer veröffentlichten Version oder einem aktuellen Host.

OpenCode: fachlich ausgewertet wurden die Entwicklungsanleitungen für End-to-End-, Komponenten-, Unit- und Terminaltests, Effect, RTL und Agent-Diagnose. Das Monorepo und seine Provider-, UI- und Plugin-Implementierungen bleiben Quellmaterial. Die Beispielumsätze und Logos verbleiben im Quellarchiv. Die Sprachfacette enthält Anleitungen für den Umgang mit Aufnahmen und Zugangsdaten.

## Re-Import und ChatGPT-Audit

Die neu gelieferten Kopien der ChatGPT Skills Library und des Python-Sprachassistenten stimmen bytegenau mit den bereits ausgewerteten Archiven überein. Alle zwölf zugeordneten Fachabläufe bleiben erhalten. Der Sprachablauf enthält jetzt zusätzlich einen expliziten Chat-Transkript- und Textpfad. Der [Auditbericht](chat-kompatibilitaetsaudit.md) dokumentiert die Änderungen am Paket.

Siehe [Quellenabgleich v0.35.0](integration-v035.md) für SCEVI R01, die Fullstack-Artefakte und die Wiederholung des ChatGPT-Skills-Archivs.

## Konsolidierung 0.70.0

Die [Integrationsmatrix](quellenintegration-070.md) dokumentiert neun Eingänge, die Übernahmen in bestehende Fähigkeiten und die verbleibenden Abnahmen.

## Visuelle Konsolidierung 0.71.0

Die [visuelle Quellenintegration](visuelle-quellenintegration-071.md) dokumentiert die neun Eingänge, den übertragbaren Anteil jeder Quelle und die offenen Host-Abnahmen.

## Konsolidierung 0.72.0

Die [Quellenmatrix](quellenintegration-072.md) bündelt die Prüfentscheidungen beider Upload-Gruppen, einschließlich der eingebetteten Vorstände und erneuten Kopien.
