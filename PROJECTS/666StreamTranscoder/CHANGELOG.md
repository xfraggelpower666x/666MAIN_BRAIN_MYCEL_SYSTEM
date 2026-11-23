# 666StreamTranscoder v3.0 — Changelog

## R05 — 2026-11-23 — Resin 3 Cyber Stream Control Engine

- Split active runtime responsibilities into InputRouter, RelayController, EncoderEngine and OutputEngine adapters while preserving the existing 3DX PCMSource, FFmpeg and protocol implementations.
- Added independent transmitted-stream gain (0–200%) and local monitor gain/device selection (0–100%).
- Added separate pre-stream-gain INPUT and post-stream-gain OUTPUT peak meters in dBFS.
- Added a thread-safe connection watch with target, last activity, byte counters and last error.
- Added bounded exponential reconnect backoff for both failed logins and established-socket send failures, retaining the existing max-retries setting and 0=unlimited behavior.
- Added active component-state events for source, encoder, server, relay and monitor; the Tk status LEDs consume those events.
- Added direct monitor routing to available PortAudio outputs, including virtual-cable playback endpoints where installed.
- Added focused control-plane tests. Execution remains open pending a suitable Python/Windows runtime.

## R04 — 2026-11-23 — PCM crossfade, relay input and Resin 3 modules

- Added automatic 3–15 second finite-queue PCM crossfade (default 8 seconds).
- Skip requests the same transition when the next decoded queue source is prepared.
- Extended finite-source decode buffering while preserving short live-source buffering.
- Added direct HTTP(S) internet-radio relay input through the existing FFmpeg and output pipeline.
- Added independent local monitor playback, volume and monitor-only Stop.
- Added SOURCE / MONITOR / ENCODER / SERVER / RELAY / ERROR status indicators.
- Added Resin 3 adapters for source capture, stream input, MP3 encoder construction, Icecast/Shoutcast outputs, relay lifecycle, local monitor, status bus and UI status model.
- Added focused unit tests for crossfade PCM and Resin 3 module contracts. Execution is still open.

## R03 — 2026-11-23 — preserved 3DX source baseline

- Created the dedicated `PROJECTS/666StreamTranscoder/` project directory.
- Copied the complete 3DX Radio Streamer 1.3.0 source tree without removing original modules.
- Retained a byte-identical source snapshot in `legacy/3dx-radio-streamer-1.3.0/`.
- Updated the active `radiostreamer/theme.py` palette to neon cyan, neon pink, neon purple and neon yellow accents.
- Preserved original build scripts, requirements, docs, tests, icons, license and third-party notices.
