# R13 · Electron ↔ 3DX/Resin3 · read-only local status integration

## Authority and additive scope
Canonical project: PROJECTS/666StreamTranscoder/ on 666MAIN_BRAIN.
Source base: 9de79206d5946781609dffb1a9950287c320d692.
R12.2 design integrated from a21356366a70682d02e3cbb96d377724b5b4b118.
This update modifies only the existing 3DX GUI event pump (best-effort 1Hz read-only snapshot), adds a Resin3 status module, an Electron-only read path, tests and Windows UI-preview build metadata.
Do not infer independent LYVRA peer execution. No foreign project changes.

## Existing engine remains authoritative
The existing Python Tk GUI is the sole broadcaster and audio-process owner.
Its existing FFmpeg PCM mixer, 3DX modules, automatic crossfade, WASAPI routing, monitor, reconnection, Shoutcast/Icecast and configuration are unchanged.
The snapshot is created under the existing 3DX APP_ID user folder:
Windows: %APPDATA%/3DXRadioStreamer/desktop-status-v1.json.
No localhost network server, new decoder, process launcher or control socket is added.

## Fixed privacy contract
Schema 666.streamtranscoder.desktop-status.v1.
Allowed: timestamp_ms, pid, status, on_air, monitor_active, input_dbfs, output_dbfs and component state labels.
Forbidden: credentials, hostnames, streaming URLs, station names, playlist content, tracks, raw devices or identifiers.
Writing is atomic and at most 1Hz. Close removes the file only when it belongs to the current process.
Electron reads a hardcoded per-user path, limits file size to 4096 bytes, validates all fields, and rejects files stale over 5 seconds.
Renderer receives sanitized data only, uses textContent and bar widths, and fails closed if status is unavailable. No Electron-to-Python command channel.

## Packaging distinction
electron-ui/package.json offers a Windows *UI PREVIEW ONLY* portable and NSIS candidate.
It does NOT bundle the existing 3DX/Resin3 engine, FFmpeg, hardware drivers, or an audio installer.
The original build/build.ps1 and build/installer.iss remain the separate existing Windows audio build path.
A single complete audio-enabled Electron package remains OPEN until engine/GUI ownership and verified packaging are solved.
Never advertise this preview as an end-to-end broadcasting executable.

## Gates
- GitHub-source readback and merge gates.
- Python test_desktop_status.py and existing R07 suite.
- Electron node syntax + security test.
- Windows original GUI ↔ Electron concurrent-host telemetry, crash/restart stale detection.
- Hardware WASAPI, VB-CABLE, mic, monitor, playlist crossfade, Shoutcast/Icecast provider, full Windows EXE/Setup: PENDING.
No production feature flag or pointer is advanced until checks and source readback pass.
