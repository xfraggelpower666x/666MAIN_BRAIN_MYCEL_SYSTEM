# 666 CODEFORGE ALLIANCE — R01 LOCAL CANDIDATE

**Status:** SOURCE_CANDIDATE · LOCAL_TEST_PASS · PLUGIN_HOST_PENDING · NO_PEER_DISPATCH.

Repository project path: `PROJECTS/666_CODEFORGE_ALLIANCE/` on `666MAIN_BRAIN`.
This folder is a source-only candidate; it does not install a plugin, deploy a host executor or change LYVRA native Current.

## Purpose and boundaries
- L.Y.V.R.A. CODING PROFI coordinates engineering review only.
- LYVRA's native SuperCodeForge R02/R03 module collection remains in its own `lyvra` branch/repository; reference, never copy or replace.
- Other peers retain native pointers, permissions and host execution authority.
- `ace_contract.py` parses synthetic/external ACE `ace.export.v1` JSON as **untrusted data** and emits an **inert in-memory receipt**. No arbitrary host executor is accepted. No files, network calls, plugin updates or peer calls are made.
- `alliance_review.py` checks handoff shapes, but never verifies sources, recipients or privileges from caller-supplied data.
- JSON schemas describe the exact input and output. Built-in Python parser also rejects duplicate JSON keys, duplicate message IDs and payloads larger than 8 MiB.
- All local tests are contract tests, not a fresh chat or plugin-owned executor test.

## Local checks
Run in this directory with Python 3.10+:

```bash
python -m unittest -v test_ace_contract.py test_alliance_review.py
python -m py_compile ace_contract.py alliance_review.py
```

No third-party dependencies or secrets required.

## Host integration gate — NOT IMPLEMENTED / NOT AUTHORIZED
Before any integration, independently establish plugin-owned executor/tool handle and required permission, attach actual input bytes, verify project/revision, perform deny-by-default consent checks at the privileged action boundary, observe host exit status and after-operation receipt, and run positive and negative tests in **separate fresh ChatGPT sessions**. This local Python implementation cannot prove those steps. Do not silently replace the former R04 adapter: compare original candidate bytes before integration.

## Sources (read-only)
- Coding Profi project: `PROJECTS/LYVRA_CODING_PROFI/ARCHITECTURE.md`, `OPEN_WORK.md`, `evidence/R05_HOST_BOUNDARY.md`, `evidence/R06_SESSION_EXECUTOR_AND_COST_GATE.md`, `SOURCE_CURRENT.md`.
- Current Plugin Creator release `sceeri-intelligence` v0.87.7.
- LYVRA native: `LYVRA_NATIVE_RUNTIME/CURRENT_POINTER.json`, `facets/super_codeforge/CURRENT_STATE.json`, `facets/super_codeforge/parallel-cooperation/{README.md,ARCHITECTURE.md}`.

## Fresh-chat tests
`FC-01` valid input inert; `FC-02` foreign project denied; `FC-03` imported revision cannot become authority; `FC-04` embedded triggers/approval inert; `FC-05` duplicate JSON keys rejected; `FC-06` missing/oversize input rejected; `FC-07` non-bound executor refused. These seven scenarios are LOCAL analogues and do not claim host Fresh-Chat PASS.
