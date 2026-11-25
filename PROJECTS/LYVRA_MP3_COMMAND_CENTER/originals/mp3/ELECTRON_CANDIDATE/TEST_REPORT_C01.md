# Electron Candidate C01 — technischer Readback / Tests

Basis: `LYVRA_MP3_MANAGER_v2_40_1_TEST_COLLECTION_REPAIR_SOURCE.zip` (vollständig unverändert mit aufgenommen).

Testumgebung: Linux, Python 3, Node 22.16.0, systemweit verfügbares FFmpeg/FFprobe.

## Ausgeführt
- `node --check electron/main.cjs`, `electron/preload.cjs`, `renderer/app.js` und `renderer/monitor.js`: PASS (statische Syntax)
- `python tests/test_bridge.py`: 5/5 PASS, darunter realer FFmpeg WAV→MP3-Export, FFprobe + MP3-Dekodierung, SHA-256-Originalvergleich, Dateikollision, Metadatenprüfung via FFprobe.
- `python -m pytest -q tests/test_v239_media.py tests/test_v238_export.py tests/test_audio_qc.py`: 10/10 PASS am unveränderten Originalprojekt.

## Offen
- Tatsächliche Electron-Desktop-UI unter Windows, Explorer-Drag-&-Drop, DPI und Monitorwechsel.
- Windows-Python-Einbettung/Portable EXE; der Kandidat benötigt momentan Host-Python.
- Feature-Parität zu Metadaten-Schreibdialog, Restoration Lab, Covervideo-Composer und Audio Repair.
- Vollständige Psychoakustik-Hörabnahme.
- Kooperative Abbruchabnahme mit echten Windows-FFmpeg-Prozessen.

Status: SOURCE_CANDIDATE_VERIFIED · HOST_WINDOWS_PENDING · NO_REPO_WRITES.
