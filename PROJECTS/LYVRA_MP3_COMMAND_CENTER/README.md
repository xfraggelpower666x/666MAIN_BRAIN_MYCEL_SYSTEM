# LYVRA MP3 COMMAND CENTER R01
Integration candidate, not a production promotion. Main screen MP3 Manager; Auto DJ and Restoration as tools. Single fullscreen Electron shell, original Universal Boot image, minimum eight seconds after visible boot, real dependency checks. Original archive sources remain separate and byte-preserved locally.

## Start (Windows, source mode)
1. Python 3.11+, Node/npm and FFmpeg/FFprobe installed locally; no automatic downloads or deployment.
2. From this directory: `python tools/import_sources.py C:\path\to\four\archives` (exact uploaded archive names and hashes pinned).
3. `python -m venv .venv` then `.venv\Scripts\python.exe -m pip install -r requirements.txt`; set LYVRA_PYTHON to absolute virtualenv python path.
4. Ensure ffmpeg and ffprobe on PATH; original MP3 bridge may also locate bundled tools. Run `npm install`, `npm run check`, `npm start`.
5. No packaged runtime or Windows installer is claimed for R01.

## Scope and limitations
New adapter code is published as text. The original four uploaded archives are not replicated into this public repository by this revision; import tool requires the original archives locally. Original UI and engine files remain intact; imported original programs remain independently runnable. MP3 inspect, export MP3/WAV, three ID3 fields, DJ basic rendering/M3U and Restoration WAV modes have adapter implementations, not host acceptance. Full original UI parity, advanced DJ block/cover/metadata and stream-ready functions, Restoration advanced controls/preview, second monitor, safe DJ/Restoration cancellation, installer and Windows no-console verification are OPEN. Electron 35.7.5 retained for source compatibility, security/version review required before production. No current pointer. No source deletion, no deployed services.

## Audit
MP3 C02 engine_bridge.py imports original media_tools via explicit sibling directory; worker uses JSON lines, CANCEL on stdin. Auto DJ worker.py imports legacy_media, legacy_planner, master_export, playlist; takes one JSON payload and FFmpeg arguments. Restoration Windows audio_input.py, realtime.py and reference_engine.py use local DSP imports; separate subprocess avoids colliding with embedded Restoration copy. Shared Python constraints match requirements.txt; original GUI depends on Tkinter. Universal Buildkit electron/main.js has local HTTP backend healthcheck; R01 reuses boot art but substitutes direct process probes because workers have no HTTP API. Full Lyrics Intelligence reference main.cjs and INSTALL_ELECTRON_RUNTIME.ps1 read at branch 666MAIN_BRAIN; runtime installer fallback is not yet integrated. R01 requires no cross-system merge.
