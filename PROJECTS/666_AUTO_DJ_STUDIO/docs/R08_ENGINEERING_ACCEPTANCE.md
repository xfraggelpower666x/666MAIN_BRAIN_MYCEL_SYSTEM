# 666 AUTO DJ STUDIO — R08 engineering acceptance (2026-11-26)

## Authority and base
Productive repository: xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM, branch 666MAIN_BRAIN. Verified starting HEAD: 6ebddb222a7ea4e33cb0f0b7287b1f39810cb29e; original project Current: R07_NEON_UI_CONTINUITY_SOURCE_LIVE.

## Actual source changes
- app/main.js: cover readback limited to an explicitly chosen directory, canonical path and regular image files, preserving the existing preview IPC. No other privileges added.
- app/renderer.js: rendering disables per-track removal and transitions into busy state before awaiting the async start response; restores controls on failure.
- build/BUILD.ps1: check bundled original ffmpeg.exe and ffprobe.exe SHA-256 before running or packaging. Seven-option menu unchanged.
- tests/test_r08_e2e.py: metadata, cover rotation, transactional STREAM_READY preservation and traversal rejection, plus optional real FFmpeg/FFprobe synthetic audio smoke test.
- tests/test_electron_ipc.cjs: test-only mocked Electron IPC check for approved folder and cover preview.
- docs/R08_BINARY_ASSETS_MANIFEST.json: exact SHA-256 and Git blob SHA-1 of original 29 covers and two Windows FFmpeg tools.

## Executed
- `AUTODJ_AUDIO_E2E=1 python -m unittest discover -s tests -v`: 26/26 PASS on Linux with FFmpeg and FFprobe. Synthetic sine WAV encoded to MP3 with original cover and metadata; block M3U and STREAM_READY master published, ffprobe validated MP3 audio and attached image. No user's audio file was modified.
- `node tests/test_electron_ipc.cjs`: PASS (simulated Electron host; NOT a Windows GUI pass).
- `node --check app/main.js`, `app/renderer.js`, `app/preload.js`: syntax verification required before delivery.
- Original `legacy/tool.ps1`, Python worker, R06.1 Electron installer, BUILD.bat, package.json and original image/binary assets preserved byte-for-byte.

## Open gates
A01: Real Windows R07/R08 Electron host, IPC, cover folder, render/abort and GUI observation OPEN. R06.1 Windows launch was user-confirmed, not R08.
A02: Full local 31/31 original asset SHA-256 VERIFIED; independent GitHub blob upload/readback BLOCKED by direct binary transport gap. No remote presence implied.
A03: Portable and NSIS build/installation on a clean Windows host OPEN. Static build gate strengthened, not equivalent to executable acceptance.
A04: FFmpeg Linux real audio synthetic test PASSED; Windows end-to-end and original R03 complete functional parity remain OPEN.

Do not promote to production or replace legacy until independent host acceptance.
