# L.Y.V.R.A. - MP3 MANAGER v2.35 — geprüfter Zustand

**Quelle:** Original v2.34 ZIP, vollständig übernommen.

## Verifiziert
- Python-Syntax der Hauptdatei und des neuen Regressionstests PASS.
- `test_audio_qc.py`: 48 kHz / 320 kbps technische MP3-Abnahme PASS; defekte Dateien erkannt.
- `test_convert_integrated.py`: Datei-Reihenfolge → Titelmetadaten → vollständige Dekodierung PASS.
- `test_repair_from_wav.py`: Original-WAV und problematische Referenz-MP3 bleiben bytegleich; Reparatur-Export + Hashbericht PASS.
- `test_real_wav_excerpt.py`: Ausschnitt einer echten Suno-WAV ohne Normalisierung konvertiert; nicht ganze WAV abgehört.
- `test_gui_repair_smoke.py`: virtuelle GUI-Smoke-Tests 1024x680, 1450x900, 1920x1080 PASS, kein echter Windows-DPI-Test.
- `test_v235_regressions.py`: gültige/ungültige Loudnorm-Messwerte, True-Peak-Sperre und Fehlerstatus PASS.
- SHA-256/ZIP-CRC: siehe neues Manifest.

## Noch offen
- Windows-native Portable-EXE mit FFmpeg-Bundle, Start auf anderem Windows-PC.
- Reale Windows-DPI, zwei Monitore, Drag-and-Drop mit großer Dateiliste.
- Vollständiger A/B-Hörvergleich eines konkreten WAV+fehlerhaft klingende MP3-Tracks.
- Vollständiger Batch-Lasttest und Nutzerbedienung der drei Qualitätsprofile.

**Keine PFS-Writes.** Ältere Originaldateien und Quellhistorie bleiben erhalten.
