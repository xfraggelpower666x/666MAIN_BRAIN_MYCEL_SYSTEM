# R14 – Tray-Start-Reparatur

## Ausgangsbasis
`KeyboardLEDRemapper-Windows-R13-ARCHIVE-INTEGRATION-R14.zip` (unveränderte Ursprungsbasis).

## Fehlernachweis
Windows-Host: Menüpunkte 1–3 funktionieren. Menüpunkt 4 schließt das Batch-Fenster ohne sichtbare Wirkung. **Ursache nicht abschließend nachgewiesen**: alter Start schreibt keinen dauerhaften Tray-Fehlerbericht. Der Tray-Backend-Start kann beim Erstellen des Fensters abbrechen.

## Geänderte Dateien
- `START_WINDOWS_MENUE.bat`: nur Menüpunkt 4: `TOOLS/REPORTS/TRAY_LAUNCH_LAST.log`, Exitcode, Fehlertext und sichtbarer Hinweis für Menüpunkt 5.
- `src/klrw/unified_tray.py`: initialisiert Tray mit einem nicht-destruktiven Fallback auf sichtbares Tk-Fenster; protokolliert Exception und Sensorfehler. Kein Zugriff auf Tastatur-LED-Hardware.
- `tests/test_r14_tray_launch_repair.py`: vier gezielte Gegenproben.

## Nicht geändert
Keine Änderungen an Laufwerkszählung, PDH, Drive-Overlay, Hotplug, HID, LED-Mapping oder vorhandenen R13-Anwendungsmodulen außerhalb `unified_tray.py`.

## Windows-Readback
Menüpunkt 4 starten; wenn das Fenster unsichtbar bleibt, `TOOLS/REPORTS/TRAY_LAUNCH_LAST.log` prüfen. Menüpunkt 5 als GUI-Gegenprobe. Windows-Host-/Tray-Abnahme bleibt `READBACK_PENDING`.
