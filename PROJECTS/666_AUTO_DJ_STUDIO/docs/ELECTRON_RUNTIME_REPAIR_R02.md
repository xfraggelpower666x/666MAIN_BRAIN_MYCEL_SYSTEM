# Electron Runtime Repair R02 — 2026-11-23

## Windows symptom
`npm install` said `added 384 packages`, but the npm `allow-scripts` plugin blocked Electron's lifecycle step. Running `node_modules/electron/install.js` then returned without creating `node_modules/electron/dist/electron.exe` (as reported by user). The exact local reason for that second silent skip has not been observed.

## Minimal source repair
Only `build/BUILD.ps1` was changed. The official package's `node_modules/electron/install.js` is run after temporarily **unsetting** `ELECTRON_SKIP_BINARY_DOWNLOAD` (which would otherwise cause a successful exit without downloading). `npm_config_ignore_scripts` is set to `false` for that child invocation. Original environment values are restored using `finally`. We require both `path.txt` and the nonempty binary before starting Electron. If still missing, print concrete paths and environment evidence rather than presenting antivirus as a confirmed cause.

## Usage
From the unpacked project directory run `BUILD.bat`, choose `3`. The installer may need Internet access. To diagnose separately choose `2`. Existing `node_modules` and all original content are preserved. If option 3 still fails, provide the new diagnostic output plus any download error from `install.js`. There is **no verified Windows start or audio test** in this delivery.

## Continuity
No project identity, architecture, audio engine, Windows packager settings, legacy script, assets or GitHub pointer were changed. This is an additive local source repair on the prior Continuity ZIP, not a production release. GitHub R04 original byte parity remains open.
