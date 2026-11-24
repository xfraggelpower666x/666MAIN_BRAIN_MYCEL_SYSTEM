# CODING PROFI — R05 Host Boundary (2026-11-22)

## Production source
- Exact installed plugin: `plugins_6af753996b5c81918daadc40df266ce7` / `sceeri-intelligence`.
- Direct current release read: `0.87.6`, `pluginrel_6b02fd5dd41c819190e194cf2377c72d`.
- `.app.json` exposes required GitHub App binding. Neither examined manifests nor source establish an ACE Python executor.
- ACE R04 import skill does not exist in current v0.87.6 release.
- No second plugin, desktop application, Electron runtime or native authority is introduced.

## Executed isolated tests (Linux / CPython 3.13)
- ACE R04 importer: **13/13 PASS**.
- ACE R04 bridge/security: **7/7 PASS**.
- Universal Cost & Consent R01 reference: **6/6 PASS**.
- R05 synthetic cross-boundary negatives: **7/7 PASS**.
- Total **33/33 local PASS**. These are developer-environment tests, **not** Plugin Host Acceptance.
- The first bridge test invocation was missing its original overlay test fixture (harness error); after correcting the fixture, all seven tests passed.

## Security and execution findings
1. **R05-01 ACE_HOST_OPEN:** ACE adapter is runnable in a separate isolated Python interpreter, producing inert `authority=NONE`, `trust=UNTRUSTED_INPUT`, `native_project_binding=null`. Current plugin does not register a verified executor and cannot yet claim this capability.
2. **R05-02 COST_HOST_OPEN:** `REFERENCE_GUARD.decide()` evaluates only reference flags. Replaying the same approval flags yields another allow decision. Atomic consumption, trusted cost evidence, expiry, provider identity and spending readback must be enforced inside the actual privileged host boundary, not in chat or imported files.
3. **R05-03 IMPORT_CONSENT_ISOLATION_PASS:** Imported ACE metadata and in-chat embedded triggers remain untrusted; cannot authorize actions or upgrade foreign native authority.
4. **R05-04 WINDOWS_HOST_OPEN:** Linux is not a Windows WinForms, PowerShell, batch, Portable or Setup acceptance environment. TS-01 source release remains `0.87.6`, host tests still required.

## Next safe execution
- Verify whether this App-backed plugin offers an actual authorized code executor at the relevant action boundary; do not infer one from Markdown skills.
- If verified, execute ACE import with explicit attachment bytes through the actual host, read back import output and negative tests in a fresh chat.
- Integrate Cost Consent only at identified privileged external call points, with exact pricing proofs and one-time approval store; otherwise block chargeable operations.
- Execute ToolStarter on a real Windows host with safe fixture, capture actual exit status/log and artifact readback.

## Scope and status
Read-only plugin inspection; repository evidence-only project documentation. No plugin update, native cross-system activation, foreign writes, paid calls or secret publication.

`SOURCE_VERIFIED · LOCAL_33/33_PASS · ACE_HOST_OPEN · COST_HOST_OPEN · WINDOWS_HOST_OPEN`
