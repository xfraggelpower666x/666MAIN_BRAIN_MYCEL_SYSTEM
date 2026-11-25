# C02 · ID3 copy-edit parity slice

- Add `metadata_copy` action to Python worker reusing `mutagen` with ID3v2.3 readback; source stays untouched.
- Apply existing exclusive output filename allocation and callback status to Electron IPC.
- Add title, artist and album fields to Electron renderer, with filename fallback for blank title.
- Include real WAV/MP3 and metadata/collision/negative tests (7/7 PASS on Linux).
- Preserve all original Tkinter, Media Tools, Restoration Lab and export paths.
- Full functional parity and Windows host acceptance remain OPEN.
