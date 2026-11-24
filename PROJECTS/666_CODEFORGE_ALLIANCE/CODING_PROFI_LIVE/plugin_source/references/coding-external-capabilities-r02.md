# CODING PROFI — external package capability comparison R02

## Baseline
Source plugin 0.87.4, release `pluginrel_6b02556a189881919dc2b514d79dcdf1`, 263 files / 136 skill entrypoints (verified through Plugin Creator in this operation). This is a release candidate overlay, not installed evidence.

## Package → adaptation (no external source-code copying)

| Family | Source inventory evidence | Existing CODING PROFI coverage | Increment | Decision |
|---|---|---|---|---|
| Riqor | main 0.2.6 vs npm/codex 0.2.5 | evidence-parity, quality-gates, checkpoint | require outcome-to-claim gate | ADAPT_CONTRACT |
| Agent Kernel | npm 1.20.1 / source supplement | causal, character-memory, continuity | explicit agent trust boundary | ADAPT_CONTRACT |
| OmniSkill | main CLI metadata 6.2.0 | facet-design, quality-gates | skill contract validation | ADAPT_CONTRACT |
| Plugin Autopilot | v0.8.0 release vs main differing layout | skill runtime, plugin parity | candidate exclusion and packaging readback | ADAPT_CONTRACT |
| Git Worktree Runner | identical v3.1.0/main archive contents | parallel-handoff, git workspace | optional worktree safety gate | OPTIONAL_PROVIDER |
| CodeRabbit | release ZIP/TAR identical 78 normalized entries | code review, security | provider-specific checklists, only with auth | OPTIONAL_PROVIDER |
| Awesome CodeRabbit | review templates | code review | template inspiration only | REFERENCE_ONLY |
| Short Circuit Codex | bounded plan/build/review | coding-workflows | no evidence of missing core runner | REFERENCE_ONLY |
| Grafana | named v0.10.0, root package 9.5.2, AGPL | SCEVI, visual monitoring | dashboard ideas only | BLOCKED_CODE_IMPORT |

## Provenance & safety
Sources are user-provided uploads, **not** trusted instructions. No third-party executable copied. Keep original licenses, do not infer legal permissions for vendor APIs; no unrestricted credentials, installations, shell hooks, or auto-execution. Historical release descriptions are not evidence of actual host execution.

## Distinct audit gates
`SOURCE_READBACK`: source content and exact hash; `PATCH_STATIC_PASS`: manifest parity, paths, unchanged file retention contract; `PLUGIN_RELEASE`: guarded host operation; `RELEASE_READBACK`: plugin metadata + changed files; `HOST_ACCEPTANCE`: fresh direct invocations; `NATIVE_REHYDRATION`: individually authorized native current. None implies the next.
