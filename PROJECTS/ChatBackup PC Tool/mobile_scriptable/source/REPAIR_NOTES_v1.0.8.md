# Repair Notes — v1.0.8

## Goal

Close every non-hardware-dependent open point after v1.0.6 without weakening or replacing any existing parser family.

## Additive repair

- Added **Diagnostics / Self-Test** to the native Scriptable menu.
- Added seven-check offline runtime self-test covering Flight, SSR, image assets, fail-closed identity, manual parsing, source fingerprinting and Scriptable file write/readback.
- Added **Public Share Probe** that performs source fetch + parser compatibility analysis without creating a backup.
- Probe reports parser family, source marker fingerprint, message/participant/image counts and error state.
- Self-test and probe reports are written with immediate app-level readback and copied to clipboard.
- Preserved React-Flight, SSR raw source, fetched-source WebView, live WebView, manual/private, group-chat, image and export paths.
- Preserved EN/DE settings and existing schemas.

## Honesty boundary

`SCRIPTABLE_FILE_WRITE_READBACK` proves the Scriptable FileManager API wrote and immediately read the same bytes. It does not prove remote iCloud server synchronization.

A real iPhone execution remains the only valid way to promote `IPHONE_SCRIPTABLE_RUNTIME_READBACK` from PENDING to PASS.


## v1.0.8 additive repair
- Added one-step `Run host acceptance` under Diagnostics / Self-Test.
- Acceptance performs live public-share fetch, current parser selection, Markdown/JSON/JSONL/Structure/source-fingerprint export, exact FileManager readback and message-count readback.
- Writes `host_acceptance_receipt.json` with schema `666.chatbackup.host-acceptance.v1`.
- Existing offline self-test, share probe, public import, manual/private, group and image paths preserved.
- Real iPhone PASS is intentionally not claimed until the real device emits `HOST_ACCEPTANCE_PASS`.
