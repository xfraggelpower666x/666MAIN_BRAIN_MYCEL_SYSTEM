# R12 · 666StreamTranscoder v3.0 · Electron Cyber-Neon UI

Status: SOURCE PREVIEW ONLY / ENGINE INTEGRATION OPEN / WINDOWS HOST OPEN.
Owner of this project: 666StreamTranscoder in 666MAIN_BRAIN_MYCEL_SYSTEM, branch 666MAIN_BRAIN.
Proposed technical coordination: LYVRA Coding Profi (planning/review); no activation or authority takeover of peer plugins.

## Decision (2026-11-24)
Adopt a modern Electron presentation layer **additively**. Existing 3DX Radio Streamer 1.3.0 and Resin 3 Python audio/broadcast runtime remain the authoritative engine. No replacement of Tkinter, tests, settings, capture/IMMDevice logic, FFmpeg, SHOUTcast/Icecast, mic/ducking, crossfade, Last.fm, integrations, original assets or Windows scripts.

## Delivered in R12
- `electron-ui/`: offline visual prototype with Broadcast, Routing, Playlist and Diagnostics surfaces.
- Explicit preview/offline semantics; all live controls disabled and no fabricated audio meters or device status.
- Electron BrowserWindow with contextIsolation, sandbox, no nodeIntegration, navigation guards and a deliberately tiny read-only preload.
- Does **not** start the Python engine, alter stream settings or use remote resources.
- Does not replace working 3DX UI. Optional start: `cd electron-ui && npm install && npm start` (Node/npm required; installation requests normal user consent).
- `npm run check` validates JavaScript syntax. Successful check does not prove Windows rendering.

## Required next acceptance
1. Define versioned IPC messages and strict contracts for read-only statuses; no arbitrary Python execution from renderer.
2. Implement supervised Python sidecar/IPC from the **existing** 3DX/Resin 3 runtime. No second audio engine, stream process or audio ownership.
3. Bind real source/monitor/encoder/server/relay/error states and measured dBFS values; fail closed on disconnect.
4. Route user actions via authenticated/validated command whitelist, explicit OFF AIR safety, settings compatibility, safe device mapping and no silent fallback.
5. Verify auto crossfade 3–15 s and skip, encoder persistence, provider reconnect, monitor independence, WASAPI/IMMDevice, VB-CABLE loop guard.
6. Build a real Windows bundle containing Electron + Python backend + FFmpeg and licenses (portable and NSIS/installer), preserve existing 3DX PyInstaller/Inno paths until real parity.
7. Windows cold start, restart, hotplug, provider and acceptance receipts. No claim of EXE/Setup completion before byte/hash/artifact and Windows host readback.

## Full Lyrics Intelligence R06.1 reuse boundary
Read its current `electron/main.cjs`, `electron/preload.cjs`, and `package.json` for methods (secure BrowserWindow, constrained preload, packaged Python runtime and NSIS). Do not copy its catalog commands or private data into this system. Peer source is reference, not native authority.

## Non-destructive invariant
`3DX_AUDIO_CORE_PRESERVED=true`
`RESIN3_PRESERVED=true`
`ELECTRON_UI_OPTIONAL=true`
`LIVE_AUDIO_ENGINE_IN_ELECTRON=false`
`NO_CROSS_SYSTEM_MERGE=true`
`HOST_ACCEPTANCE_PENDING=true`
