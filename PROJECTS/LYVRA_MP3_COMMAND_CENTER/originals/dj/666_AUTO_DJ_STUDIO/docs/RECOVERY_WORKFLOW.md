# 666 AUTO-DJ STUDIO — lossless continuity gate

## Sources
- Canonical *historical* project checkpoint: `666MAIN_BRAIN` commit `1bc7eb56b659ad345a7cba7adf808772163e9520` at `PROJECTS/666_AUTO_DJ_STUDIO`.
- Last owner-provided delivery candidate: `666_AUTO_DJ_STUDIO_CONTINUITY_CODEFORGE_PATCH.zip`.
- Original PowerShell source preserved as `legacy/tool.ps1`, covers under `legacy/covers` and FFmpeg EXEs under `tools/ffmpeg`.

## What is actually merged in this ZIP
The existing continuity delivery candidate is retained in place. R04 historical continuity documentation has been restored as contextual text; its exact blob IDs are recorded in `GITHUB_R04_SOURCE_RECOVERY_MANIFEST.json`. Two earlier public APIs (`worker.destination` and `playlist.safe_playlist_path`) were restored additively without deleting any renderer logic. The former GitHub Current is placed under `history/` and **not** asserted as the Current of the new local ZIP.

## Authority warning
The current shared `666MAIN_BRAIN` HEAD no longer lists `PROJECTS/666_AUTO_DJ_STUDIO`. This is a repository consistency conflict. No GitHub write, branch rewind, forced checkout, or Current pointer promotion was performed. The complete R04 source body has NOT been verified byte-for-byte inside this local ZIP. Resolve source-lineage ownership before remote publication.

## Run
Extract the archive and double-click `BUILD.bat` in `666_AUTO_DJ_STUDIO`. Option 7 starts the preserved original PowerShell GUI, option 3 starts the Electron development app, 4/5/6 create Windows packages when build prerequisites are present. Windows builds, audio output and installer validation require the actual target machine.
