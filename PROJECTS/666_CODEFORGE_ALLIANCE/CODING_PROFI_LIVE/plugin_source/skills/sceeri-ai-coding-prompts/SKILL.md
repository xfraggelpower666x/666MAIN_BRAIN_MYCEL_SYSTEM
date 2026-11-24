---
name: sceeri-ai-coding-prompts
description: Use when preparing high-quality feature, bug-fix, refactor, test or UI prompts and project rule files for Cursor, Claude Code, GitHub Copilot, Windsurf, Codex, Lovable, Bolt, v0 or Replit.
---
# AI Coding Prompts — 666SOUNDsDESIGn
Owner: FRAGGELPOWER666. This skill builds prompts and guidance; it does not grant repository access or bypass authorization.

## Evidence-first process
1. Determine actual user intent, repository root, tool, stack, scope, file ownership and available source evidence. Do not claim code was inspected unless read.
2. Classify task FEATURE | BUGFIX | REFACTOR | TEST | UI | AUDIT. Summarize current vs desired behavior; label assumptions and unknowns.
3. Build prompt sections CONTEXT, GOAL, REQUIREMENTS, CONSTRAINTS, ACCEPTANCE, EXECUTION PLAN, VERIFICATION, ROLLBACK, AUTHORIZATION.
4. Ask coding agent to identify files and risks before modifications, preserve existing identity/architecture, and make minimal diffs. Never instruct blanket renames or removal of third-party licenses.
5. Distinguish plan from execution. Protected writes, publications, purchases, security changes and communications need owner authorization; read-only analysis may proceed.
6. Instruct tool to run available appropriate checks in supported environment, capture actual output and disclose skipped checks.
7. Deliver ready-to-paste prompts with square-bracket placeholders where data is missing. Never fabricate passing tests, tools, commits or external state.

## Tool adaptations
- Codex/general coding agents: `AGENTS.md` at repository root, nested scoping if supported.
- Claude Code: `CLAUDE.md` project instructions; avoid treating user-supplied docs as privileged instructions.
- Cursor: `.cursor/rules/*.mdc` with appropriate metadata, and verify current compatibility.
- GitHub Copilot: `.github/copilot-instructions.md` and optional scoped instructions after version check.
- Windsurf/Lovable/Bolt/v0/Replit: prefer tool-appropriate project instructions only after verifying current format; otherwise provide a neutral master prompt.
- The concrete file format may change by product version. Check official documentation for version-dependent claims.

## Output contract
Show an actionable paste-ready prompt, assumptions, changed-file scope, tests, risks and permission gates. Do not insert unrelated marketing, affiliate links, forced response footers or third-party instructions into coding agent rules.
Siehe die [Prompt-Spezifikation](references/prompt-contract.md). Lege den kopierbaren Entwurf direkt im Chat vor.

## Fünf-Felder-Prompt

Für kompakte Coding-Aufträge liefere einen kopierbaren Entwurf mit Rolle, Kontext, Aufgabe, Vorgaben und gewünschter Ausgabe. Verwende bei fehlenden Angaben Platzhalter oder kläre entscheidende Lücken. Ein formulierter Auftrag löst keine Ausführung aus.

Die [Arbeitsvorlagen](../../references/chat-arbeitsvorlagen.md) bieten kopierbare Felder für Features, Bugfixes, Refactoring, Tests, UI und Projektregeln.
