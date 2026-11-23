# MENU-4 Diagnose und Reparatur

- B-06: Python-Version auf Host nicht gefunden, obwohl frühere Installationen belegt sind. **Hypothese:** PATH/winget-Discovery zu eng. Eine neue Python-Installation ist deshalb nicht legitimiert, bevor weitere Installationsorte geprüft wurden.
- `TOOLS/WINDOWS_TOOL_MANAGER.ps1`: Find-Python prüft jetzt vorhandene `.venv`, py Launcher, Registry und WinGet-Packages.
- Setup überspringt erneute Installation, wenn alle Pflichtelemente READY sind.
- pip-Reparatur versucht `ensurepip` innerhalb der lokalen `.venv`.
- Batch- und bestehende Fachmodule bleiben funktional unverändert; ein einziger Windows-Batch-Einstieg.
- Echter Windows-Host-Readback weiterhin READBACK_PENDING.
