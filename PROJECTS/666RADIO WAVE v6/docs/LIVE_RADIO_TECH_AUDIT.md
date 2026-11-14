# Live Radio Technology Audit — RADIO WAVE v6.66

## Scope and comparison

This audit compares the live-radio transport and settings in the WebRadio source
(`public/js/player-core.js`, `public/js/audio-start-core.js`,
`public/js/all-player-audio-recovery.js` and `config/stream.config.js`) with the
Electron integration (`main.js`, `preload.js`, `src/integration/666-integration.js`,
`src/app.js` and `src/shared/radio-config.cjs`). It covers behavior and data flow,
not visual styling.

Both projects use the same radio service and routes: `/stream`,
`/fallback-stream` and `/api/nowplaying`. This audit also follows the three
operator features through their renderer, Electron IPC and WebRadio endpoints:
Auto-DJ Skip, Player/Broadcast Messenger and Discord Messenger.

## Findings and repairs

| Area | Finding | Change |
|---|---|---|
| Stream recovery | Radio Wave only reacted to media `error`. A live stream that emitted `waiting` or `stalled` without an `error` could remain stuck. | Added a bounded 16-second waiting/stalled check which enters the existing fallback and recovery flow. Successful playback cancels the timer; source changes invalidate stale checks. |
| Playback intent | A transport error while radio was merely selected could start the fallback without a user Play action. Main recovery could also restart playback after a pause. | Added explicit play/pause intent handoff from the existing transport control. Failover and recovery now preserve pause intent and do not start playback until requested. |
| Volume preference | The volume slider was initialized from the HTML default on every launch; only mute state was persisted. | Save the volume in local storage and restore it with a 0–1 bound. |
| Player/Broadcast Messenger receive | WebRadio's `/api/player-alert/current` returns the alert fields at the top level, including `message` as a string. Radio Wave selected that string as the candidate alert, then discarded it because it was not an object. Broadcasts could be sent but not displayed by Radio Wave's receive poller. | Normalize both the direct WebRadio payload and wrapped `alert`/`current`/`data` payloads. Ignore expired messages, show receive errors instead of swallowing them, and test the actual response shapes. |
| Sound settings | The visualizer analyzed the media element, but no equalizer or output gain stage existed. | Added low/mid/high biquad controls and a bounded +0–12 dB booster in the shared Web Audio path, before both device output and recording capture. Values use the existing UI-settings persistence. |
| Admin/password worker | Skip and Discord used the existing login gate, but Worker runtime-config current/backups/update/rollback endpoints were not exposed in Radio Wave. | Added main-process-only adapters and a Radio Admin window. Config writes are field/size bounded and require explicit confirmation; rollback is also confirmed. Password tokens remain in Electron Main. |
| Histories | Player Alert history and track history existed in WebRadio data, but Radio Wave did not render them; Discord had no history endpoint. | Added Messenger history refresh/periodic polling, renders track history returned with `/api/nowplaying`, and keeps a bounded local history of successful Discord sends. Player/stream history availability still depends on the remote endpoint payload. |
| System LEDs and panels | Audio LED levels were already measured from the real analyser, but hover text exposed no live percentage. Repeated dock actions only focused an open panel. | Added live, accessible LED percentages and made attached/detached panel actions toggle the existing window. Detached window visibility is persisted, and Electron windows remain movable across displays. |
| Offline media | The picker and local queue accepted only audio extensions; there was no folder/playlist workflow or video stage rendering. | Extended the bounded local queue to common audio/video containers, added file drag/drop, native folder import and JSON playlist save/load, and renders local video frames into the visualizer/export canvas. Codec decoding is delegated to the installed Electron/Windows media stack; unsupported codecs show a playback error rather than being transcoded. |
| Video exporter | Recorder preferred MP4 even when the runtime fell back to WebM, so the file extension could disagree with the actual container. Chunk writes were not serialized and could race file close; there was no pause control. | Selects a supported recorder MIME before opening the native save dialog, keeps the extension aligned, serializes and checks chunk writes, and adds pause/resume plus play-media-file access through the local player. |

## Remote operator feature audit

- **Auto-DJ Skip:** the renderer calls `radio:skip`; Main requires a confirmed
  admin gate then posts to `/api/admin/skip`, matching the current WebRadio
  protected route. The feature requires a successful Player Admin login and a
  configured server-side AutoDJ bridge; the WebRadio keeps the dedicated worker
  secret server-side.
- **Player/Broadcast Messenger:** sending uses `/api/player-alert/send`, the
  public same-origin WebRadio route, with the expected message/sender fields.
  The receive-payload mismatch above was repaired.
- **Discord Messenger:** manual messages use `/api/discord/message`; manual
  Now Playing and automatic track-change updates use `/api/discord/nowplaying`.
  The payload includes the artist/title fields expected by the WebRadio worker.
  Requests are authenticated through the existing Admin gate in Radio Wave;
  actual delivery still depends on the WebRadio's Discord configuration and
  worker availability.
- **Password Worker Admin Config:** reads `/api/admin/config/current` and
  `/api/admin/config/backups`; updates use `/api/admin/config/update` and
  rollback uses `/api/admin/config/rollback`. Worker-side validation, Admin/PW
  verification, write-origin checks and GitHub secrets remain authoritative.
  The Radio Wave adapter only accepts the stream URL/list fields supported by
  the Worker; it does not expose Worker secrets or issue remote changes without
  an explicit confirmation.

## Existing behavior retained

- Main is the initial route; fallback is used only after a playback failure.
- A recovered Main route is probed before leaving a stable fallback stream.
- Now-playing polling remains visibility-aware, and route/metadata continue to
  synchronize to secondary visual outputs.
- Admin credentials remain owned by the Electron main process. Remote Admin
  Config writes are now available only through the protected and confirmed
  Main-process adapters.

## Deliberate scope limits

The WebRadio browser player has separate Main, Backup and reconnect controls and
a page-wide recovery owner. Those controls/modules are not copied as-is: Radio
Wave has one shared Soundwave audio element, a different playback owner, and no
corresponding route-control surface. This repair adapts stall recovery to that
existing owner and does not change the visual interface. Manual route selection
remains a separate product decision.

## RADIO WAVE v6.66 follow-up

- **Windows and overlays:** New detached control windows estimate their first
  bounds from actual panel content, constrained to the current monitor work
  area. Saved geometry is kept, and native windows remain draggable/resizable.
  The visualizer can be toggled and auto-fitted from the main HUD after being
  moved to another display.
- **Single playback owner:** The application continues to use its single
  Electron-instance lock and one main-renderer audio owner. Secondary display
  outputs are visual-only and capped at two; video output is muted and follows
  the main playback clock.
- **Monitor controls:** Display 1/2 selection, visual output start/stop,
  visualizer window toggle, and auto-fit are available in the main HUD. These
  select display outputs; they do not choose a physical GPU adapter per monitor.
- **Live diagnostics:** Worker `/health`, runtime-config status, Shoutcast
  listener statistics, Player Messenger/Skip status, local output-watchdog
  state, Electron GPU features, display metrics, output heartbeats and memory
  are surfaced as diagnostic data. Listener/peak/limit/unique counts come from
  `/api/shoutcast/stats`; DJ, bitrate, track history and metadata timestamps
  come from `/api/nowplaying` when the service supplies them. Missing values
  remain unavailable rather than being fabricated.
- **Manual stream routes:** Primary/fallback URLs can be saved locally in the
  Windows user-data directory. The currently integrated WebRadio routes remain
  the defaults and can be restored. Values accept HTTP(S) URLs without embedded
  user information.
- **SoundCloud setup:** Client ID/secret can be stored in Electron `safeStorage`
  encryption in the user's local app data; they are not saved to renderer
  settings. The optional browser is an isolated, single-instance SoundCloud
  window without Node integration and is restricted to HTTPS SoundCloud hosts.
- **Language, information and artwork:** English is the default, with a
  persisted German option. German translations also apply to mapped static UI
  and dynamically updated text; preset names and arbitrary server/error text
  may remain in their original language. The About panel contains the requested
  copyright, email and project/social links. Supplied brand images are
  downscaled while preserving aspect ratio and displayed with `object-fit:
  contain`.
- **Build setup:** Source build/check/start batches use winget to attempt a
  silent Node.js LTS install/update and use `npm ci` for locked project tools.
  The Python-host build similarly installs/updates Python 3.12 and PyInstaller.
  These actions require winget/network access and do not request automatic
  elevation. The NSIS installer is the primary `dist` target, while
  `dist:all:unsigned` builds both NSIS and Portable targets without resource
  editing/signing. On this host, resource editing with electron-builder's
  legacy signing-tool archive is blocked by Windows symbolic-link privileges;
  resulting executables are therefore unsigned. The portable ZIP is built from
  the unpacked runtime with bundled 7-Zip, checks Electron locales and
  Chromium's license notice, validates archive integrity, and writes SHA-256
  hashes for all generated installers/packages.
- **Live endpoint check (2026-11-07):** `/health`,
  `/api/runtime-config/status`, `/api/shoutcast/stats` and `/api/nowplaying`
  returned HTTP 200. Shoutcast reported 4 current listeners, 106 peak, limit
  500, 3 unique listeners and stream status 1; Now Playing reported 320 kbps
  and `LYVRA DJ`. Shoutcast timestamps changed between probes; the latest
  observed timestamp was more than five minutes ahead of the session clock, so
  the data's exact age could not be established reliably. The UI labels
  timestamps older than five minutes as stale and timestamps more than five
  minutes ahead as clock skew. Live endpoint reachability does not verify audio
  playback, Discord delivery, or authenticated Admin actions.
- **Codec packaging:** No FFmpeg binary or additional codec package is bundled.
  Playback/export support is still limited to codecs available in the installed
  Electron/Windows runtime. Adding FFmpeg requires a separate build/runtime
  integration and review of its exact binary configuration, license notices,
  and codec redistribution rights; the installer must not claim universal
  codec compatibility in the meantime.

## Validation

Static integration checks cover the radio recovery path, audio processing,
bounded media queue and playlists, supported-recorder selection, IPC guards,
history surfaces, panel toggling, stale telemetry and portable archive
integrity. This source audit made read-only GET requests to the public health,
runtime-config, Shoutcast-stats and Now-Playing endpoints; it did not modify any
live service. It does not establish that the stream audio, authenticated
Admin/Password Worker actions, Discord delivery, Messenger delivery or codecs
on another Windows machine work end to end.
