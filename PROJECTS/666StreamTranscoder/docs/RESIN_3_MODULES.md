# Resin 3 module map

Resin 3 is implemented as adapters around the preserved 3DX Radio Streamer 1.3.0 runtime. It does not create a second encoder, duplicate output protocol stack or replace the existing broadcast engine.

## Runtime control boundaries

- `input_router.py`: selects playlist/device/WASAPI/app/HTTP(S) relay input and creates the existing PCMSource.
- `relay_engine.py`: RelayController owns reconnect policy, connection health and output activity counters; RelaySession keeps monitor and relay lifecycle distinct.
- `encoder_engine.py`: starts the one persistent MP3 encoder process.
- `output_engine.py`: opens, writes and closes the existing Shoutcast/Icecast output socket through the protocol router.
- `control_plane.py`: independent stream gain, peak dBFS metering, route description and bounded exponential reconnect policy.

## Active integration points

- `source_audio.py`: delegates device/app/loopback capture creation to the preserved 3DX capture implementation.
- `source_stream.py`: validates HTTP(S) relay URLs and delegates FFmpeg input arguments to the existing media module.
- `encoder.py`: builds the persistent MP3 encoder command used by the existing Broadcaster.
- `output_icecast.py` / `output_shoutcast.py`: protocol-specific adapters around the existing source-connection implementation.
- `output_router.py`: selects the correct adapter from the existing server setting.
- `monitor_engine.py`: optional independent local playback sink. It receives post-mix PCM and can be stopped without touching the relay socket.
- `relay_engine.py`: RelayController owns retry backoff and connection activity; RelaySession keeps monitor and relay lifecycle distinct.

## Status and UI support

- `status_bus.py`: thread-safe component status events and snapshots.
- `ui_main.py`: UI-facing LED state model.
- The active Tk GUI displays SOURCE, MONITOR, ENCODER, SERVER, RELAY and ERROR indicators and exposes local monitor Play/Stop, volume and output-device selection.
- The broadcast panel shows independent INPUT and OUTPUT peak meters in dBFS plus a transmitted-stream gain control.
- The server status line shows retry state, retry count and time since the last encoded output packet.

## Optional local monitor dependencies

Install only when local monitor playback is needed:

```powershell
python -m pip install -r requirements-monitor.txt
```

## Signal routes

- Input: playlist/file media, direct device capture, WASAPI system loopback, WASAPI process loopback, HTTP(S) radio relay.
- Virtual cable input: select the Windows `CABLE Output` capture endpoint in the device input list.
- Output: existing Shoutcast v1/v2, Icecast 2 or the built-in local server.
- Local monitor: select a PortAudio output device; the VB-CABLE playback endpoint is typically listed as `CABLE Input`.
- Stream gain is applied after the local monitor tap. The monitor's own gain is applied only by its local playback sink.

## Preservation rules

- Existing 3DX queue, media resolution, Shoutcast/Icecast protocol code, local server, tunnel, UPnP, metadata, microphone ducking and build workflows remain the runtime authority.
- Stopping the local monitor must never call `Broadcaster.stop()`.
- Disconnecting the relay is an explicit broadcast lifecycle action.
- No VB-CABLE driver or embedded Python runtime is installed or copied automatically.
- The Resin 2.0 archive remains historical reference material; no missing Resin source files are fabricated into this project.
