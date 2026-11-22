# R17 Cyber GUI Repair — Audit & Handoff

## Source
R16 Cyber Hover Overlay ZIP, current-local archive; no native repository mutation.

## Confirmed screenshot findings
- B-01: Windows-native ttk theme renders near-white text on white buttons; previous `_set_theme` only configured `ttk` style values and did not select a theme respecting them.
- B-02: Excessively expanded blank list area; window layout did not separate list and footer visually.
- B-03: Bottom-right apply control clipped by single overfull horizontal packing.
- B-04: Footer settings placed in long horizontal rows, no responsive layout.
- B-05: Windows-native checkbuttons inconsistent with neon palette.

## Changes
- `src/klrw/drive_workspace_window.py`: explicit dark `clam` ttk styles, themed neon action buttons, split header/list/footer, embedded scrollbar (no absolute coordinates), adaptive settings groups that stack below 990px, scroll wheel in list. No changes to measurement, live data, tray, hotplug, settings parsing, or LED logic.
- `tests/test_r17_cyber_gui_layout.py`: responsive breakpoint, scrollbar contract and action visibility checks.

## Verification
- Python pytest with `PYTHONPATH=src`: 282/282 PASS (279 existing + 3 new) on Linux, headless.
- Python compileall: PASS.
- Windows Tk rendering / different display scales / GUI clickability: READBACK_PENDING. `clam` minimizes native theming differences, but must be checked on real Windows.
- Keyboard USB-HID: remains disabled pending device-specific verification.

## Windows acceptance
1. Extract into separate folder, preserve previous R16 installation.
2. Run `START_WINDOWS_MENUE.bat`, select E.
3. Confirm dark buttons (Speichern, Overlay zeigen, Jetzt neu erkennen, Einstellungen anwenden) are legible and responsive to clicks.
4. Resize window between narrow 720px and normal desktop width, check settings stack and remain fully accessible.
5. Scroll a list of 10+ volumes, check actual tray and overlay remain operational.
6. Confirm hotplug detection and saved `drive_workspace.json` remain intact.

Status: LOCAL STATIC VERIFIED / WINDOWS UI READBACK_PENDING / NO PUBLISH.
