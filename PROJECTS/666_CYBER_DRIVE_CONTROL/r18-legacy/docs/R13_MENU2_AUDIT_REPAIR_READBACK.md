# R13 MENU-2 · Audit → Repair → Re-Audit

Datum: 21.11.2026 · Projektstand R13 v1.12.0 + MENU-2, keine Änderung der Kern-API.

## Analysis und bestätigte Befunde

| ID | Vorher | Wirkung | Reparatur | Gegenprobe |
|---|---|---|---|---|
| B-01 | R13 hatte zuvor sieben Starter, MENU-1 bereits einen | Einstieg inkonsistent | Nur `START_WINDOWS_MENUE.bat` als Windows-Starter erhalten | genau 1 Batchdatei im Auslieferungspaket |
| B-02 | MENU-1 `where py/python` prüfte Existenz statt Python-Funktion | Store-Alias wurde fälschlich akzeptiert | PowerShell-Helper startet jeden Kandidaten mit `-c`, prüft Version >=3.10 und filtert WindowsApps | statischer Regressionstest; echter Windows-Host offen |
| B-03 | Setup endete bei fehlendem Python | kein Installationspfad | nach Einwilligung Python 3.13 via `winget`; sonst offizieller manueller Hinweis | Quelltest, Windows-Installationslauf OFFEN |
| B-04 | Python-Interpreter konnte zwischen Aktionen wechseln | `pip`/Runtime auseinander | Anwendungen und Readback nutzen nur `.venv/Scripts/python.exe` | Quelltest; Hostprüfung OFFEN |
| B-05 | fehlende Reinstall-/Upgrade-Möglichkeit | veraltete/fehlende Python-Pakete | Menu 2 Setup/Repair; Menu 3 Update der lokalen pip-/Projektpakete | Quelltest, Hostprüfung OFFEN |
| B-06 | Setup ohne Abschlussreadback | scheinbarer Erfolg bei kaputten Imports | Importcheck + JSON-Bericht unter TOOLS/REPORTS | Quelltest, Windows-Readback OFFEN |

## Sicherheits- und Erhaltungsregeln

- Originalprojekt R13 MENU-1 unverändert gelassen; neue Version als eigener Ordner.
- Alle 55 Python-Quelldateien und Tests aus MENU-1 unverändert. 12 neue Tests separat.
- Diagnose arbeitet lesend; Installationen/Updates nur nach ausdrücklicher Auswahl und Benutzerbestätigung.
- Keine Treiberinstallation, keine Firmware-, HID- oder Lock-Key-Schreiboperation.
- Vorhandene beschädigte `.venv` wird nicht gelöscht. Fehlendes `winget` führt zum manuellen Python-Hinweis.
- Installation über `winget` und pip benötigt ggf. Netzwerk, Berechtigung und Benutzerbestätigung; keine Erfolgsgarantie ohne Windows-Host.
- Optionale Tools: smartctl, wheel, build. Pflicht: Python >=3.10, pip, klrw, psutil, pystray, PIL, pytest.

## Re-Audit

- `PYTHONPATH=src pytest -q`: **199/199 PASS** (187 Bestand + 12 MENU-2-Vertragstests).
- `python -m compileall -q src tests`: PASS.
- `python -m pip wheel --no-deps --no-build-isolation`: PASS.
- Bytevergleich der 55 vorherigen `.py`-Dateien: 55/55 identisch.
- Genau eine `.bat`: `START_WINDOWS_MENUE.bat`.
- Echter Windows-PowerShell-Installer, winget-Nutzung und native Tray-Abnahme: **READBACK_PENDING**.

## Nächste ausführbare Abnahme

1. `START_WINDOWS_MENUE.bat` doppelklicken, `1` Diagnose.
2. `2` Setup/Repair; die ausdrücklichen Fragen bestätigen (installiert Python nur bei Fehlen).
3. `1` Diagnose wiederholen; `TOOLS/REPORTS/TOOL_REPORT_*.json` prüfen.
4. `4` Tray starten, `7` Windows-Readback. Bericht bei Auffälligkeiten bereitstellen.
