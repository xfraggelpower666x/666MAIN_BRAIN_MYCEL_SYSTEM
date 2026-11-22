# System-only exclusion manifest

The archive is scanned and rejects:

- `*.pdf`, `*.docx`
- image formats: PNG, JPG, JPEG, WEBP, GIF
- audio formats: WAV, MP3, FLAC, AIFF, OGG
- `output/`, render and contact-sheet directories
- `archive/`, prior backup ZIPs and historical release snapshots
- `__pycache__`, `.pyc`, `.pyo`, temporary and log files
- chat/search/capture registers and generated result productions
