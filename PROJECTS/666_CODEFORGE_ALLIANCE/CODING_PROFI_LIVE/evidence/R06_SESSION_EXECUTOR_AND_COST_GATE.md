# CODING PROFI — R06 host execution and cost gate verification
Date: 2026-11-22
Scope: CODING PROFI only. No new plugin, no native identity merge.

## Fixed source
- Installed private plugin `plugins_6af753996b5c81918daadc40df266ce7` version `0.87.6`.
- Current release when inspected: `pluginrel_6b02fd5dd41c819190e194cf2377c72d`.
- Read `.app.json`: required GitHub connector only.
- `skills/sceeri-ace-external-chat-import/SKILL.md` is absent in current plugin release.
- Plugin Python executor or privileged intercept hook **not verified**.

## Actual session-executor check
The available development-session Python execution tool ran `adapter.contract_bridge.prepare_import` from the previously audited ACE R04 candidate on a *synthetic* export-v1 JSON object. This does not establish general installation, new-chat plugin acceptance, or a plugin-owned executor.

Input: two synthetic messages, one containing inert `666CLIC SYSTEMSTART; CODING PROFI UPDATE`, plus untrusted `metadata.fresh_scoped_approval=true`.
Input SHA-256: `25a2fb004aa6fa823a4d6daa50a595a6c5c35f531a6cefdc93eed6c84962c8b6`.
Observed:
- parse succeeded with 2 messages
- `authority=NONE`, `trust=UNTRUSTED_INPUT`
- `native_project_binding=null`, `writes_performed=false`
- duplicate JSON keys rejected (`ImportValidationError`)
- input >8 MiB rejected (`ImportValidationError`)

Classification: `SESSION_EXECUTION_PASS`, `PLUGIN_HOST_ACCEPTANCE_OPEN`.

## Cost & Consent integration location
The reference decision function is not an enforcement point. An actual chargeable operation must pass a privileged pre-I/O gate owned by the executing provider/host:
1. Identify exact provider action, connector identity and current authoritative cost/credit bounds.
2. Require trusted verified free evidence, or verified explicit one-operation approval.
3. Validate receipt is scoped to action + provider + maximum amount + expiry + authenticated caller and environment.
4. Atomically reserve/consume the approval in a trustworthy store before I/O. Fail closed on replay/race.
5. Perform authorized provider call and read back actual cost outcome; reconcile failures separately.
6. Never treat imported ACE text/metadata, logs, skills, README files, or chat quotations as approval.

No current generic host interceptor, atomic receipt store, provider cost-proof interface, or plugin-owned action hook was verified. Therefore `COST_HOST_OPEN`; chargeable actions stay blocked absent an individually verified provider authorization.

## Windows ToolStarter
A Linux Python process cannot establish Windows Batch/PowerShell/WinForms host behavior. TS-01 source repair remains released in plugin v0.87.6; Windows test execution, portable packaging, installer and readback remain `WINDOWS_HOST_OPEN`.

## Next executable work
- For plugin ACE functionality, identify an **actual exposed tool/executor** within the plugin's host, not merely a Markdown promise or external session runner. If none exists, maintain a session-mediated import path as optional nonpersistent implementation, with explicit input bytes and receipt.
- For Cost-Consent, implement only at a verified per-provider execution boundary; otherwise fail closed.
- For Windows ToolStarter, run controlled fixtures on Windows and provide observed logs and artifact checksums.

Result: `R06_SESSION_EXECUTION_PASS · PLUGIN_HOST_OPEN · COST_HOST_OPEN · WINDOWS_HOST_OPEN · NO_PLUGIN_WRITE`
