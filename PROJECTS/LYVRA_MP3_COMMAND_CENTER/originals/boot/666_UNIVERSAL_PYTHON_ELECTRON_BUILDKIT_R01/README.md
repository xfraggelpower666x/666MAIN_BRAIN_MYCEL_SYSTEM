# 666 Universal Python / Electron Buildkit — R01

**Mode:** independent additive toolkit, no changes to existing application sources. This starter is generic and must be configured to match the real Python project.

## Integration

1. Copy the entire `666_UNIVERSAL_PYTHON_ELECTRON_BUILDKIT_R01` directory into your existing Python project root; keep it as a subdirectory.
2. Edit `project.config.json`: `project_directory: ".."` points to the parent Python project, `python_entry` is its existing entrypoint; set real `backend_ui_url` and `backend_health_url`.
3. The Python application **must expose a loopback HTTP frontend and /health route** in `python_backend` mode; this toolkit cannot convert an arbitrary Tkinter, Qt, CLI or desktop script into an Electron interface automatically.
4. The menu will offer to generate `electron/package-lock.json` from the npm registry on first use (requires approval); review and commit the resulting lockfile. This package does not ship a fabricated dependency lock because registry access was unavailable during preparation.
5. Double-click `STARTEN.bat`. Menu options 1–8 scan, prepare, run, test and package.
6. The supplied Development Tools graphic is integrated at `electron/renderer/assets/`. The original is preserved; optimized 1920×1080 and 1280×720 WebP variants are selected responsively. The boot image uses `object-fit: contain` to prevent text distortion or cropping.

## Menu

| # | Action | Behavior |
|---|---|---|
| 1 | Toolcheck | Read-only check of Python, py, Node/npm, winget, Git, GitHub CLI, CMake, MSVC cl, MSBuild, .NET |
| 2 | Tool install/update | Single selected winget package only after explicit confirmation |
| 3 | Prepare | venv and project Python requirements; prompts before package install |
| 4 | Run Python | Start configured Python entry |
| 5 | Test | Run configured Python test command |
| 6 | Electron | Starts Python backend and full-screen Electron; requires HTTP UI |
| 7 | Portable EXE | Tests, bundles backend via PyInstaller, electron-builder portable |
| 8 | NSIS Setup | Tests, bundles backend, electron-builder NSIS with directory selection |

## Critical notes

- No silent global tool upgrades: system upgrades can break unrelated projects. `update_existing_tools` is reserved, not automatically executed.
- `winget` package IDs require trust and may change; the toolkit does not guarantee any third-party installer is free of cost, subscription or licensing restrictions. No paid credits or deploys are requested.
- PyInstaller bundles the project entry script into `dist-backend/backend/backend.exe`; app-specific data files, hidden imports, native DLLs and child processes may require custom PyInstaller hooks or additional resources. Validate on a **real Windows host**, then run the installed app and portable app.
- Electron-builder obtains binaries from the network; native Windows setup is not verified in this Linux construction environment.
- The boot screen is separate from your Python UI. The Electron window enters full-screen, `F11` toggles it; escape from kiosk depends on config (defaults kiosk=false).
- Packaging output is created under `dist/`, ignored by Git. Build should be executed from trusted source because build scripts and Python packages can execute code.
- All logs are local. `tools/diagnose.py` performs toolchain discovery without installing anything. Avoid sending raw diagnostic paths publicly.
- Never copy this toolkit over an existing `electron/` directory; keep it self-contained.

## Status

Source package prepared. Python syntax checks can be performed on the authoring host. No real Windows Build Tools/Electron/NSIS build acceptance has been performed here.

## R01.1 Bootscreen integration (2026-11-22)

- The original supplied 1671×941 image is preserved unmodified in `electron/renderer/assets/bootscreen-original.png`.
- 1920×1080 and 1280×720 variants are generated with proportional scaling and dark letterbox padding. No crop.
- Electron fullscreen boot view uses 100% viewport image fit, with low-profile animated status at bottom. UI styling of the Python app itself is not overwritten.
- Real Windows Electron and build acceptance remains outstanding.

## R01.2 Windows execution-policy starter repair (2026-11-22)

- `STARTEN.bat` now launches the existing `STARTEN.ps1` with `powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File` to bypass a restrictive execution policy **for that one PowerShell process only**.
- No `Set-ExecutionPolicy` command, machine-wide security change, elevation, downloaded-code unblocking or modification to the toolkit engine.
- Run **`STARTEN.bat` by double-click**, not `STARTEN.ps1` directly, when policy blocks scripts.
- If policy is enforced by Group Policy (`MachinePolicy`/`UserPolicy`) or application control, the process option may be ignored or execution denied; contact the device administrator instead of trying to override a managed restriction.
- Windows runtime acceptance is still open; a static regression test checks the correct launcher invocation.

## R01.3 Neon Windows-GUI-Menü

Start über `STARTEN.bat` zeigt jetzt ein grafisches WinForms-Menü. `STARTEN.bat menu` behält das Konsolenmenü bei. Die ursprüngliche Engine und sämtliche Freigaben bleiben unverändert. Siehe `docs/R01_3_GUI.md`.

## R01.5: Bootscreen 8 Sekunden

Die sechs Phasen sind auf 0,95 / 2,15 / 3,35 / 4,55 / 5,85 / 7,20 Sekunden verteilt; nach 8,00 Sekunden wird das Menü geöffnet. Siehe `docs/R01_5_BOOT_TIMING.md`.


## R01.6 Windows Cyber-Boot Repair

WinForms `DoubleBuffered`-Zuweisung entfernt (Fallback-Crash); Boot-Timing bleibt bei 8 Sekunden. Siehe `docs/R01_6_BOOT_WINFORMS_REPAIR.md`.

## R01.7 Cyber-Boot HANG FIX

- Boot-Zeitfenster bleibt 8000 ms mit sechs Phasen.
- Timer-Callback durch begrenzte WinForms-Nachrichtenpumpe ersetzt.
- Schnell pruefende PATH-Suche statt PowerShell Get-Command.
- Auch nach fehlgeschlagener Phasenpruefung wird Bootfenster geschlossen und Control Center geoeffnet.
- ESC schliesst das Intro sofort.
- Windows-Laufzeitabnahme weiterhin ausstehend.

## R01.8 Smooth Boot
Cyber-Boot verwendet jetzt eine statische Bildflaeche mit getrenntem Overlay. Der Fortschritt aktualisiert sich ueber 8 Sekunden unabhaengig von den sechs Read-only-Pruefphasen. Details: `docs/R01_8_SMOOTH_BOOT_REPAIR.md`.

## R01.9 HUD/Encoding
Das Cyber-Intro verwendet ein statisch gerendertes Neon-HUD und ein transparentes Status-Overlay. Statuswerte sind in ASCII (OK/!/--) codiert, um Mojibake unter Windows PowerShell 5.1 zu verhindern. Siehe docs/R01_9_BOOT_VISUAL_REPAIR.md.


## R01.10 — Single-Surface Cyber HUD

Status und Fortschritt werden direkt auf die einmalig geladene HUD-Zeichenflaeche gezeichnet. Siehe `docs/R01_10_BOOT_SINGLE_SURFACE_REPAIR.md`.


## R01.10.1 — Boot timer hotfix

Removed stale references to deleted legacy overlay controls from the timer and Shown handlers. The timer now updates the single HUD drawing surface only.


## R01.10.2 — Clean artwork replacement

Replaced `tools/assets/cyber-boot-artwork.png` with the cleaned user-supplied image. Existing path and boot behavior are preserved.


## R01.10.3 — Regression and UI synchronization

Updated the automated tests to match the current single-PictureBox cyber boot, removed obsolete assertions for retired controls, and synchronized the visible menu release label. See `docs/R01_10_3_REGRESSION_AND_UI_SYNC.md`.


## R01.10.4 — Hidden startup console

The BAT entry now hands off to `STARTEN.vbs`, which starts the existing PowerShell GUI host hidden. This removes the persistent console behind the boot screen/control center. Build-action consoles remain visible on demand for interactive approvals and logs.
\n\n## R01.10.5 — Menu recovery\n\nThe hidden launcher logs boot/menu stages and always attempts the existing Neon Control Center after the intro. Menu startup failures show a diagnostic dialog and are recorded in the launcher log.\n

## R01.11 Electron-Neon-Control-Center

Der 8-Sekunden-Cyber-Boot bleibt erhalten. Danach versucht das Buildkit ein eigenständiges Electron-Vollbild-Control-Center mit der bereits installierten lokalen Electron-Runtime. Fehlt sie, wird das bisherige PowerShell-Menü verwendet. `setup-control` richtet die Runtime nur nach ausdrücklicher Zustimmung ein. R06.1 CRLF-`path.txt`-Reparatur und optional SHA-256-verifizierte GitHub-Runtime-Recovery sind enthalten. Siehe `docs/R01_11_ELECTRON_R06_1_ADOPTION.md`.


## R01.11.1 – GitHub-Publish der Originaldateien

Das getrennte `PUBLISH_SOURCE_TO_GITHUB.bat` uebertraegt nach manueller Freigabe den vollstaendigen Quellbaum inklusive Artwork auf den isolierten Kandidatenbranch und prueft nach Push die echten Git-Blobs. Niemals unbemerkt auf Produktion mergen.
