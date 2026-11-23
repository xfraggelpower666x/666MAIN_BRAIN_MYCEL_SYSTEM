# Architecture and preservation rules

## Protected base

The 3DX Radio Streamer 1.3.0 remains the runtime base. The source tree is preserved under `legacy/3dx-radio-streamer-1.3.0/` and mirrored into the active project layout.

## Additive extension boundaries

- Audio engine: preserve the existing continuous encoder and stream connection.
- Playlist: retain current queue ordering, shuffle, loop, play-next, and skip semantics.
- Crossfade: mix decoded PCM from current and prepared next source; never restart the encoder or network connection.
- Skip: request a crossfade, not abrupt source termination.
- Microphone: preserve mic gain and ducking, and mix after track crossfade.
- Monitoring: local monitor lifecycle must not control broadcast lifecycle.
- Theme: palette-only change in the first visual step; no layout or workflow replacement.
- Resin 3: new capabilities must be isolated and integrated through documented adapters.

## Crossfade acceptance criteria

- Duration setting constrained to 3–15 seconds; default 8 seconds.
- Automatic crossfade for finite local/decoded queue tracks when the next track is ready.
- Skip starts the same configured transition immediately.
- A single transition can be active at a time; repeated skip requests are coalesced.
- If the next source is unavailable, keep the current track and stream alive.
- Live input sources are not crossfaded as finite playlist tracks.
- No encoder restart, socket reconnect, or stream format change during transition.
