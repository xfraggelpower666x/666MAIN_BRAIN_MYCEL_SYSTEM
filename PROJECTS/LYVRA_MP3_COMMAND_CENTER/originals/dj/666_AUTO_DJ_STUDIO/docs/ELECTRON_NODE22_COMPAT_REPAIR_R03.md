# Electron Node 22 compatibility repair R03 (non-destructive)

Observed Windows log: Node v26.13.1, Electron 35.7.5 npm package exists, but `node_modules/electron/path.txt` and `dist/electron.exe` are absent, even after direct `node install.js` exits successfully. Skip-download variable is unset.

An upstream Electron issue #51619 reports a similar silent binary extraction failure on Node 24/26, although under Electron 42 on Linux: https://github.com/electron/electron/issues/51619 . Treat as a supported hypothesis, not proven cause on the user's Windows setup.

Changed **only** `build/BUILD.ps1`. If host Node version is 24 or above, run the original Electron postinstall using an official scoped Node 22 Windows x64 executable. Download the latest-v22.x Windows x64 ZIP and SHA-256 manifest from `https://nodejs.org/dist/latest-v22.x/`, verify archive checksum, extract only the expected `node.exe` into `build/toolchains/node22/`, then run Electron's existing `install.js`. This avoids changing user's global Node and avoids npm package reinstall. Retains failed partial downloads for inspection rather than silently deleting unrelated files. Once Electron exe and path.txt are both present, ordinary launch/build actions proceed.

No Electron version change, no npm dependency versions changed, no node_modules deleted, original tool.ps1 and packaged FFmpeg preserved. Local installer download and Windows runtime remain **unverified** until executed by user.

Diagnostic if still failing: record the Node 22 runtime banner, errors above the final exception, and whether `node_modules/electron/path.txt` and `dist/electron.exe` exist. **Do not** simply reinstall the package with Node 26.
