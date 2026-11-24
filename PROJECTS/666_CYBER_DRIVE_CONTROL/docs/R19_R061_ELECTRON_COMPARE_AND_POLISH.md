# R19 / FULL LYRICS R06.1 — Electron convergence audit (2026-11-25)

Source: verified same-branch GitHub at commit 080d026fd3433b7fdaa7b15fd691bf3253e00130.
Peer: PROJECTS/666_FULL_LYRICS_INTELLIGENCE/DELIVERY_R06_1.json, README_START_HIER.md, tools/LAUNCH.ps1, tools/INSTALL_ELECTRON_RUNTIME.ps1, renderer/style.css and package.json.
Native target: PROJECTS/666_CYBER_DRIVE_CONTROL.

## What R06.1 actually fixed
PowerShell Set-Content appended CRLF to node_modules/electron/path.txt. Electron's Node loader used the literal marker as an executable path, producing spawn ENOENT. R06.1 uses .NET File.WriteAllText without a line ending and repairs the already-present runtime in place. It is a local developer-runtime fix, not a replacement for the packaged Windows build. Its delivery JSON itself records windows_host=NOT_RUN; the README separately mentions user-reported Windows functionality, so do not promote either to an independent Windows host receipt.

## R19 comparison
R19 is already Electron with isolated main/preload, HTML/CSS renderer, frozen Python metrics sidecar, native tray/overlay and a verified Windows CI Portable/NSIS packaging run. No Electron conversion is required.
R19's central Windows build controller now checks an existing Electron package marker only when dist/electron.exe and path.txt both exist. If the marker is exactly electron.exe with trailing whitespace, it repairs bytes in place using File.WriteAllText ASCII, and immediately reads back. It does not download, remove or upgrade an Electron runtime; it fails closed on unexpected marker contents.
A separate additive neon-cyber CSS polish uses original R19 IDs/selectors and respects transparent overlay. No JS event handlers, IPC, Python engine, R18 files, keyboard controls, build commands or other projects were changed.

## Evidence / acceptance
Static source readback and CSS inspection are source evidence, not a visual Windows acceptance. Existing Windows release receipts apply to an earlier R19 commit; new CSS and marker-guard source require subsequent Windows build and desktop GUI review before release promotion.
