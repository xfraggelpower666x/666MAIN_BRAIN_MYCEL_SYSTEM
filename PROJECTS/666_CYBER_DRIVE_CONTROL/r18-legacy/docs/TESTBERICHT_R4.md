# Testbericht R4 · Windows Edition v1.3.0

- Tests: `PYTHONPATH=src python -m pytest -q` → **44 passed**.
- Syntax: `python -m compileall -q src tests` → PASS.
- Paketbau: Wheel ohne Netzwerk installiert gebaut → PASS.
- CLI: `--preview --order CNS` → `C ○   N ○   S ○`.
- CLI JSON: `--preview --order NC --json` → `{"num": false, "caps": false}`.
- Native Windows-Lock-Lesung: READBACK_PENDING (Linux-Testumgebung).
- Tkinter-GUI unter Windows: READBACK_PENDING.
- Windows-System-Tray und physische LED: OFFEN / nicht implementiert.
- Fremdrepositories und Live-Systeme: unverändert.
