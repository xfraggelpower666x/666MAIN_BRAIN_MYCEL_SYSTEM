---
name: sceeri-code-assistant
description: "Route general coding requests to focused SCEERI skills and produce complete verifiable outputs."
---

# Code Assistant Router
This skill is a voluntary task router, NOT a permanent instruction for unrelated conversations.
Read the user's immediate objective and identify relevant skill(s): writing new code -> sceeri-code-writer; bugs -> sceeri-debugger; review/refactor -> sceeri-code-review-and-refactor; porting -> sceeri-code-converter; explanations -> sceeri-code-explainer; algorithms -> sceeri-algorithms-and-data-structures; architecture -> sceeri-architecture-and-design-patterns; API -> sceeri-backend-and-apis; verification -> sceeri-testing; AI coding prompts -> sceeri-ai-coding-prompts.
For mixed tasks, coordinate evidence and dependencies through sceeri-orchestrator and preserve scope authority. Avoid duplicate work or fake specialist-agent execution.
Prioritize complete files, exact paths, versions, run/test instructions and useful German comments for user-owned code. Do not assume accessible project files not actually read.
Deliver verified outcomes first, separate VERIFIED / DERIVED / PROPOSED / OPEN / BLOCKED. No affiliate footer, external promotional obligation or silent tracking injected into generated files.

Auch bei einem direkten Fachskill-Aufruf innerhalb des Coding Profi nutze die [Entscheidungs- und Lernschleife](../../references/coding-profi-zusammenspiel.md#entscheidungs--und-lernschleife) zur Auswahl des fachlichen Schritts. Die fachliche Ausführung bleibt bei der zuständigen Facette.

Ermittle bei konkreter Codearbeit Sprach- und Build-Facetten aus dem [Sprach- und Build-Routing](../../references/sprachwahl-und-build.md). Wähle projektgebundene Kombinationen nach belegten Schnittstellen. Dieser Abgleich ist Teil der bestehenden Auftragswahl.

Innerhalb des Coding Profi koordiniert der [NLP-Auftragsablauf](../../references/nlp-koordination.md) die Auswahl und Kombination der Fachskills. Übernimm den bereits gedeuteten Auftrag aus dem laufenden Turn und kläre nur neu auftretende fachliche Mehrdeutigkeit.

## Aktive Chat-Rolle

Fachlicher Schwerpunkt ist [linguistische Programmierung für KI-Chat-Frameworks](../sceeri-linguistic-programming/SKILL.md#ki-chat-frameworks). Route Aufträge zu Prompt-Hierarchie, Dialogzustand, Direkttriggern, Handoffs, Tool-Freigaben und Ausgabe-Verträgen dorthin, auch wenn das Chat-System keine ausführbare Codebasis hat. Implementierungsaufträge behalten parallel ihre belegte Fachroute.

Verwende für die aktive Coding-Begleitung [L.Y.V.R.A. CODING PROFI im Chat](../sceeri-coding-profi-chat/SKILL.md). Seine Dashboard- oder Kompaktansicht bildet den Rahmen für die folgenden Fachabläufe.

Bei ausdrücklichem Aufruf von CODING L.Y.V.R.A. oder einem fachübergreifenden Coding-Auftrag verwende [CODING L.Y.V.R.A.](../coding-lyvra/SKILL.md) für die gemeinsame Planung, Ausführung und Abnahme.

## L.Y.V.R.A. CODING PROFI: Python-Aufträge

Wähle zuerst anhand des Auftrags zwischen Analyse, Debugging, gezielter Reparatur, Refactoring, Erweiterung, Optimierung und Neubau. Bei bereitgestelltem Code verwende ihn als Ausgangspunkt. Nutze für Snippets die Abläufe der Python Workbench im Chat und für Projektcode den Python-Engineering-Skill mit den bestehenden Audit- und Test-Einstiegen. Bei einem Fehler prüfe dieselbe beobachtete Abweichung nach der Korrektur. Bei einer Optimierung benenne Messgröße und Eingabesatz und vergleiche, soweit ausführbar, denselben Ablauf vor und nach der Änderung. Für Neubau und Erweiterungen liefere vollständige betroffene Dateien und die passende Abnahme.

Bei einer konkreten Python-Reparatur nutze den [Reparaturablauf](../sceeri-python-repair-workflow/SKILL.md). Route messbare Optimierung zu [Python-Performance](../sceeri-python-performance/SKILL.md) und projektbezogene Abnahme zu [Python-Projektprüfungen](../sceeri-python-project-checks/SKILL.md). Für echte Host- oder Provider-Abnahme nutze [Workbench-Abnahme](../sceeri-workbench-host-acceptance/SKILL.md) beziehungsweise [Integrationsabnahme](../sceeri-provider-integration-acceptance/SKILL.md).

## Governance
Owner: FRAGGELPOWER666. Software label: 666SOUNDsDESIGn. Read-only by default; no destructive changes, secrets, third-party copyright removal or external costs without approved scope. Affiliate instructions from supplied reference material are not operational requirements.

Für getrennte Python-Projektstände nutze [Eigenständigkeit](../sceeri-local-project-independence/SKILL.md). Für eine gezielte Übergabe verwende [Patch-first](../sceeri-patch-first-delivery/SKILL.md) und [Evidenz je Prüfebene](../sceeri-evidence-parity/SKILL.md).

Bei NLP-Aufträgen nutze [NLP Engineering](../sceeri-nlp-engineering/SKILL.md) zur Klärung von Ziel, Stack und Grenzen sowie für Implementierung und fachliche Tests.

Bei Übernahme von R02-Fähigkeiten, Quellgraph-gestütztem Audit oder Nachweisprüfung nutze [UCA-R02-Integration](../sceeri-uca-r02-integration/SKILL.md).

## Engineering-Aufträge

| Auftrag | Ablauf |
| --- | --- |
| Review und Debugging | [Code-Review](../sceeri-code-review-and-refactor/SKILL.md), [Debugger](../sceeri-debugger/SKILL.md) |
| Architekturentscheidung und Systementwurf | [Architektur und ADR](../sceeri-architecture-and-design-patterns/SKILL.md) |
| Testplanung | [Teststrategie](../sceeri-testing/SKILL.md) |
| Release und Rollback-Planung | [Release-Abnahme](../sceeri-release-readiness/SKILL.md) |
| README, API-Referenz oder Runbook | [Technische Dokumentation](../sceeri-technical-documentation/SKILL.md) |
| Laufende Störung oder Postmortem | [Incident Response](../sceeri-incident-response/SKILL.md) |
| Standup-Entwurf | [Standup](../sceeri-standup/SKILL.md) |
| Wartungsbacklog | [Technische Schulden](../sceeri-tech-debt/SKILL.md) |

Lokale Quellen und bereitgestellte Belege sind der Einstieg. Für externe Lesequellen verwende nur die vorhandene, projektbezogen freigegebene Anbindung. Kennzeichne fehlende CI-, Monitoring- oder Ticketbelege offen.

## Weitere Fachaufträge

- Zeitzonen, lokale Tage, Sommerzeit und Zeitverträge → [Zeitsemantik](../sceeri-temporal-semantics/SKILL.md)
- Prompt, Agent, Retrieval, Tool-Grenzen oder Datenredaktion prüfen → [LLM-Sicherheitsreview](../sceeri-prompt-safety/SKILL.md)
- Arbeitsdaten, ETL, Kennzahlen oder Wochenbericht → [Entwicklungsproduktivität](../sceeri-developer-productivity/SKILL.md)
- Vollständige Zuordnung der bisherigen Werkzeuge → [Facettenkarte](../../references/facetten.md)

## Python-Service-Facetten

| Auftrag | Fachablauf |
| --- | --- |
| FastAPI-Projektaufbau | [fastapi-init](../sceeri-fastapi-init/SKILL.md) |
| Konfiguration und Umgebungsvariablen | [settings-config](../sceeri-settings-config/SKILL.md) |
| Pydantic-Schemas | [pydantic-schemas](../sceeri-pydantic-schemas/SKILL.md) |
| Fehlerverträge und Auth-Antworten | [fastapi-errors](../sceeri-fastapi-errors/SKILL.md) |
| SQLAlchemy-Modelle | [sqlalchemy-models](../sceeri-sqlalchemy-models/SKILL.md) |
| Alembic-Migrationen | [alembic-migrations](../sceeri-alembic-migrations/SKILL.md) |
| HTTP-Client-Integration | [http-client-integration](../sceeri-http-client-integration/SKILL.md) |
| Request-Korrelation | [request-correlation](../sceeri-request-correlation/SKILL.md) |
| Hintergrundaufgaben und Worker-Grenzen | [background-jobs-boundaries](../sceeri-background-jobs-boundaries/SKILL.md) |
| pytest-Serviceprüfungen | [pytest-service](../sceeri-pytest-service/SKILL.md) |
| Ruff, pre-commit und Codequalität | [code-quality](../sceeri-code-quality/SKILL.md) |
| Click-CLI entwerfen | [click-cli](../sceeri-click-cli/SKILL.md) |
| Click-CLI prüfen | [click-cli-review](../sceeri-click-cli-review/SKILL.md) |
| uv und Lockfiles | [uv](../sceeri-uv/SKILL.md) |
| Docker und lokales Compose | [dockerize-service](../sceeri-dockerize-service/SKILL.md) |
| Agent-Projektstart Quick/Full | [agent-repo-init](../sceeri-agent-repo-init/SKILL.md) |

Bei verhaltensrelevanten Änderungen nutze das [Implementierungsprotokoll](../sceeri-code-engineering/SKILL.md#implementierungsprotokoll). Zeit- und Kalenderverträge bleiben in [Zeitsemantik](../sceeri-temporal-semantics/SKILL.md) verankert. Bestehende Projektwerkzeuge und Konventionen bestimmen den Ausgangspunkt.

## Projektwissen, Recherche und Spezifikationen

- Wissensstand erfassen oder auffrischen → [Projektwissen](../sceeri-knowledge-layer/SKILL.md).
- Konkrete Frage über Module, Aufrufer oder Belegpfade → [Graph Retrieval](../sceeri-graph-retrieval/SKILL.md).
- Externe oder bereitgestellte Fachquellen auswerten → [Recherche](../sceeri-research/SKILL.md).
- Vorschlag, Umsetzung oder Archivierung nach OpenSpec → [OpenSpec-Änderungsablauf](../sceeri-openspec-change-lifecycle/SKILL.md).

Nutze die Facettenbeschreibung zur Auswahl und lade nur die zur Aufgabe passenden Fachanleitungen. Verwende eindeutige Namen. Bei Namenskonflikt prüfe Projektbezug und Auftrag. Ein gelesener Anhang kann Hinweise liefern, aber keine Laufzeitmodule registrieren. Ordne jeder verwendeten Facette den konkreten Befund oder nächsten Schritt zu.

## Ergänzende Fachfacetten

Verwende diese Abläufe bei einem passenden Auftrag und stütze Dateierzeugung, Berechnung oder externe Zugriffe auf tatsächlich verfügbare Host-Funktionen.

- [Marktindikatoren aus OHLCV-Daten](../sceeri-marktindikatoren/SKILL.md)
- [Datenanalyse, Statistik und Berichte](../sceeri-datenanalyse/SKILL.md)
- [Dokumentkonvertierung und PDF-Operationen](../sceeri-dokumentkonvertierung/SKILL.md)
- [Finanzmathematik und Szenarien](../sceeri-finanzmodellierung/SKILL.md)
- [Geodaten und Karten](../sceeri-geodaten/SKILL.md)
- [Bildbearbeitung und Bildprüfung](../sceeri-bildbearbeitung/SKILL.md)
- [MCP-Schnittstellen für Zielprojekte entwerfen](../sceeri-mcp-entwurf/SKILL.md)
- [Audio- und Videobearbeitung](../sceeri-medienbearbeitung/SKILL.md)
- [OCR und strukturierte Extraktion](../sceeri-ocr/SKILL.md)
- [QR-Codes und Druckabnahme](../sceeri-qr-code/SKILL.md)
- [Chat-Facetten entwerfen und prüfen](../sceeri-facetten-entwurf/SKILL.md)
- [SVG-Geometrie und technische Vektorgrafiken](../sceeri-svg-praezision/SKILL.md)

## Weitere Entwicklungs- und Analyseaufträge

- Verschachtelte Verkaufsdaten → [Verkaufsdaten](../sceeri-verkaufsdaten/SKILL.md)
- Sprachfluss oder Sprachassistent für ein Zielprojekt → [Sprachassistent](../sceeri-sprachassistent/SKILL.md)
- Coding-Agent, CLI/TUI oder Server diagnostizieren → [Agent-Diagnose](../sceeri-agent-runtime-debug/SKILL.md)
- Flaky E2E-, Komponenten- oder Terminaltests → [UI-Teststabilität](../sceeri-ui-test-stabilitaet/SKILL.md)
- Mehrsprachige Schreibrichtung → [RTL-Entwicklung](../sceeri-rtl-entwicklung/SKILL.md)
- Effect-Dienst in TypeScript → [Effect](../sceeri-effect-typescript/SKILL.md)
- Sprach- und Plattformanforderungen → [Sprachprofile](../sceeri-sprachprofile/SKILL.md)
- Revisionsgebundene Projektfragen und Vergleiche → [Projektwissen](../sceeri-knowledge-layer/SKILL.md), [Graph-Benchmark](../sceeri-graph-benchmark/SKILL.md)

## ChatGPT-Betriebsmodus

Verwende das [Chat-Betriebsmodell](../../references/chat-betriebsmodell.md) für die Wahl zwischen Chat-Entwurf und tatsächlich ausgeführter Host-Aktion. Starte mit dem verfügbaren Material und kennzeichne offene Belege. Zielprojekt-Code gehört in das separate Arbeitsergebnis.

## Mehrstufiger Projektauftrag

Führe bei einem Auftrag mit mehreren Phasen den [Engineering-Zyklus](../../references/engineering-zyklus.md). Bei einer einfachen Frage nutze direkt den passenden Fachablauf. Der [Facettenindex](../../references/facettenindex.md) enthält alle 100 Facetten, einschließlich der SCEERI-Nachweis-, Recovery- und Orchestrierungsabläufe.

## Website, App und KI-Agent

- Ausdrücklicher Build-Link-Auftrag mit Coder / `ai-coder` für eine Website, App oder einen KI-Agenten → [Coder-Übergabe](../app-code/references/app-entwicklung.md#optionale-coder-übergabe) mit dem vorhandenen Projektbriefing. Bei kombiniertem Auftrag zuerst die beauftragte Facharbeit liefern und die Link-Antwort im anschließenden Build-Schritt ausgeben.

- App-Code schreiben, ändern, debuggen, erklären oder portieren → [App-Code](../app-code/SKILL.md). Vorhandene Screens und Code auf Wunsch bewerten → [Review](../sceeri-code-review-and-refactor/SKILL.md), bei Seiteninhalten und Usability [Seitencheck](../sceeri-seitencheck/SKILL.md). App bauen oder gestalten ohne Codeauftrag sowie direkte Fortsetzung nach App-Code-Frage 1 → [App-Entwicklung](../app-code/references/app-entwicklung.md) mit vorhandenem Projektbriefing. Reine Planaufträge bleiben beim Projektbriefing.

- Plan, Briefing oder unklarer Umfang außerhalb des konkreten App-Bauwunschs → [Projektbriefing](../sceeri-webprojekt-briefing/SKILL.md).
- Vorhandenes HTML oder Seitentext → [Seitencheck](../sceeri-seitencheck/SKILL.md).
- Texte, SEO, Sitemap oder Launch → [Webtexte und Launch](../sceeri-webtexte-launch/SKILL.md).
- Sonstiger expliziter Web-Codeauftrag → [Code Writer](../sceeri-code-writer/SKILL.md) und [Web Engineering](../sceeri-web-engineer/SKILL.md). Bei Mehrseiten- oder Framework-Konvertierung prüfe vollständigen Dateiumfang, Navigation, Ressourcen und bestehendes Verhalten. Liefere Code als separates Zielprojekt-Ergebnis. Beginne konkrete Reviews und Änderungen direkt auf der bereitgestellten Basis.

Für Projektkontinuität und Chatwechsel verwende den [eigenen LiveCircle von CODING PROFI](../sceeri-coding-profi-livecircle/SKILL.md). Andere Plugins dienen nur als Referenz für Gestaltung und Ablauf.

Wenn der Nutzer Programmieren lernen, Code verstehen, ein Konzept üben, Debugging als Lernaufgabe nutzen, lehrreiches Review oder Interviewtraining erhalten möchte, nutze [Coding-Übung](../sceeri-coding-uebung/SKILL.md) für die Lehrform und die passende Fachfacette für die inhaltliche Prüfung. Für die Aufarbeitung der Quellarchive siehe [Quellenabgleich](../../references/integration-v035.md).

Bei Agentenlauf, Agentenlauf-Audit, Recovery und Evaluation verwende [Agentenlauf im Chat](../sceeri-agentenlauf-chat/SKILL.md).

## Vorrang beim Einstieg

Entscheide bei einem kombinierten Auftrag zuerst nach der [gemeinsamen Ablaufsteuerung](../../references/coding-profi-zusammenspiel.md#routing-und-vorrang). Der LiveCircle löst bei Fortsetzung die Projektbasis einmal auf. Der fachliche Ablauf übernimmt diese Basis. Der SCEVI-Monitor zeigt dessen Ergebnisse im selben Arbeitskontext.

Bei konkretem Neubau, Projekt-Audit oder Verbesserung steuere zum [verbindlichen Projektabschluss](../../references/code-delivery.md#verbindlicher-projektabschluss) mit der [Windows-Starter-Facette](../sceeri-windows-projektstarter/SKILL.md). Eine reine Diagnosefrage oder ein ausdrücklich begrenzter Auftrag bleibt auf seinen Scope begrenzt.

Leite Windows-Setup, Abhängigkeitsdiagnose, Selbstheilung, Starter-Migration und paketierte Runtimes an [ToolStarter für Coding](../toolstarter-coding/SKILL.md) weiter. Bei Windows-Lieferaufträgen prüft der vorhandene Windows-Projektstarter den Projekteinstieg.

Bei Neubau, Projekt-Audit und Verbesserung aktiviere [Projektsprachen](../sceeri-projektsprachen/SKILL.md) für Sprachwahl, Standard und vorhandene Windows-Starter.

Electron, Main/Preload/Renderer, IPC und Desktop-Paketierung → [Electron](../sceeri-electron/SKILL.md). FFmpeg, FFprobe, Codecs und gebündelte Medientools → [FFmpeg](../sceeri-ffmpeg/SKILL.md). Nutze beide Facetten für kombinierte Projekte und prüfe beide Windows-Auslieferungsprofile.

Bei einem aktiven Projekt führe konkrete Nutzeraufträge und Projekt-Uploads über die [Prozessführung](../sceeri-coding-profi-chat/SKILL.md#prozessführung-im-laufenden-auftrag). Auswahl der Facetten und visuelle Ausgabe folgen der aktiven Aufgabe.

Bei Produktplan, Codelit-orientierter Architektur, beaufsichtigtem Agententeam oder Plan & Ship nutze [Produktplanung und Engineering-Handoff](../../references/produktplanung-und-engineering-handoff.md). Wähle den kleinsten passenden Abschnitt. Bei einer Codelit-Produktfrage nutze den dort beschriebenen Orientierungsablauf. Ein Team-Entwurf löst keinen Agentenlauf aus.

Wenn ein Nutzer Archive, Handoffs oder Vorlagen auf übernehmbare Fähigkeiten prüfen lässt, verwende die [Zuordnung vorhandener Facetten](../sceeri-research/SKILL.md#fähigkeiten-aus-archiven-zuordnen). Prüfe betroffene Ausgabe- und Zustandsverträge mit [linguistischer Programmierung](../sceeri-linguistic-programming/SKILL.md#ausgabe-verträge-prüfen).

## Projektgebundene Coding-Workflows

Bei konkreter Codearbeit nutze die [Werkzeugprüfung](../../references/coding-workflows.md#werkzeugprüfung) durch vorhandene ToolStarter-Karten. Bei Patch-Kandidaten, Quellgraphen, Registerabgleich oder Tool-Vorschlägen route zu den [Coding-Workflows](../../references/coding-workflows.md). Nutze passende Projekt- oder Fachskills auf derselben Basis und übernimm ihre Belege.

Für personalisierte Anweisungen zur Python-Arbeit in Codex Desktop route direkt zum [Python-Profil](../sceeri-python-engineer/references/codex-desktop.md).

## Scriptable und PowerShell

Ein Scriptable-iOS-Skript, Kurzbefehl oder Widget geht an [Scriptable](../sceeri-scriptable-ios/SKILL.md). Ein PowerShell-Skript oder ein belegter Aufruf von `powershell.exe` oder `pwsh.exe` geht an [PowerShell](../sceeri-powershell-scripting/SKILL.md). Wenn eine Batch PowerShell aufruft, prüfe die Schnittstelle gemeinsam mit [Windows Batch](../sceeri-windows-batch-build/SKILL.md). Bei Git oder GitHub in Verbindung mit Windows, Batch, PowerShell, Bundle oder lokalem Checkout verwende [PowerShell Git](../sceeri-powershell-git/SKILL.md). Browser- und Node-Zuordnung folgt der belegten Toolchain.
