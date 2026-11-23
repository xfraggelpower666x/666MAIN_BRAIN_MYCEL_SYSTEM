# Import and implementation status

## Source baseline

- `VERIFIED`: 3DX Radio Streamer 1.3.0 source imported into `PROJECTS/666StreamTranscoder/`.
- `VERIFIED`: 43 original files also retained under `legacy/3dx-radio-streamer-1.3.0/`.
- `VERIFIED`: original engine, GUI, capture, protocol, media, integrations, wizard, tests, assets and build files are present in the active project.
- `VERIFIED`: active theme palette updated to neon cyan, pink, purple and yellow accents.

## R05 Resin 3 Stream Control Engine

- `IMPLEMENTED`: active InputRouter / RelayController / EncoderEngine / OutputEngine boundaries.
- `IMPLEMENTED`: independent 0–200% stream gain after the local-monitor tap.
- `IMPLEMENTED`: independent 0–100% local monitor gain and PortAudio output selection.
- `IMPLEMENTED`: input and output peak meters in dBFS.
- `IMPLEMENTED`: connection activity watch, byte counters, last error and exponential reconnect backoff.
- `IMPLEMENTED`: source/encoder/server/relay/monitor component-state events connected to the Tk status LEDs.
- `IMPLEMENTED`: route selection for playlist, direct input/virtual cable, WASAPI loopback, WASAPI app capture, HTTP(S) relay, Shoutcast, Icecast and local monitor output.

## v3.0 code added in R04

- `IMPLEMENTED`: PCM crossfade helper and mixer transition path for finite queue tracks.
- `IMPLEMENTED`: 3–15 second crossfade setting; default 8 seconds.
- `IMPLEMENTED`: Skip requests a fade to the prepared next queue item.
- `IMPLEMENTED`: HTTP(S) relay input using the existing FFmpeg PCM and encoder pipeline.
- `IMPLEMENTED`: independent local monitor sink, volume and monitor-only Stop.
- `IMPLEMENTED`: SOURCE / MONITOR / ENCODER / SERVER / RELAY / ERROR status indicators.
- `IMPLEMENTED`: initial Resin 3 adapters under `radiostreamer/resin3/`.

## R06 boundary and routing protection

- `IMPLEMENTED`: runtime-boundary tests cover input, encoder, output and relay adapter handoffs.
- `IMPLEMENTED`: guard against a VB-CABLE monitoring feedback loop.
- `OPEN`: tests are present but have not been executed against a Windows device/network runtime.
- `OPEN`: actual end-to-end input → PCM mix → encoder → Icecast/Shoutcast provider acceptance.

## R11 Windows IMMDevice identity extension

- `IMPLEMENTED`: Windows MMDeviceEnumerator COM-based render endpoint ID
  enumeration and unique mapping to existing PortAudio/PyAudioWPatch routes.
- `IMPLEMENTED`: stable `IMM:` selections and explicit rejection of
  stale/ambiguous endpoint mappings, preserving R10 legacy selections.
- `IMPLEMENTED`: 10 new identity tests, Windows CI smoke job,
  read-only Windows host inventory and hardware acceptance protocol.
- `OPEN`: native CI receipt and direct Git readback must be checked.
- `OPEN`: physical capture/monitor/audio hardware, hotplug, owned
  Shoutcast/Icecast endpoint and Windows EXE/installer acceptance.

## R10 routing identity and real local socket failure

- `SOURCE IMPLEMENTED`: exact PortAudio index, host API and name validation for local monitor output.
- `SOURCE IMPLEMENTED`: indexed WASAPI loopback selection, legacy name compatibility
  and explicit stale/duplicate device failures rather than silent fallback.
- `SOURCE IMPLEMENTED`: standard and A/B/C/D VB-CABLE loop-protection differentiation.
- `TESTS ADDED`: 15 focused tests including an actual socketpair disconnect/reconnect.
- `OPEN`: execution readback and CI acceptance pending publication.
- `OPEN`: persistent Windows IMMDevice IDs, physical device hotplug and provider connections.

## R09 resource lifecycle repairs

- `SOURCE IMPLEMENTED`: explicit FFmpeg decoder and encoder pipe cleanup.
- `SOURCE IMPLEMENTED`: idempotent PCMSource.close and bounded worker joins.
- `TESTS ADDED`: five process/pipe regression cases.
- `READBACK_PENDING`: validate GitHub Actions R09 tests, real local FFmpeg crossfade, warnings and live branch before promoting to VERIFIED.
- `OPEN`: Windows WASAPI/device/provider/installer validation remains separate.

## R08 isolated real-audio integration gate

- `IMPLEMENTED`: two synthetic end-to-end tests using real FFmpeg, the existing 3DX local server, a persistent MP3 encoder and one HTTP listener.
- `IMPLEMENTED`: automatic and Skip crossfade continuity checks, received MP3 decode-back and audible PCM assertions.
- `IMPLEMENTED`: CI job checks FFmpeg/libmp3lame availability and invokes the isolated synthetic tests.
- `OPEN`: test execution evidence must be read from the matching GitHub Actions job.
- `OPEN`: Windows physical WASAPI/VB-CABLE, paid/free provider networking and installer acceptance remain separate.

## Evidence and open gates

- `OPEN`: focused Python tests added but not executed in this session.
- `OPEN`: Windows GUI and WASAPI acceptance.
- `OPEN`: physical local monitor device acceptance.
- `OPEN`: Windows portable and Inno Setup installer build.
- `OPEN`: live connection against a user-owned Shoutcast/Icecast endpoint.

No test, build, provider connection or Windows host acceptance is claimed without an execution receipt.
