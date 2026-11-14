# L.Y.V.R.A. - MP3 MANAGER v2.36 — Prüfbericht

## Basis und Geltungsbereich
- Unverändertes v2.35-Quellarchiv ausgepackt und minimalinvasiv erweitert.
- Keine PFS- oder GitHub-Schreibvorgänge.
- Tests laufen unter Linux mit lokalem FFmpeg und virtualisiertem Tk/Xvfb; nicht auf Windows.

## Verifizierte Testgruppen
1. Vorhandene Tests `test_audio_qc.py`, `test_convert_integrated.py`, `test_real_wav_excerpt.py`, `test_repair_from_wav.py`, `test_v235_regressions.py`: **PASS**.
2. Virtueller GUI-Test `test_gui_repair_smoke.py`: **PASS** bei 1024×680, 1450×900 und 1920×1080.
3. `test_v236_gui_selection.py`: **PASS** — Neue Ordner sofort ausgewählt; explizit leere Auswahl bei Refresh erhalten.
4. `test_v236_drop_dispatch.py`: **PASS** — Tk-Event-Dispatch bei Ordnernamen mit Leerzeichen; **kein nativer Explorer-DnD-Test**.
5. `test_v236_portable_check.py`: **PASS** — Fehlende Bestandteile führen zu FAIL, vollständige statische Struktur zu STATIC_PASS_WINDOWS_PENDING.
6. `test_v236_real_wav_ab.py`: **PASS** — echter Suno-WAV-Ausschnitt von 100–112 Sekunden, 320 kb/s MP3, vollständige Dekodierung, numerischer Vergleich, Originalquelle bytegleich. Einzelheiten in JSON.
7. Python-Syntax und ZIP-CRC: **PASS**.

## Grenzen / offene Host-Gates
- Kein nativer Windows-PyInstaller-Build auf dem aktuellen Linux-Host möglich.
- Kein Nachweis für EXE-Start oder vollständige portable Ausführung auf fremdem Windows-PC.
- Keine echte Windows-DPI-/Mehrmonitor-/Explorer-DnD-Abnahme; nur virtuelle Tk-Prüfungen.
- Keine paarige beschädigte MP3 genau derselben WAV zur Untersuchung subjektiver Störgeräusche vorhanden. Andere MP3-Dateien wurden **nicht** als künstliches Paar verwendet.
- Bandenergie-Abweichungen sind **kein** Beweis für psychoakustische Artefaktfreiheit.

## Windows-Abnahme ohne erneuten Entwicklungs-Reset
1. `BUILD_PORTABLE_EXE.bat` ausführen, nur wenn v2.36 neu gebaut werden soll.
2. Danach `dist/L.Y.V.R.A._MP3_MANAGER/PORTABLE_VERIFY.bat` starten.
3. Gesamten Ordner kopieren; `PORTABLE_VERIFY.bat` auf zweitem Windows-PC erneut ausführen.
4. EXE-Start, Datei-Drop, alle drei Tabs und Monitore real prüfen. Diagnose und Screenshots zurückgeben.
5. Artefakt-Hörtest mit vollständiger WAV plus **zugehöriger** problematischer MP3.
