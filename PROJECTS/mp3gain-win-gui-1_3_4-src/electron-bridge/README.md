# MP3Gain JavaScript bridge for the VB6 GUI

This bridge keeps the existing VB6 interface and its command-line output handling. It accepts the legacy GUI's `mp3gain.exe` arguments, translates Windows-style switches, and runs the MP3Gain WebWorker from the `mp3gain.js` 1.1.0 package inside a hidden Electron renderer. Processed bytes are written back to the original files; the native `mp3gain.exe` is not used.

## Build on Windows

Install Node.js, then run these commands from this directory:

```powershell
npm ci
npm test
npm run build:win
```

Copy the contents of `release\win-unpacked` beside `MP3GainGUI.exe`. The packaged bridge executable is named `mp3gain.exe`; keep the other unpacked Electron runtime files and the `resources` directory beside it. The VB6 GUI detects this executable at startup.

The worker and Emscripten binary are distributed by the pinned `mp3gain.js` npm package. The upstream `mp3gain.js-master` sources remain in the sibling project folder for reference; rebuilding those sources separately requires the Emscripten Docker toolchain described in that project's README. The Windows package includes the GUI's LGPL notice and the `mp3gain.js` package metadata (ISC license) under `resources\licenses`.

## Compatibility notes

- Input files are loaded into memory for each command, so very large selections can require substantial memory.
- The engine's worker interface returns processed copies; this bridge writes those copies back to their original paths.
- `-p` preserves each file's original modification time. The native GUI option for temporary-file handling is accepted, but processing occurs in the worker's in-memory filesystem.
- Keep both projects' license notices when redistributing the GUI and bridge.
