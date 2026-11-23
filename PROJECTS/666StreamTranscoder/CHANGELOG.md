# 666StreamTranscoder v3.0 — Changelog

## R10 — 2026-11-23 — Device identity and fault-injection routing

- Added PortAudio monitor output descriptors with host API, enumerated device index
  and exact name readback before opening output. Duplicate legacy names fail closed.
- Added indexed WASAPI loopback selection with explicit stale/ambiguous device rejection.
  Compatible unambiguous legacy device names remain supported.
- Updated GUI refresh to preserve old selections and safely migrate unique legacy names
  without silently choosing another output.
- Strengthened virtual-cable feedback guard to distinguish standard and A/B/C/D cables.
- Added device identity, local monitor isolation, reconnect and real local socket-failure
  regression tests to the project-scoped CI gate.
- Protected 3DX original source snapshot and existing stream protocol implementation unchanged.
- Windows hardware endpoint ID / hotplug and live Icecast/Shoutcast provider acceptance remain open.

## R09 — 2026-11-23 — FFmpeg resource lifecycle repair

- PCMSource.close now guards repeated calls, stops the decoder, performs bounded reader-thread joins and explicitly closes stdin/stdout/stderr.
- EncoderEngine.stop explicitly terminates the encoder, joins its output/error readers and releases its process pipes.
- Broadcaster.stop delegates encoder cleanup to the Resin 3 lifecycle owner.
- Added five focused pipe-lifecycle regression tests and a dedicated CI gate.
- Crossfade, source routing, local monitor, original 3DX features and codec settings remain unchanged.
- Windows/WASAPI/physical monitor and remote provider acceptance remains open.

## R08 — 2026-11-23 — Isolated real-audio end-to-end acceptance

- Added two synthetic WAV-to-MP3-to-HTTP tests exercising real FFmpeg and the original 3DX built-in streaming server.
- Tests cover automatic crossfade and user Skip crossfade, encoder process continuity, same HTTP listener, decoded audible output, and fatal-error absence.
- Network binding is forced to loopback using the original LocalServer, without public radio services, credentials, drivers or external provider traffic.
- The project-scoped GitHub Actions workflow now includes real local end-to-end streaming alongside its existing 26 Python unit/contract tests.
- Windows WASAPI, physical monitor devices, online providers and installers remain separate acceptance gates.

## R06 — 2026-11-23 — Runtime boundary contracts and safe virtual-cable routing

- Added ten new focused runtime-boundary/route tests with mocked FFmpeg/process/device/network boundaries.
- Coverage includes InputRouter device/WASAPI/HTTP relay, single EncoderEngine process, OutputEngine protocol/send/close, RelayController reconnect lifecycle, stream-versus-monitor gain, and monitor Stop isolation.
- Added virtual cable feedback-route guard to prevent monitoring to CABLE Input while capturing CABLE Output from the same cable; physical monitor devices remain selectable.
- Preserved the existing 3DX source baseline, protocol handlers, encoder, mixer, UI and build scripts.
- Native Windows hardware, real network/provider acceptance and executable test receipts remain open.

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
