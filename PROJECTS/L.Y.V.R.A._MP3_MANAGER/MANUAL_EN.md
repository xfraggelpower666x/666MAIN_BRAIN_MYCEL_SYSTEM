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

Select exactly one WAV or MP3 in the audio browser and choose **OPEN RESTORATION LAB** to open its full interface above the manager with that file loaded. Restoration Lab supports mono or stereo audio at 44.1 or 48 kHz. Export a separate WAV in Restoration Lab; after export, you can select the result in the manager's audio browser. The source checkout needs the sibling `Restoration-Lab-main` project and the dependencies in `requirements.txt`; the portable build bundles the integration.

## 5. Second-screen windows and drag & drop
Open the detachable file manager from any tab, then move it to the second display. Explorer file/folder drag & drop is supported when tkinterdnd2 is available. The detachable live monitor shows current track and individual/overall job progress.

## 6. System and language
The SYSTEM tab checks dependencies, but EXE packaging is only available through `L.Y.V.R.A._MP3_MANAGER.bat build` from the source directory. Select DE or EN at the top. Use “? HILFE / HELP” for this manual. Language selection never translates user filenames, song titles or metadata.

## Safety and testing
Use backups and try 2–3 files first; native Windows GUI/HiDPI/drag-drop/FFmpeg and portable EXE behavior still require real-world testing.


### v2.24 – Metadaten / Metadata
The metadata start button is above the target list. Per-file title transfer disables manual song-title entry. EXE building takes place outside the app using `L.Y.V.R.A._MP3_MANAGER.bat build`.


### v2.24 – Metadaten / Metadata
The metadata start button is above the target list. Per-file title transfer disables manual song-title entry. EXE building takes place outside the app using `L.Y.V.R.A._MP3_MANAGER.bat build`.
