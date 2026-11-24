# Datei-für-Datei-Zuordnung der Agenten-Add-ons

Die beiden neuen Archive sind statisch erfasst. Die Zuordnung beschreibt die fachliche Nutzung im [Chat-Ablauf](../skills/sceeri-agentenlauf-chat/SKILL.md) und in der [Agentenlauf-Abnahme](agentenlauf-abnahme.md). Python-Symbole werden aus der Syntaxstruktur inventarisiert. Die Dateien wurden als Quellen gelesen. Zielprojekt-Server, Skripte und Workflows benötigen einen eigenen Laufnachweis.

Die drei übrigen ZIPs waren Wiederholungen bereits erfasster Inhalte. Der [bisherige Quellenabgleich](integration-v035.md) dokumentiert ihre fachlichen Zuordnungen.

## agent-runtime-core-addon

| Quelldatei | Symbole oder Prüfschwerpunkt | Chat-Übernahme |
| --- | --- | --- |
| `README.md` | Agent Runtime Core Add-on, Kernfunktionen, Architektur, Schnellstart | Projektarchitektur und Installationsannahmen als Herkunft |
| `dashboard-api/index.html` |  | SCEVI-Darstellung und Host-Abnahme |
| `deployment/ci.yml` |  | CI-Schritte, ausgeführte Checks und Quellrevision |
| `deployment/docker-compose.yml` |  | Zielprojekt-Abhängigkeiten und tatsächliche Dienste |
| `docs/roadmap.md` | Nächste Ausbaustufen | Geplante Fähigkeiten gegenüber belegtem Bestand |
| `reference/data-model.md` | Runtime Data Model | Chat-Lauftabelle und Evidenzfelder |
| `reference/runtime-architecture.md` | Runtime Architecture, Komponenten, Datenfluss, Sicherheitsprinzip | Laufphasen und Zuständigkeitsgrenzen |
| `reference/tool-policy.md` | Tool Policy, Tool-Klassen, Regeln | Scope, Werkzeugfreigabe und Policy-Evidenz |
| `runtime/pyproject.toml` |  | Versions- und Abhängigkeitsinventar des Zielprojekts |
| `runtime/src/agent_runtime/__init__.py` |  | Paketgrenze und Versionsmetadaten des Zielprojekts |
| `runtime/src/agent_runtime/api.py` | CreateRunRequest, ToolCallRequest, create_run, call_tool, get_memory, evaluate_run | Lauf-, Werkzeug-, Auswertungs- und Beobachtungsgrenzen |
| `runtime/src/agent_runtime/approvals.py` | ApprovalService, ApprovalService.__init__, ApprovalService.create, ApprovalService.approve, ApprovalService.reject, ApprovalService._get | Bindung von Freigabe an Lauf und konkrete Aktion |
| `runtime/src/agent_runtime/evaluator.py` | Evaluator, Evaluator.evaluate | Ziel, Testnachweise, Verstöße und Evidenz getrennt bewerten |
| `runtime/src/agent_runtime/executor.py` | SandboxExecutor, SandboxExecutor.__init__, SandboxExecutor.run_command | Befehlsausführung und nachgewiesene Host-Isolation getrennt prüfen |
| `runtime/src/agent_runtime/guardrails.py` | validate_input, validate_command, validate_output | Defensive Eingabe-, Ausgabe- und Redaktionsprüfung |
| `runtime/src/agent_runtime/memory.py` | MemoryStore, MemoryStore.__init__, MemoryStore.save_working, MemoryStore.load_working, MemoryStore.save_episodic, MemoryStore.save_semantic, MemoryStore.save_procedural, MemoryStore.search | Arbeitsstand, Ereignisse, Fachwissen, Verfahrensregeln und Suche |
| `runtime/src/agent_runtime/models.py` | RunState, RiskLevel, ToolSpec, Task, Evidence, TraceSpan, Run | Laufzustand, Aufgabe, Evidenz und Trace-Felder |
| `runtime/src/agent_runtime/policy.py` | PolicyDecision, evaluate_tool_policy | Projektbindung, Rollen, Scope und Freigaben prüfen |
| `runtime/src/agent_runtime/tools.py` | ToolRegistry, ToolRegistry.__init__, ToolRegistry.register, ToolRegistry.get, ToolRegistry.invoke, ToolRegistry._validate | Werkzeugregister, Eingabe- und Ausgabevertrag |
| `runtime/tests/test_guardrails.py` | test_allowed_command_passes, test_command_chaining_is_blocked, test_unknown_command_is_blocked, test_secret_in_input_is_blocked, test_script_output_is_blocked | Vorgelegte Sollfälle in Chat-Gegenproben übernehmen. Ausführungsstatus getrennt ausweisen. |
| `runtime/tests/test_memory_evaluator.py` | test_memory_stores_working_state, test_only_high_confidence_patterns_are_stored, test_evaluator_requires_tests, test_evaluator_detects_security_violation | Vorgelegte Sollfälle in Chat-Gegenproben übernehmen. Ausführungsstatus getrennt ausweisen. |
| `runtime/tests/test_policy.py` | test_developer_may_run_medium_risk_tool, test_developer_cannot_deploy_production, test_missing_scope_is_denied | Vorgelegte Sollfälle in Chat-Gegenproben übernehmen. Ausführungsstatus getrennt ausweisen. |
| `runtime/tests/test_tools.py` | make_spec, test_registry_invokes_registered_tool, test_unknown_tool_is_rejected, test_missing_argument_is_rejected | Vorgelegte Sollfälle in Chat-Gegenproben übernehmen. Ausführungsstatus getrennt ausweisen. |
| `runtime/tools/tool_manifest.yaml` |  | Werkzeugdeklaration und nachgewiesene Host-Fähigkeiten |
| `skills/observability-evaluation/SKILL.md` | Observability & Evaluation, Zweck, Trigger, Observability | Trace, Evaluation und bestätigte Regeln |
| `skills/policy-governance/SKILL.md` | Policy & Governance, Zweck, Trigger, Risikoklassen | Tool-Vertrag, Projektgrenze und vorhandene Freigabe |
| `skills/runtime-workflow/SKILL.md` | Runtime Workflow, Zweck, Trigger, Workflow | Laufphasen, Nachweis und Wiederaufnahme |

## production-agent-platform-addon

| Quelldatei | Symbole oder Prüfschwerpunkt | Chat-Übernahme |
| --- | --- | --- |
| `README.md` | Production Agent Platform Add-on, Schnellstart, Docker Compose, Dashboard | Projektarchitektur und Installationsannahmen als Herkunft |
| `dashboard/src/index.html` |  | SCEVI-Darstellung und Host-Abnahme |
| `deployment/ci.yml` |  | CI-Schritte, ausgeführte Checks und Quellrevision |
| `deployment/docker-compose.yml` |  | Zielprojekt-Abhängigkeiten und tatsächliche Dienste |
| `docs/production-checklist.md` | Production Checklist, Persistenz, Sandbox, Integrationen | Architekturabnahme und Recovery-Gegenproben |
| `platform/alembic/versions/001_initial.py` | upgrade, downgrade | Migrations- und Rückleseabnahme |
| `platform/pyproject.toml` |  | Versions- und Abhängigkeitsinventar des Zielprojekts |
| `platform/src/agent_platform/__init__.py` |  | Paketgrenze und Versionsmetadaten des Zielprojekts |
| `platform/src/agent_platform/api.py` | SandboxRequest, EvalRequest, health, run_sandbox, run_eval, evaluate_nlp, get_audit, get_metrics | Lauf-, Werkzeug-, Auswertungs- und Beobachtungsgrenzen |
| `platform/src/agent_platform/config.py` | Settings | Konfiguration der Zielumgebung, Herkunft und Geheimnisgrenzen |
| `platform/src/agent_platform/database.py` | get_session, save_run_checkpoint, load_run_checkpoint, healthcheck | Checkpoint, Persistenz und Gesundheitsnachweis |
| `platform/src/agent_platform/evaluation/framework.py` | EvalCase, EvalResult, EvaluationRunner, EvaluationRunner.run | Fallbasierte Evaluation, Sollwerte und fehlende Messung |
| `platform/src/agent_platform/evaluation/nlp_metrics.py` | NlpMetrics, entity_metrics | Entitätsvergleich und nachvollziehbare Metriken |
| `platform/src/agent_platform/integrations/ci.py` | CIIntegration, CIIntegration.__init__, CIIntegration.headers, CIIntegration.get_workflow_runs, CIIntegration.get_run_logs | CI-Readback, Revision und Logbezug |
| `platform/src/agent_platform/integrations/github.py` | GitHubIntegration, GitHubIntegration.__init__, GitHubIntegration.headers, GitHubIntegration.get_repository, GitHubIntegration.create_pull_request | Repo-Readback und autorisierter PR-Workflow |
| `platform/src/agent_platform/integrations/gitlab.py` | GitLabIntegration, GitLabIntegration.__init__, GitLabIntegration.headers, GitLabIntegration.get_project, GitLabIntegration.create_merge_request | Projekt-Readback und autorisierter MR-Workflow |
| `platform/src/agent_platform/models.py` | RunState, RiskLevel, AgentRole, AgentTask, TraceEvent, Run | Laufzustand, Aufgabe, Evidenz und Trace-Felder |
| `platform/src/agent_platform/observability/telemetry.py` | configure_telemetry, MetricsRegistry, MetricsRegistry.__init__, MetricsRegistry.increment, MetricsRegistry.observe, MetricsRegistry.snapshot | Trace, Laufmetrik und Exportnachweis |
| `platform/src/agent_platform/orchestration/orchestrator.py` | MultiAgentOrchestrator, MultiAgentOrchestrator.create_standard_workflow, MultiAgentOrchestrator.resolve_conflict | Aufgabenabhängigkeiten und Konfliktentscheidung |
| `platform/src/agent_platform/retrieval.py` | RetrievedDocument, VectorRetriever, VectorRetriever.__init__, VectorRetriever.index, VectorRetriever.search, VectorRetriever.remote_search | Projektbezogene Suche, Indexprovenienz und Sortierung |
| `platform/src/agent_platform/routers/events.py` | run_events | Statusereignisse gegen reale Arbeitsschritte abgleichen |
| `platform/src/agent_platform/routers/runs.py` | CreateRunRequest, create_run, get_checkpoint | Laufplanung, Checkpoint-Zugriff und Wiederaufnahme |
| `platform/src/agent_platform/routers/search.py` | SearchRequest, search | Abrufberechtigung, Herkunft und Ergebnisgrenzen |
| `platform/src/agent_platform/security/audit.py` | AuditLog, AuditLog.__init__, AuditLog.record, AuditLog.for_tenant | Auditspur und Nachweis zur Aufbewahrung |
| `platform/src/agent_platform/security/identity.py` | Identity, resolve_identity | Autoritative Identität, Rollen und Projektbindung |
| `platform/src/agent_platform/security/policy.py` | PolicyDecision, authorize | Projektbindung, Rollen, Scope und Freigaben prüfen |
| `platform/src/agent_platform/security/sandbox.py` | IsolatedSandbox, IsolatedSandbox.__init__, IsolatedSandbox.run | Tatsächlich erzwungene Ressourcen- und Prozessgrenzen |
| `platform/tests/test_evaluation.py` | test_nlp_eval_computes_f1, test_security_eval_fails_on_violation, test_regression_eval_detects_regression, test_entity_metrics | Vorgelegte Sollfälle in Chat-Gegenproben übernehmen. Ausführungsstatus getrennt ausweisen. |
| `platform/tests/test_observability.py` | test_metrics_registry_counts_events | Vorgelegte Sollfälle in Chat-Gegenproben übernehmen. Ausführungsstatus getrennt ausweisen. |
| `platform/tests/test_orchestrator.py` | test_standard_workflow_contains_required_agents, test_security_blocks_workflow | Vorgelegte Sollfälle in Chat-Gegenproben übernehmen. Ausführungsstatus getrennt ausweisen. |
| `platform/tests/test_policy.py` | test_tenant_isolation_blocks_cross_tenant_access, test_developer_cannot_deploy_production, test_high_risk_requires_approval | Vorgelegte Sollfälle in Chat-Gegenproben übernehmen. Ausführungsstatus getrennt ausweisen. |
| `platform/tests/test_retrieval.py` | test_search_is_tenant_isolated, test_results_are_sorted_by_score | Vorgelegte Sollfälle in Chat-Gegenproben übernehmen. Ausführungsstatus getrennt ausweisen. |
| `platform/tests/test_sandbox.py` | test_command_chaining_is_blocked, test_unknown_command_is_blocked, test_allowed_command_passes_validation | Vorgelegte Sollfälle in Chat-Gegenproben übernehmen. Ausführungsstatus getrennt ausweisen. |
| `platform/tools/tool_manifest.yaml` |  | Werkzeugdeklaration und nachgewiesene Host-Fähigkeiten |
| `reference/architecture.md` | Production Architecture, Kernprinzip | Architekturabnahme der Zielplattform |
| `reference/evaluation-model.md` | Evaluation Model, Eval-Typen, Metriken | Fallbasierte Evaluation und Metriken |
| `reference/security-model.md` | Security Model, Identität, Berechtigungen, Schutz | Defensive Zugriffs- und Datenabnahme |
| `skills/evaluation-observability/SKILL.md` | Evaluation & Observability, Zweck, Metriken, Evaluation | Zählwerte, Metriken und Quellenbelege |
| `skills/multi-agent-orchestration/SKILL.md` | Multi-Agent Orchestration, Zweck, Agenten, Workflow | Aufgaben, Fachrollen und Konflikte |
| `skills/production-runtime/SKILL.md` | Production Runtime, Zweck, Trigger, Workflow | Persistenz, Retrieval, CI und Laufzustand |
| `skills/security-compliance/SKILL.md` | Security & Compliance, Zweck, Schutzschichten, Regeln | Defensive Identitäts- und Zugriffskontrollen |
