# 666StreamTranscoder v3.0

**RESIN 3 · Universal Stream / Relay Engine**  
**Repository path:** `PROJECTS/666StreamTranscoder/`  
**Runtime base:** 3DX Radio Streamer 1.3.0 — preserved and extended additively.

## Preservation

The complete 3DX Radio Streamer 1.3.0 source is retained in the active project and in `legacy/3dx-radio-streamer-1.3.0/`. The original source snapshot remains untouched. Existing queue, media resolver, FFmpeg decode/encode path, Shoutcast v1/v2 and Icecast output, built-in server, Cloudflare tunnel, UPnP, WASAPI capture, app capture, input devices, microphone ducking, metadata, Last.fm, wizard, settings, tests and build scripts are retained.

## v3.0 additions in this source revision

- Automatic crossfade for finite queue tracks, configurable from 3 to 15 seconds (default 8 seconds).
- Skip requests the same crossfade into the prepared next queue source.
- The transition is mixed in the existing PCM mixer. The persistent MP3 encoder and output socket are not restarted.
- Finite-source decode buffering supports the configured transition window; live sources retain their short buffer to avoid adding latency.
- Direct HTTP(S) internet-radio relay input uses the existing FFmpeg decode and output pipeline.
- Local monitor Play/Stop and volume are independent of the outgoing relay. Stopping local monitoring does not disconnect the radio server.
- Visible SOURCE / MONITOR / ENCODER / SERVER / RELAY / ERROR indicators.
- Resin 3 separates runtime boundaries into InputRouter, RelayController, EncoderEngine and OutputEngine while delegating FFmpeg, capture and protocol primitives to 3DX.
- Independent stream gain (0–200%) is applied after the monitor tap; local monitor gain (0–100%) remains independent.
- Input and output peak meters report dBFS separately; the existing EBU R128 loudness monitor remains available for silence detection.
- Reconnect uses bounded exponential backoff (base delay from the existing setting, cap 60 seconds; max retries 0 still means unlimited).
- Local monitor output-device selection includes physical outputs and VB-CABLE endpoints exposed by PortAudio.
- Resin 3 adapters under `radiostreamer/resin3/` include input routing, relay health/watch, encoder lifecycle, output routing, signal gain/metering, status bus and local monitor.

## R06 runtime boundary and routing safety

- Added eight adapter-oriented runtime acceptance tests for input, decoder/capture delegation, persistent encoder, protocol output, relay recovery, and independent monitor/stream audio.
- Added two route-safety tests for VB-CABLE output-to-input loop prevention and physical-monitor routing.
- Monitor startup now rejects VB-CABLE feedback when the broadcast input captures CABLE Output and the local monitor targets CABLE Input; this protection does not disconnect the broadcaster.
- Validation is local to monitor startup and does not change existing stream or virtual audio device settings.
- These are source-level changes and acceptance tests, **not** evidence of a completed native Windows or live Shoutcast/Icecast run.

## Optional local monitor

The monitor uses `sounddevice` and `numpy`. Install them only if local playback is needed:

```powershell
python -m pip install -r requirements-monitor.txt
```

No audio driver is installed automatically. Existing VB-CABLE/physical device setup remains under the user's control.

## Start on Windows

1. Install Python 3.10+ (Python 3.11/3.12 recommended).
2. Install FFmpeg and ensure `libmp3lame` is available.
3. Install base dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Start:

   ```powershell
   python 666StreamTranscoder.py
   ```

   Or run `Start-666StreamTranscoder.bat`.

## Build Windows portable / installer

```powershell
powershell -ExecutionPolicy Bypass -File build\\build.ps1
```

Inno Setup 6 is required for the installer stage. Windows packaging and physical audio-device acceptance must be performed on a Windows host.

## Test commands

```powershell
python -m unittest discover -s tests -v
```

Focused crossfade, Resin 3 adapter and control-plane tests are present. They have **not** been executed in this session. Native Windows GUI, WASAPI, physical monitor output, portable build, installer and real user-owned radio-provider acceptance remain open.

## Configuration and secrets

Existing 3DX settings remain compatible. Crossfade, stream gain, monitor gain/device and relay settings are stored in the current application settings. Stream passwords stay in local user settings and must never be committed.

## Licensing

The preserved 3DX source baseline retains its original MIT license and third-party notices. Resin 3 adapter code delegates to existing 3DX primitives; it does not replace or erase their attribution.
