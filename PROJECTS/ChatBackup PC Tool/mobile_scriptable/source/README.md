# 666 ChatBackup Scriptable iPhone v1.0.9

Variant-tolerant Scriptable companion for ChatGPT shared conversations with on-device diagnostics.

## Import architecture

1. Structured React-Flight / legacy source parser
2. Direct raw-HTML SSR transcript parser
3. Fetched-source WebView recovery
4. Live WebView DOM recovery
5. Manual clipboard import

The direct SSR parser recognizes the server-rendered transcript family without requiring WebView rendering:

- `data-conversation-transcript`
- `data-message-role="assistant|user"`
- `data-assistant-markdown-root`
- `data-assistant-markdown`
- `data-user-message-copy`
- `data-submit-message-animation-target`

The existing React-Flight, legacy, manual/group, image and export paths remain preserved.

## Diagnostics / Self-Test

The main menu now contains **Diagnostics / Self-Test**.

### Offline self-test

Runs locally on the iPhone and checks:

- React-Flight fixture parsing
- SSR source fixture parsing
- SSR HTTP image extraction
- fail-closed user identity
- manual transcript reconstruction
- source fingerprinting
- Scriptable `FileManager.iCloud()` write/readback through the app API

The report is saved under the Scriptable output folder and copied to the clipboard. This verifies the Scriptable runtime path when executed on the actual device; it does not claim remote iCloud synchronization.

### Public share probe

Fetches one public `/share/` or `/s/` URL, fingerprints the delivered source and tries the structured/source parsers **without creating a chat backup**. The JSON report includes parser, message count, participant count, image asset count and source markers.

## Identity safety

A `data-message-role="user"` marker confirms a user role, not a real-world identity. If the source provides no participant name or ID, participant resolution remains `UNRESOLVED`.

## Images

Direct HTTP(S) images found in structured data or SSR message markup are retained as downloadable assets. Internal/non-public pointers remain metadata only.

## Runtime gate

Static/source regression is complete. Final iPhone platform PASS still requires a self-test or real import report produced by Scriptable on the user's iPhone.


## Host acceptance
`Diagnostics / Self-Test → Run host acceptance` runs the complete public-share import/export/readback chain and stores a machine-readable receipt. It does not claim PASS until the real iPhone returns `HOST_ACCEPTANCE_PASS`.

For v1.0.9, `Run host acceptance` uses the same direct-source and WebView paths as the public-share menu. The receipt identifies the selected path under `importPath`.
