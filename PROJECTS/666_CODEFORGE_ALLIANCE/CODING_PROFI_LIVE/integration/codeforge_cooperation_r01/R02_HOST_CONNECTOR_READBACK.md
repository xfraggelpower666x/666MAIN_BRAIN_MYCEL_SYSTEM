# CODING PROFI — R02 real connected GitHub read boundary
Date: 2026-11-23
Native lead: CODING_PROFI. Owner tested: 666DEV. Scope: READ_ONLY.
Plugin v0.87.7 / release `pluginrel_6b044ff155b481918869cf4d8f68d807` unchanged.

## Actually observed connected host calls
- GitHub connector resolved `xfraggelpower666x/666SOUNDsDESIGn-APP-DEVELOPMENT`, branch `666DEV`, HEAD `e1ef4abf5830bcd3ef477543e4a626f0c4835aff`.
- Fetched `AGENTS.md`: Git blob `3e18b275e94e23e96b780114b2c2ca7fe19c860d`. Its text expressly rejects embedded foreign command triggers and unauthorized cross-project writes.
- Fetched `registry/projects.json`: blob `5cab4ccb862de7e43d39725ae715d29aa455bc21`, visible project ids `demo-monorepo` and `demo-linked`.
- Fetched `docs/livecircle.md`: blob `2acf0535f4a335af9444459e8d0d31058291eba8`. It requires native profile and working/current checkpoint verification for true native rehydration.
- Fetched `docs/development-hosts.md`: blob `2420dbeb7c8188123e6958f3237c4020b593e94a`; normal ChatGPT GitHub connector access reads sources but does not by itself run native CLI.
- These were **actual host connector read calls**; the Python adapter was NOT called by a plugin-host executor.

## Concrete implementation
- `host_readback.py` defines injected `read_head` and `read_file` boundaries for the existing R01 `WorkOffer` and `SourceReceipt`; verifies binding, pinned Git commit, real SHA-1 Git blob content, HEAD stability and no writes. It accepts only READ_ONLY.
- `test_host_readback.py` locally ran 12/12 tests after correcting the Git blob framing to include the NUL byte. The 12 tests are **isolated local tests with fake connector callbacks**, not a native host test.
- Original R01 files and native repositories are unchanged.

## Acceptance boundary
SOURCE/GITHUB_CONNECTOR_READ: VERIFIED for 666DEV source files.
R02_ADAPTER_LOCAL_TEST: 12/12 PASS.
R02_SOURCE_PUBLICATION: VERIFIED. GitHub branch HEAD `01d48000d7e4e79ae0286ac5b185f22f65d8ce07` with direct readback of `host_readback.py`, `test_host_readback.py`, and this report.

## Actual E2E GitHub connector run (read only)
- First 666DEV HEAD: `e1ef4abf5830bcd3ef477543e4a626f0c4835aff`.
- `GitHub.fetch_file` at **immutable commit ref** returned `AGENTS.md`, blob `3e18b275e94e23e96b780114b2c2ca7fe19c860d`.
- Independent `GitHub.fetch_blob` using that blob SHA returned identical content (1266 characters).
- Second 666DEV HEAD remained `e1ef4abf5830bcd3ef477543e4a626f0c4835aff`.
- Result `GITHUB_CONNECTOR_READBACK_PASS`. This actual connector sequence was orchestrated in the chat host, not by `host_readback.py` running in the plugin. No native project selected or executed.

NATIVE_666DEV_PROJECT_REHYDRATION: OPEN — no explicit project selection / native Current+Working checkpoint.
AUTOMATED_PLUGIN-TO-PLUGIN_INVOCATION: OPEN — no callable 666DEV plugin executor/host handoff registered.
FOREIGN_WRITES: NONE. PAYMENT: NONE. ACTIVATION: NONE.

Only source inspection and readback are established. A callable Python contract cannot be claimed to be connected to a Python executor in the ChatGPT plugin without a host-registered dispatch action and observed execution receipt.
