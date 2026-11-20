# SOURCE MAPPING — v1.10.5

## Runtime

- `app/chatbackup_core.py` — Share parser, manual-transcript parser, export models, raw/copy/asset preservation
- `app/chatbackup_backend.py` — backend orchestration for public share loading, manual text analysis and reparse
- `app/chatbackup_gui.pyw` — bilingual Cyber-Neon GUI, Private/Manual workflow, Help, Structure Inspector, Image Browser, exports
- `app/chatbackup_gui.py` — source launcher wrapper

## Private / Manual additions

- `ChatBackend.analyze_manual_text()` -> `analyze_manual_transcript()`
- explicit English/German role-marker recovery
- safe single-message fallback without invented turns
- manual raw text preservation in `rawContent.sourceText`
- manual machine/structure exports through existing schemas
- `/c/` URL intercept to Manual Import dialog
- expanded bilingual Help with public Share, private chats, manual copy and Chat-full recovery guidance

## Preserved layers

- v1.6.0 bilingual UI and persistent language
- v1.5.x loss-aware backend, Structure Inspector and Structure JSON
- v1.4.0 Chat Image Browser and selected image export
- v1.2.1 PowerShell 5.1 encoding hardening
- v1.1.1 byte-exact long-chat readback


## v1.8.0 Group Chat Layer
- `app/chatbackup_core.py`: ChatParticipant, structured participant extraction, participant-to-message resolution, group detection, manual group transcript parsing, group-aware exports.
- `app/chatbackup_gui.py[w]`: group/participant visibility in Structure Inspector and bilingual help.
- `tests/test_core.py`: structured + manual group regression tests.


## v1.8.1 Audit/Repair Layer
- participant identity hardening in `app/chatbackup_core.py`
- assistant/custom-GPT identity preservation
- manual markdown-heading false-positive guard
- cross-file version coherence regression test

## v1.8.2 Direct Image Download Layer

- `app/chatbackup_gui.pyw` / `.py`: Einzel-/Batch-Download im Chat-Bildbrowser.
- `_fetch_chat_image_bytes`: gemeinsame Byte-Quelle für Vorschau, Portable ZIP und Direktdownload.
- `_write_binary_verified`: bytegenauer Write/Readback auch für Direktdownloads.
- Portable ZIP: echte Binärbilder in `assets/`, keine Base64-Serialisierung.


## v1.10.5 Current Mobile Companion

- `mobile_scriptable/666_CHATBACKUP_SCRIPTABLE_IPHONE_v1.0.9.zip` — current audited mobile distribution snapshot.
- `mobile_scriptable/history/` — preserved older companion packages (including v1.0.7, v1.0.6 and v1.0.0) for provenance only.
- `REPAIR_NOTES_v1.10.5.md` — current cross-platform packaging/governance contract.
- PC runtime remains Python/Tkinter; mobile runtime remains Scriptable/iOS. No runtime authority is shared implicitly.

## Preserved AUTH-Wall / Browser Recovery (introduced v1.10.0)

- `app/chatbackup_core.py` — `detect_auth_wall`, `AuthWallDetected`, explicit pre-parser gate.
- `app/chatbackup_backend.py` — `recover_browser_transcript` orchestration.
- `app/chatbackup_gui.pyw` — guided Browser Recovery UI and automatic transition from direct Share failure.
- `FEATURE_AUTH_WALL_BROWSER_RECOVERY_v1.10.0.md` — recovery contract and security boundary.


## v1.10.5 Host Acceptance Layer
- `VERIFY_WINDOWS_HOST_ACCEPTANCE.bat` — one-step Windows acceptance orchestration.
- `tests/host_acceptance_probe.py` — live/fixture Share fetch→parse→export→readback receipt producer.
- `WINDOWS_HOST_ACCEPTANCE_PROTOCOL.md` — real Windows closure contract.
- Scriptable v1.0.9 `Run host acceptance` — matching iPhone live Share export/readback receipt.
- `FREEZE_REPORT_v1.10.5.md` — strand/freeze return anchors.
