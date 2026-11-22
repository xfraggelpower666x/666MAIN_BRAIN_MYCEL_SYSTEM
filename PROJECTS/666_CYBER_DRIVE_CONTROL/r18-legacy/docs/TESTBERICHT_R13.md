# R13 Testbericht

Stand: 21.11.2026. Plattform: Linux-Python-Container, **kein natives Windows**.

- R1–R12 Regression: 170/170 PASS.
- Neue R13-Modell-/Adapter-/Renderingtests: 17/17 PASS.
- **Gesamt: 187/187 PASS**.
- Python-Compileall PASS; simulierte CLI-nahe Status-Snapshot-Probe PASS.
- R13-RGB-Caps-Priorität, Frame-Änderungskennung, Eingabevalidierung, Negative-Rates,
  Lock-Reihenfolge, simulierte Sensoren und Icon-Rendering überprüft.
- Native Tray/Windows-Laufwerks-/Tastatur-Hardwaretests: `READBACK_PENDING`.

Alle Hardware-Funktionen standardmäßig read-only. Keine Remote-Repository-Mutation.
