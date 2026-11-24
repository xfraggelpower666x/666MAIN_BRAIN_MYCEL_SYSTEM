# L.Y.V.R.A. CODING PROFI — Native Development Workspace

Status: LIVE_WORKSPACE_SOURCE / PLUGIN_RELEASE_SEPARATE

This is the permanent, Git-managed **development workspace** for the existing L.Y.V.R.A. CODING PROFI ChatGPT plugin. It is **not** a second plugin, a new native authority, a Python application, or an Electron desktop application.

## Identity and boundaries
- Plugin ID: `plugins_6af753996b5c81918daadc40df266ce7`
- Plugin name: `sceeri-intelligence`
- Last independently read plugin version: `0.87.7`
- Last independently read plugin release: `pluginrel_6b044ff155b481918869cf4d8f68d807`
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

## Three-layer Coding Profi / CodeForge Alliance R03 (2026-11-25)
- **Authority (one):** Installed L.Y.V.R.A. CODING PROFI plugin, release and permissions remain the primary plugin authority. No second runtime or native identity is created.
- **Live development:** This `PROJECTS/LYVRA_CODING_PROFI/` project, with CodeForge Alliance as a subordinate coordination and engineering function (not an autonomous agent/controller).
- **Unpacked live backup:** `PROJECTS/666_CODEFORGE_ALLIANCE/CODING_PROFI_LIVE/` mirrors the complete development subtree by identical Git tree SHA, including all source files. It is not ZIP, not the primary code owner and not a plugin release.
- **Mandatory per-update sync:** Every authorized Coding Profi source change must update the mirrored tree in the same scoped commit and verify both Git trees after publication. Actual plugin release evolution remains independently governed.
- **Auto-sync limitation:** Repository-internal snapshot publication and readback are verified per commit; a cross-repository/plugin event hook is not installed. Unobserved edits outside this update path must be marked BACKUP_SYNC_PENDING until reconciled.
- **R03 details:** `integration/live_backup_r03/README.md` and the backup's `LIVE_BACKUP_STATUS_R03.json`.

## Live backup role (2026-11-25)

The original installed CODING PROFI plugin is the **sole plugin authority and execution location**. This existing GitHub folder remains a useful development/evidence workspace but its `plugin_source/` subtree is an **unpacked, release-bound LIVE BACKUP**, not a second authority, independent plugin, or executable host. The three ordered phases for every authorized plugin change are: (1) original plugin work, (2) guarded publish + live plugin readback, (3) matching GitHub source mirror update + SHA/commit readback. If the third phase fails, report `BACKUP_SYNC_PENDING`. No ZIP is used as the repository backup. See `plugin_source/references/coding-profi-live-backup.md` and `SOURCE_CURRENT.md`.
