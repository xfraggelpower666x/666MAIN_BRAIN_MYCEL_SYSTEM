# AUDIO REPAIR — v2.34

## Reparatur eines problematischen MP3-Exports

1. `STARTEN.bat` starten und `03 AUDIO CONVERT` öffnen.
2. `WAV → MP3 REPAIR (A/B)` klicken.
3. **Original-Suno-WAV** auswählen.
4. Die betroffene **alte MP3** als Referenz auswählen.
5. Bei voneinander abweichenden Dateinamen prüfen, ob es wirklich derselbe Track ist.
6. Den Vorgang bestätigen. Nur die WAV wird neu kodiert.
7. Die neue Datei liegt im Unterordner `_666MP3_REPAIR` neben der Referenz-MP3.
8. Original-WAV, alte MP3 und neue MP3 bewusst vergleichen; mit identischer
   Abhörlautstärke, insbesondere Höhen, Hi-Hats, Bass- und Acid-Transienten prüfen.

Das Repair-Preset ist fest: **Maximum Quality, 48.000 Hz, 320 kbit/s,
Stereo, 32-Bit-Float-Zwischenformat, OHNE Normalisierung**.

## Beweisdatei

Jede erfolgreich erzeugte MP3 erhält eine zusätzliche
`<ausgabe>.mp3.quality.json` mit Hashwerten, Normalisierung,
technischem Decode-Test und ggf. der alten MP3 als Referenz.

Ein technisch fehlerfreier MP3-Stream ist nicht notwendigerweise
psychoakustisch artefaktfrei. Verlorene Informationen lassen sich aus
MP3 allein nicht exakt rekonstruieren. Kein automatischer Hochtonfilter.

## Datensicherheit

- Neue Dateien ausschließlich in getrennten Ausgabeordnern.
- Dateikollisionen werden mit fortlaufenden Nummern vermieden.
- Kein Überschreiben von Original-WAV oder Referenz-MP3.
- Bei Abbruch oder fehlgeschlagenem Audio-QC wird nur der neue Export verworfen.
- Kein automatischer Netzwerk-Download und keine PFS-Writes.

## Aktuelle Testgrenzen

Nativer Windows-PyInstaller-Build und Hörabnahme eines zusammengehörigen
WAV/MP3-Paares stehen aus. Linux/Xvfb GUI-Test ersetzt keinen Windows-DPI-Test.
