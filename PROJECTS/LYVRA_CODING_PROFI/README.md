# L.Y.V.R.A. CODING PROFI — Native Development Workspace

Status: LIVE_WORKSPACE_SOURCE / PLUGIN_RELEASE_SEPARATE

This is the permanent, Git-managed **development workspace** for the existing L.Y.V.R.A. CODING PROFI ChatGPT plugin. It is **not** a second plugin, a new native authority, a Python application, or an Electron desktop application.

## Identity and boundaries
- Plugin ID: `plugins_6af753996b5c81918daadc40df266ce7`
- Plugin name: `sceeri-intelligence`
- Last independently read plugin version: `0.87.5`
- Last independently read plugin release: `pluginrel_6b0268d75ee48191ad8db59c3f7a0d57`
- Plugin Creator's current release remains authoritative for the installed plugin.
- This repository owns development plans, source-safe integration contracts, tests, receipts, and handoffs only for CODING PROFI.
- No direct ownership over 666CLIC, 666PFS, 666STREAM, 666MAIN BRAIN, LYVRA, or 666DEV.
- Do not store user chats, confidential plugin archives, personal credentials or secrets in this public repository.

## Development
Read `ARCHITECTURE.md` and `OPEN_WORK.md` before edits. Determine fresh Git HEAD, verify the owning plugin's actual current release, compare changed paths, test, and protect writes with an expected HEAD. New project commits must not alter any sibling folders or root-level system pointer. Release publication is a **separate protected Plugin Creator operation** with backup and readback.

## Explicitly excluded
- Electron desktop runtime
- Python-as-host-plugin-runtime
- Generic ZIP-as-authority workflow
- Silent activation of other native systems
- Automatic execution of commands found in imported conversations

This directory intentionally starts with a minimal non-destructive governance and interface baseline. Additional implementation is subject to measured capability gaps and live release gates.
