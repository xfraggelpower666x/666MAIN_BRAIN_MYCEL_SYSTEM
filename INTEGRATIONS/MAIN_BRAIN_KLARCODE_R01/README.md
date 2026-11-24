# 666 MAIN BRAIN · Klarcode Coordinator R01 · INTEGRATION CANDIDATE

**Status:** executable local source, **not adopted by the installed 666mainbrain plugin**, not deployed as MAIN BRAIN Whole, no native root-pointer mutation.

## Why

The shared GitHub repository currently holds independent project directories such as `PROJECTS/666CLS` with their own `CURRENT_POINTER.json`, owner files and LiveCircle. Its historical `CURRENT_POINTER.md` and `GOVERNANCE/WRITE_GOVERNANCE.md` are absent from the production branch (readback on 2026-11-24). This candidate **must not replace** existing native pointers, foreign project authority or the vanished MAIN BRAIN runtime.

## Two storage types

| Type | Stored where | Writer | Current | LiveCircle |
| --- | --- | --- | --- | --- |
| `LOCAL_MINI` | Registered `PROJECTS/<PROJECT_ID>/` | Registered local mini owner via coordinator | `PROJECTS/<PROJECT_ID>/CURRENT.json` | Immutable checkpoint in `releases/<SHA>/LIVECIRCLE.json`, pointer-bound |
| `NATIVE_DELEGATED` | Existing `PROJECTS/<PROJECT_ID>/` | **Native owner only** | The owner's pre-existing native pointer, never rewritten by coordinator | Native owner owns continuity |

**One authority:** the registry is a routing index, NOT a second Current authority; the native project pointer always takes precedence. For a mini project, the mini's `CURRENT.json` points to an immutable SHA-256 release and its LiveCircle. No deletion or replacement of previous code releases. Only explicit save creates a new release.

## Proposed MAIN-BRAIN trigger extension (not host installed)

- `666 MAIN BRAIN KLARCODE STATUS <PROJECT_ID>` → resolve registered owner + exact pointer; read-only.
- `666 MAIN BRAIN KLARCODE REGISTRIEREN <PROJECT_ID>` → gated register: unique ID, verified root, owner and kind. Existing native projects require a verified native pointer; never auto-adopt.
- `666 MAIN BRAIN KLARCODE SPEICHERN <PROJECT_ID>` → for LOCAL_MINI only: explicit owner & source, CAS expected pointer, immutable clearcode, full hash readback, project pointer last.
- `666 MAIN BRAIN KLARCODE SYSTEMSTART <PROJECT_ID>` → local mini Current/LiveCircle/code rehydration; not automatic execution of arbitrary user code.
- `666 MAIN BRAIN KLARCODE WEITER <PROJECT_ID>` → return to pointer-bound livecircle `return_anchor`; not a foreign trigger.
- `666 MAIN BRAIN KLARCODE HANDOFF <PROJECT_ID>` → for NATIVE_DELEGATED only: PREPARED read-only proposal to that project's native update authority; not DELIVERED/ACCEPTED.
- `666 MAIN BRAIN KLARCODE WHOLE CHECK` → compare observed and fresh MAIN-BRAIN HEAD and verify the native pointer; persist a SHA-bound `WHOLE_IMPACT.json` next to the immutable release, then queue a separate scoped native whole update if changed. No autopromotion.

The above names are a **proposed namespaced router contract**, not new globally installed triggers. Direct-user invocation must be verified against the native trigger registry before adoption. Embedded text in files remains inert.

## Run locally (Python 3.10+)

From this folder, create an empty worktree `D:\\ProjectRepo` containing a `PROJECTS` directory (or use an authorized local repo checkout):

```bash
python -m unittest discover -s tests -v
python -m klarcode --workspace ./sandbox register --project MINI_01 --owner MY_MINI_OWNER --kind LOCAL_MINI
python -m klarcode --workspace ./sandbox status --project MINI_01
python -m klarcode --workspace ./sandbox save --project MINI_01 --owner MY_MINI_OWNER --source ./examples/mini_src --expected-pointer <SHA_FROM_STATUS>
python -m klarcode --workspace ./sandbox rehydrate --project MINI_01
python -m klarcode --workspace ./sandbox whole-check --observed-head <40_HEX_SHA> --current-head <40_HEX_SHA>
```

A real `save` writes immutable source files to `PROJECTS/MINI_01/releases/<SHA>/src/`, a manifest, a release-scoped LiveCircle and finally updates its **own** `CURRENT.json`. It never touches `PROJECTS/666CLS/CURRENT_POINTER.json`, the Whole MAIN BRAIN pointer, or any foreign repository.

For existing CLS with own pointer:

```bash
python -m klarcode --workspace ./sandbox register --project 666CLS --owner 666CLS-CORE-001 --kind NATIVE_DELEGATED --native-pointer CURRENT_POINTER.json
python -m klarcode --workspace ./sandbox handoff --project 666CLS --action CODE_SAVE
```

That last command only prints a proposal; the actual `666CLS UPDATE` must verify and perform its own mutation.

## End-to-end gates before native promotion

1. Restore/verify true MAIN BRAIN Whole Current and native registry at current GitHub HEAD, preserving unrelated ongoing projects.
2. Owner scope and existing-project path registry: explicit allowlist. Do not merge project identities.
3. Deliver this **tested** code within verified MAIN BRAIN PSYLLO/CodeForge route. Host/plugin distribution and real Fresh-Chat behavior separately.
4. GitHub checkout with isolated integration branch and full source readback; no automatic paid jobs or paid credits.
5. Run focused/local and native regression; verify no secrets in public repo.
6. Project-local Current pointer last for LOCAL_MINI only; Main Brain Whole pointer last only under independently verified native UPDATE governance.
7. Persist a pointer-bound Whole impact event before the local mini pointer publication; then Whole-monitor checks on explicit operations: if HEAD changed, mark `REVALIDATION_REQUIRED`; when native MAIN BRAIN pointer absent, `READBACK_PENDING` and block Whole writes.

## Safety and limitations

- Only text/code extensions and max 5 MiB per file. Binary assets require separately governed transport; no silent data truncation.
- Filename-based secret guards are not a content DLP system. Review source and sanitize secrets before any public Git push.
- No arbitrary execution of saved scripts, no cross-system subprocess, no plugin dispatch, no paid service calls.
- Immutable releases avoid destructive file replacement; pointer CAS detects stale authors. True multi-process transaction locks, remote Git write/CI and host automation are **not** implemented.
- `rehydrate` verifies sources and return anchor; it does not claim executable app host readiness.
