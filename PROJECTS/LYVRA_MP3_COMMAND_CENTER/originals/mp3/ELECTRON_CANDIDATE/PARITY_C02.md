# L.Y.V.R.A. MP3 MANAGER — Electron C02 · Parity Report

Basis: Original v2.40.1 Electron C01 + unveränderte Tkinter/Python-Engine. C02 is an additive source candidate, **not** the default application.

## Implementiert und lokal getestet
- File selection, folder scan, source metadata inspection and audio stream selection (existing C01).
- MP3/WAV export from original `media_tools.export_media`, progress and STOP signaling (existing C01).
- Second status-monitor Electron window (source exists; native Windows display test OPEN).
- **New C02:** ID3 editor for title, artist and album. Creates new MP3 in selected output directory, ID3v2.3 tag readback, source SHA unchanged, collision guard, invalid-field rejection.
- Syntax: `node --check` on Electron main and renderer; `python -m py_compile` worker.
- `python -m unittest discover -s ELECTRON_CANDIDATE/tests -p 'test_*.py'` -> 7 PASS in Linux host.

## Offen / ausdrücklich nicht paritätisch
- Full Tkinter ID3 editor (other fields, cover art, per-file/batch controls).
- Cover-video composer and image import in Electron GUI.
- Full rename workflow, batch queue, file selection persistence and cancellation across tabs.
- Restoration Lab overlay / repair workflow UI.
- Live Explorer drag-and-drop in Electron (not offered as implemented).
- Windows-native Electron launch, packaged EXE, FFmpeg tools bundle, DPI/second monitor, accessibility and GUI host tests.
- Perceptual WAV/MP3 artifact A/B verification with real matching tracks.

## Windows test procedure
1. Unpack complete ZIP into a new folder.
2. Confirm old `MP3_MANAGER_START.bat` still starts Tkinter source project.
3. In `ELECTRON_CANDIDATE`, install Electron devDependencies only after consent (`npm install`), then `START_ELECTRON_WINDOWS.bat`.
4. Select MP3, select destination folder, INSPECT. Fill title/artist/album, use ID3-KOPIE ERSTELLEN.
5. Confirm new `.id3-edited.mp3` exists and original is unchanged; repeat to verify collision denial.
6. Test existing Export + Stop, second-monitor behavior, then collect host error logs. Do not promote Electron to default starter.

## Preservation
No existing Tkinter files, original assets, PFS, GitHub or LYVRA native authority were changed. All changes remain under `ELECTRON_CANDIDATE/`.
