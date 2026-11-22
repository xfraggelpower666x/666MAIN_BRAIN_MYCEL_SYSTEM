# Testbericht — R1 · 2026-11-21

**Status:** VERIFIZIERT (lokale Entwicklungsumgebung); Windows-Hardware READBACK_PENDING.

## Ausgeführte Prüfungen

- `PYTHONPATH=src pytest -q`: **12 passed** (1.00 s)
- `python -m compileall -q src`: bestanden
- `python -m pip wheel --no-deps --no-build-isolation . -w ...`: Wheel erstellt
- `PYTHONPATH=src python -m klrw.cli --count 1`: Smoke-Test erfolgreich (Simulation)
- `PYTHONPATH=src python -m klrw.cli --config /tmp/klrw-demo-r1.json --init-config`: Konfiguration erzeugt

## Testumfang

Konfigurations-Roundtrip, Unknown-Field-/Schema-Rejection, Hardware-Freigabe-Sperre, kein Überschreiben existierender Konfiguration, Default-Simulation, OR-Regellogik, Threshold-Validierung, Cleanup, Zählerdifferenzen in B/s, Reset-Clamping, Monitor-Lauf mit Mock-Sampler, Thread-Start-/Stop.

## Grenzen

Diese Tests wurden **nicht auf einem physischen Windows-Rechner** ausgeführt. `WindowsLockBackend` wurde nur statisch geprüft, nicht mit echter Hardware getestet. Keine USB-/Bluetooth-/RGB-Kompatibilitätszusage. Keine Windows-EXE gebaut. Keine Repository-Mutation. Keine Treiber installiert. Runtime benötigt Python 3.10+ und psutil.

## Nächste sinnvolle Recherchepunkte

1. Windows Keyboard-HID / RawInput: hardwareabhängige Lock-LED-Fähigkeiten ermitteln.
2. Vendor-SDK-Adaption für RGB-Tastaturen mit individueller LED-Steuerung.
3. Sleep/Resume- und RDP-Robustheit einschließlich Start-/Stop-Recovery.
4. Signierter Windows-Installer und reproduzierbare Build-Pipeline.
