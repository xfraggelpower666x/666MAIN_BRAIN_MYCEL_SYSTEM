# Feature — Scriptable iPhone Companion bundled with PC Tool v1.9.0

## Purpose

Ship the PC application and an independently usable iPhone/Scriptable companion together without merging their runtime authorities.

## Mobile capabilities

- native guided Scriptable UI using Alert, UITable, WebView, QuickLook and ShareSheet
- English default; persistent English/German selection
- public ChatGPT share-link import
- private/manual clipboard transcript analysis
- group-chat participant preservation and fail-closed unresolved identity
- structure browser and structure JSON
- Markdown / JSON / JSONL / JavaScript exports
- direct image preview and binary download for reachable HTTP(S) assets
- raw-source preservation when available
- bilingual help, including private chats and the observed non-guaranteed "chat full" share-window workaround

## Packaging

The exact audited mobile ZIP is embedded at:

`mobile_scriptable/666_CHATBACKUP_SCRIPTABLE_IPHONE_v1.0.0.zip`

The same ZIP is also delivered separately.

## Important platform difference

Scriptable has no native ZIP writer. The mobile `All Formats + Source Folder` workflow creates a portable iCloud folder; the iOS Files app can compress that folder if a ZIP is required. This does not affect the distribution ZIP created on the development host.
