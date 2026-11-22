# R15 — CYBER OVERLAY IMPLEMENTATION / HANDOFF

## Basis
R14 TRAY START REPAIR aus bestehender lokaler, unveraenderter Projektkopie.
Keine Veraenderung an originalen Windows-Installationen, keine Repo-Writes.
Keine Fremdcode-Uebernahme.

## Aenderungen
- src/klrw/bicolor_activity.py NEU: Zustand pro stabilem Volume-Key, getrennte Baselines, Impulszeit, Ruhesperre, Farbauswahl
- src/klrw/drive_workspace.py: additive persistente Layout/LED-Zeit-Konfiguration und Cyber-Farbdefaults
- src/klrw/drive_workspace_window.py: vertical/horizontal Umschaltung, eine Overlay-LED pro Volume, Cyber-Palette, Checkboxen/Status/Container, zeitbasierte LED-Ausgabe
- tests/test_r15_cyber_overlay.py NEU: 6 reproduzierbare Regressionen

## Vertragsgrenzen
- Keine physischen USB-HID-Kommandos.
- Windows-PDH-Volume-Zuordnung unveraendert, keine erfundenen Laufwerkswerte.
- Bisherige Tray-Symbole bleiben mit bestehender Doppelleuchtenanzeige; neue Bicolor-LED ist fuer Overlay.
- Bei gleichzeitiger Lese-/Schreibaktivitaet priorisiert die einzige LED Pink (Schreiben).
- Adaptive Grundlast lernt einen konstanten I/O-Pegel; dauerhafte moderate Last soll nicht dauernd leuchten.
- Meldungen fuer nicht verfuegbare I/O-Quellen bleiben erhalten.
- `interval_ms` default 500ms: Anzeigeimpulse koennen in der realen GUI grober erscheinen als gewaehlter Millisekundenwert.
- UI ohne Windows-Host in dieser Ausfuehrung nicht visuell abgenommen; Python-Tests sind statisch/mit Testdoubles.

## Abnahme
- Vollstaendige lokale pytest-Suite: 277/277 PASS.
- 6 neue R15-Tests: PASS.
- Windows GUI/Layout, USB-Bursts und echte LED-Farbwirkung: READBACK_PENDING.
- Bestehende R14-Source unveraendert ausser benannten Dateien; keine Installation.
