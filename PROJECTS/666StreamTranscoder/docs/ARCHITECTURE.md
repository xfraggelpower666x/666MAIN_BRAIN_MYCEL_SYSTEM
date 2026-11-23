# Architecture and preservation rules

## Protected base

The 3DX Radio Streamer 1.3.0 remains the runtime base. The source tree is preserved under `legacy/3dx-radio-streamer-1.3.0/` and mirrored into the active project layout.

## Additive extension boundaries

- Audio engine: preserve the existing continuous encoder and stream connection.
- Playlist: retain current queue ordering, shuffle, loop, play-next, and skip semantics.
- Crossfade: mix decoded PCM from current and prepared next source inside the existing mixer; finite-source buffering supports up to 15 seconds; never restart the encoder or network connection.
- Relay source: direct HTTP(S) stream input enters the existing PCM decoder and encoder path.
- Local monitor: a separate sounddevice sink receives post-mix PCM; its Stop control must not call Broadcaster.stop() or drop the output socket.
- Resin 3 adapters delegate to preserved 3DX primitives instead of duplicating the streaming stack.
- Skip: request a crossfade, not abrupt source termination.
- Microphone: preserve mic gain and ducking, and mix after track crossfade.
- Monitoring: local monitor lifecycle must not control broadcast lifecycle.
- Theme: palette-only change in the first visual step; no layout or workflow replacement.
- Resin 3: new capabilities must be isolated and integrated through documented adapters.

## Resin 3 control-plane boundaries

- InputRouter owns source selection and delegates to the preserved PCMSource, FFmpeg decoder and 3DX capture implementations.
- RelayController owns connection state, retry limits, exponential backoff and last-output-activity counters.
- EncoderEngine owns the one persistent FFmpeg MP3 encoder process.
- OutputEngine owns protocol connection, encoded-byte send and socket close through the existing Shoutcast/Icecast protocol adapters.
- Stream gain is applied after the monitor tap. Local monitor gain and selected PortAudio output affect only local listening.
- Input peak meter is measured after source/microphone mixing and before stream gain; output peak meter is measured after stream gain and before MP3 encoding.
- The UI receives component state events for source, encoder, server, relay and monitor. Status display is not the execution authority.

## Signal route matrix

| Input | Runtime path |
|---|---|
| Playlist / files | Existing media resolver → FFmpeg PCM |
| Device / VB-CABLE | Existing FFmpeg device input |
| WASAPI loopback | Existing 3DX LoopbackCapture → FFmpeg PCM |
| WASAPI app capture | Existing 3DX AppCapture → FFmpeg PCM |
| HTTP(S) radio | Existing stream URL parser → FFmpeg PCM |

| Output | Runtime path |
|---|---|
| Shoutcast v1/v2 | Existing source protocol adapter |
| Icecast 2 | Existing HTTP PUT source protocol adapter |
| Built-in | Existing local listener server |
| Physical / VB-CABLE monitor | Optional PortAudio output sink, separate from relay |

## Crossfade acceptance criteria

- Duration setting constrained to 3–15 seconds; default 8 seconds.
- Automatic crossfade for finite local/decoded queue tracks when the next track is ready.
- Skip starts the same configured transition immediately.
- A single transition can be active at a time; repeated skip requests are coalesced.
- If the next source is unavailable, keep the current track and stream alive.
- Live input sources are not crossfaded as finite playlist tracks.
- No encoder restart, socket reconnect, or stream format change during transition.
