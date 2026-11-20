# L.Y.V.R.A. - MP3 MANAGER · User Manual v2.20

## 1. Launch and dependencies
Run `L.Y.V.R.A._MP3_MANAGER.bat` and select an action. The source project supports launch, system check and portable build; the same menu launches and verifies the executable from the portable folder. Audio tools can be checked and installed with explicit confirmation. Python dependencies are installed into `.venv_stable` only after confirmation. Building requires the full source project: **no EXE build feature is shipped inside the app**. Direct commands: `L.Y.V.R.A._MP3_MANAGER.bat start`, `check`, `build`, `audio` or `verify`, optionally followed by `/nopause`.

## 2. Files and renaming
Choose a music directory and scan it. MP3 and WAV files are shown together. The fixed counter displays total, MP3, WAV and selected entries. “Rename files only” never edits tags. “Clean filenames + ID3 titles” can also process MP3 title tags. `[0m00s-4m56s]` time ranges can be removed; numbered suffix `(1)` becomes `1` when enabled. Always preview first. Existing destination files are never overwritten. STOP takes effect between files.

## 3. Metadata and artwork
Choose selected files or all files. Only checked ID3 fields are written. Per-track title transfer: filename → ID3 title or ID3 title → filename. “START / SAVE METADATA” edits MP3 tags and covers **without renaming any files**. Originals are backed up first. WAV is not treated as ID3.

For cover art, choose one image for all selected MP3 tracks or assign individually. Enable cover embedding. All supported readable inputs become 512 × 512 JPEG; JPEG quality is adjustable 1–100 (default 95). Modes: **Fit** (letterbox), **Crop** (center), and **Stretch** (like Windows desktop stretch, changes aspect ratio). A 16:9 image becomes a full 512 × 512 square in stretch mode. ID3 changes can invalidate C2PA provenance; protected files require explicit approval.

## 4. Audio conversion
Choose WAV, MP3 or MIXED input. Standard output: 48000 Hz, 320 kbit/s, Stereo, optionally −14 LUFS / −2 dBTP normalization. `s16p` is an intermediate PCM format, not MP3 sample depth. MP3 is lossy. Re-encoding an MP3 cannot restore lost information. Inspect decoded output and levels. STOP terminates the active FFmpeg process and removes only incomplete temporary output files.

**Preset behavior from v2.38.** Maximum Quality and Original Preserve export without loudness normalization. When Balanced Radio normalization is enabled, the measurement is followed by a fixed gain adjustment. If the projected level exceeds the true-peak limit or source LRA exceeds the target, the manager reports an error for that track. The MP3 appears in the output folder after ID3 validation and any enabled audio QC.

## 5. Audio Labs
The AUDIO LABS tab launches Suno Song Remaster, Restoration Lab, SunoCleanser, and the MP3Gain VB6 GUI; Sunscreen and wav2mp3 run as command-line tools. In a source checkout, keep the project folders beside the MP3 manager under `PROJECTS`. Suno requires local Electron dependencies and a built renderer (`npm run build` in its project folder); the manager does not start a development server. Restoration Lab uses its own `STARTEN.bat`, and SunoCleanser requires the Conda environment `sunocleanser`. MP3Gain is Windows-only and requires `MP3GainGUI.exe` plus the complete `electron-bridge/release/win-unpacked` build beside the GUI. Sunscreen accepts MP3, WAV, FLAC, and M4A; one selected file is processed with `--smooth --widen --excite --match --master`. Outputs are 24-bit WAVs in a `sunscreen` folder beside the source. wav2mp3 processes every WAV file directly in the chosen folder and writes MP3 outputs there; the manager will not launch it if same-name MP3 outputs already exist. Building wav2mp3 requires the C++ and LAME development files in its Makefile. Portable builds optionally include existing apps, the MP3Gain GUI and bridge, and available Sunscreen and wav2mp3 Windows binaries. Missing packages are never installed silently. The manager and VB6 interfaces use the L.Y.V.R.A. dark-blue, cyan, pink, and violet palette.

Select exactly one WAV or MP3 in the audio browser and choose **OPEN RESTORATION LAB** to open its full interface above the manager with that file loaded. Restoration Lab supports mono or stereo audio at 44.1 or 48 kHz. Export a separate WAV in Restoration Lab; after export, you can select the result in the manager's audio browser. The source checkout needs the sibling `Restoration-Lab-main` project and the dependencies in `requirements.txt`; the portable build bundles the integration.

## 6. Second-screen windows and drag & drop
Open the detachable file manager from any tab, then move it to the second display. Explorer file/folder drag & drop is supported when tkinterdnd2 is available. The detachable live monitor shows current track and individual/overall job progress.

## 7. System and language
The SYSTEM tab checks dependencies, but EXE packaging is only available through `L.Y.V.R.A._MP3_MANAGER.bat build` from the source directory. Select DE or EN at the top. Use “? HILFE / HELP” for this manual. Language selection never translates user filenames, song titles or metadata.

## Safety and testing
Use backups and try 2–3 files first; native Windows GUI/HiDPI/drag-drop/FFmpeg and portable EXE behavior still require real-world testing.


### v2.24 – Metadaten / Metadata
The metadata start button is above the target list. Per-file title transfer disables manual song-title entry. EXE building takes place outside the app using `L.Y.V.R.A._MP3_MANAGER.bat build`.


### v2.24 – Metadaten / Metadata
The metadata start button is above the target list. Per-file title transfer disables manual song-title entry. EXE building takes place outside the app using `L.Y.V.R.A._MP3_MANAGER.bat build`.
