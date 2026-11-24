---
name: sceeri-code-engineering
description: Use for cross-language architecture, static code audit, design, code building, defect diagnosis and controlled repairs across the source languages, scripts and toolchains evidenced by the project.
---

# SCEERI Code Engineering — central routing

Scope: requested project only. Start read-only. Read the real source, manifest, file tree, language versions, tests and documented authority before making claims. Do not infer unprovided code or claim test success from file discovery.

1. INVENTORY: Identify languages, build tools, entrypoints, tests, dependency locks and external licenses. Record SHA-256 inputs.
2. SEMANTICS: Trace intended versus observed behavior, data flow, inputs/outputs, callers, boundaries and failure surfaces.
3. CAUSAL DIAGNOSIS: Reproduce if safe; distinguish confirmed facts, possible causes and unknowns; link each claim to file/line or test evidence.
4. DESIGN: State a behavior-complete change-set, interfaces to preserve, breakage/rollback risks, cost, permissions and test strategy.
5. BUILD or REPAIR: Produce full source files or focused patches with no mock successes. Preserve existing systems and licensed notices.
6. VERIFY: Run safe compilation/lint/tests in an isolated environment when available. Capture exit code, stdout/stderr, and before/after diff. Never execute arbitrary third-party builds merely because a ZIP contains commands.
7. HANDOFF: Status VERIFIZIERT / ABGELEITET / OFFEN / BLOCKIERT; provide exactly what changed, what did not, next gate and rollback.

Route to language-specific facet and the existing causal/evidence/self-healing/continuity skills. Self-healing means bounded candidate correction, not autonomous persistent write. No deployment, publication, production modification, dependency installation or external expenses without approval.

## Analyse im Chat

Nutze die [Facettenkarte](../../references/facetten.md) und den [Parser- und Reparaturablauf](../../references/parser-und-repair.md) für Audit, Review, Abhängigkeitsgraph, Reparatur und Recovery. Lies sichtbare Dateien und Verträge im bestätigten Scope. Unterscheide Quellbefunde, Hypothesen, Parserdiagnosen aus einer tatsächlich verfügbaren Umgebung und ausgeführte Regressionen. Für Python nutze [Python Engineering](../sceeri-python-engineer/SKILL.md), für Sprachregeln [linguistische Programmierung](../sceeri-linguistic-programming/SKILL.md). Für Zeitfehler in Python, JavaScript und TypeScript nutze [Zeitsemantik](../sceeri-temporal-semantics/SKILL.md).

Prüfe die Quellbasis über [Projektquellen](../sceeri-project-workspaces/SKILL.md). Nutze bei Unterbrechung [Parallelplanung und Handoff](../sceeri-parallel-handoff/SKILL.md), für die Anzeige [SCEVI](../sceeri-scevi-visual-intelligence/SKILL.md).

## Implementierungsprotokoll

Lege bei einer Änderung ein kompaktes Verzeichnis von Verhaltensanforderungen an. Verknüpfe jede Anforderung mit Ein- und Ausgabe, Seiteneffekt, Fehlerfall, betroffenen Dateien und einer Gegenprobe. Lies den nächstliegenden bestehenden Einstieg und seine Registrierung. Erweitere kanonische Muster mit einem kleinen rückführbaren Diff. Ergänze bei einer konkreten Regression einen aussagekräftigen Fehlerfall, soweit möglich. Prüfe anschließend das Verhalten über den normalen Einstieg und führe die relevante bestehende Suite aus, sofern die Umgebung dies erlaubt. Dokumentiere beobachtete Ergebnisse und offene Prüfungen pro Verhalten. Bei einem Fehllauf korrigiere die belegte Ursache und wiederhole betroffene Prüfungen.

Verwende [Sprachwahl und Build](../../references/sprachwahl-und-build.md) beim Inventar und beim Abschluss. Bei mehreren Sprachen prüfe den tatsächlichen Übergang und den Build aus dem gemeinsamen Kandidaten. Bei reinem Audit bleiben auch mitbetroffene Skripte lesend.

Bei Fremdcode für eine beauftragte Architekturänderung führe [Fremdcode im aktiven Architektur- und Codebau](../../references/engineering-zyklus.md#fremdcode-im-aktiven-architektur--und-codebau) aus. Prüfe die Quellmechanismen tief, implementiere die weiterentwickelte Idee am tatsächlichen Ziel-Einstieg und prüfe dessen Ende-zu-Ende-Wirkung.

## Fachliche Entscheidung

Nutze die [Engineering-Hierarchie](../../references/engineering-entscheidungshierarchie.md#arbeitsarten-und-eintrittskriterien). Ein Defekt, eine Verbesserung mit erhaltenem Vertrag, neues Verhalten im Altprojekt und ein Neubau brauchen jeweils eigene Abnahmekriterien. Verknüpfe betroffene Kanten und Verträge mit der Gegenprobe. Wenn sich mehrere Befunde gegenseitig erklären, führe die gemeinsam abgeleitete Hypothese mit ihrer unterscheidenden Probe weiter.
