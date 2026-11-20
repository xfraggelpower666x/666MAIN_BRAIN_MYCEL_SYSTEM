# Host Readback Protocol — Scriptable v1.0.9

## Gate A — runtime self-test

On the iPhone:

1. Open `666 ChatBackup Scriptable iPhone v1.0.9`.
2. Choose `Diagnostics / Self-Test`.
3. Choose `Run offline self-test`.
4. Expected terminal state: `SELFTEST_PASS` with 7/7 checks.
5. The JSON report is copied to the clipboard and stored in the Scriptable output folder.

Only that real report can close the generic Scriptable runtime gate.

## Gate B — live share compatibility

1. Copy a public ChatGPT `/share/` link.
2. Open `Diagnostics / Self-Test`.
3. Choose `Probe public share`.
4. Expected state: `PROBE_PASS` plus a parser family and non-zero message count.
5. No chat backup is created by this probe.

A `PROBE_FAIL` report preserves source fingerprints for the next parser repair.

## Gate C — full import

Run the normal `Public Share Link` workflow and verify the resulting message count and exports. Only this closes end-to-end import readback for that share family.


## v1.0.9 one-step host acceptance

Use **Diagnostics / Self-Test → Run host acceptance** with a real public `/share/` or `/s/` URL.
The workflow performs live fetch, parser selection, Markdown/JSON/JSONL/structure/source-fingerprint export, exact FileManager readback, message-count readback and writes `host_acceptance_receipt.json`.
Only `HOST_ACCEPTANCE_PASS` produced on the real iPhone closes the iPhone runtime + real-share import/export gate.

v1.0.9 uses the same import routine for acceptance and the regular Public Share menu. The receipt records the actual path under `importPath` and the ordered gate results under `importAttempts`. Source HTML and its fingerprint are available when the direct fetch returned HTML. A successful WebView-only recovery may therefore have no raw source file.
