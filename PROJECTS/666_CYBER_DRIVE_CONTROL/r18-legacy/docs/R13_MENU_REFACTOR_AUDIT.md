# R13 MENU-1 Audit und Reparatur

Basis: KeyboardLEDRemapper-Windows-R13-WINDOWS-ABNAHME.zip (lokal entpackt).

## Befunde
- B-01: 7 Batch-Starter in Root und WINDOWS_ABNAHME -> zentral `START_WINDOWS_MENUE.bat`, zuvor bestehende BAT-Dateien nur in neuer Lieferkopie entfernt.
- B-02: heterogene Interpreterwahl -> bevorzugt lokale `.venv`, sonst `py` / `python`; Setup erzeugt eigene `.venv`.
- B-03: keine vollstaendige Werkzeugpruefung -> Diagnose fuer Python-Version, pip, Projektimport, psutil, pystray, Pillow, pytest, PowerShell, optional smartctl.
- B-04: Abnahmeskript verwendete immer `py` -> neuer Parameter `-PythonExe` und einheitlicher Aufruf aller Python-Pruefungen und des gestarteten Tray-Prozesses.
- B-05: Tray-Pakete fehlten unbemerkt -> Diagnose und nutzerinitiierter Setup-Menuepunkt.

## Safety
- Keine automatischen Downloads beim Programmstart; nur expliziter Setup-Eintrag installiert pip-Pakete.
- Read-only-Vorschau verfuegbar. Keine Admin-, Firmware- oder Kernel-Treiberbefehle.
- Originalarchiv und R13-Originalbasis bleiben unberuehrt.

## Verifikation
- Basisregression: `PYTHONPATH=src pytest -q` auf MENU-1.
- Batch-Menue nur statisch pruefbar (Linux-Host). Native Windows-Menue-/Tray-/Hardwaretests READBACK_PENDING.
