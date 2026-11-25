# R01.10.5 — Neon Control Center recovery

The user reported that after the hidden-console change the boot intro completed but the menu did not appear.

- Reworked only the GUI branch in `STARTEN.ps1`.
- Boot remains best-effort; boot failure is logged and cannot prevent the menu attempt.
- The existing menu script is checked and explicitly invoked after boot returns.
- Menu startup failures are written to `%LOCALAPPDATA%\\666SOUNDsDESIGn\\UniversalBuildkit\\logs\\launcher.log`.
- A visible diagnostic dialog is shown for menu startup failures.
- Existing hidden BAT/VBS startup, menu UI and build actions remain preserved.

Windows Forms runtime acceptance remains pending.
