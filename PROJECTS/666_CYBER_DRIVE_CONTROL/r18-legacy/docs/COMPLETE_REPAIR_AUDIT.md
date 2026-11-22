# R13 COMPLETE REPAIR · Audit / Repair / Re-Audit

## Scope
Quelle: R13 MENU8 ZIP, vollständig entpackt. Änderungen nur am `START_WINDOWS_MENUE.bat`, `TOOLS/WINDOWS_TOOL_MANAGER.ps1`, Dokumentation und ergänzenden Tests. Keine Treiber- oder Hardwarezugriffe und kein GitHub-Write.

## Belegte Ausgangslage
- B-01 · **HIGH** · Windows-Log vom 21.11.2026: Windows führt Python 3.13.17 als installiert, Projektmanager kann aber keine lauffähige `python.exe` finden. `winget`-Metadaten sind kein Interpreter-Readback.
- B-02 · **MEDIUM** · Ein Python-Registrierungseintrag sperrt die Setup-Route. Schutz vor wiederholter Installation muss erhalten bleiben, aber der Anwender braucht einen nachvollziehbaren Recovery-Weg.
- B-03 · **MEDIUM** · Unvollständige Suche nach App-Paths und möglichen Installationsverzeichnissen, fehlender interaktiver Dateiauswahldialog.

## Reparaturen
- Weitere App-Paths-Registry-Ansichten und Installationshinweise werden read-only als Python-Kandidaten aufgenommen. Zusätzlich gezielte Prüfungen plausibler Installationsorte (keine unbeschränkte Laufwerkssuche).
- `C` zeigt separat die Python-Recovery-Diagnose mit Bericht. Bei Menüpunkt 2 erlaubt `?` einen Dateiauswahldialog für eine vorhandene `python.exe`.
- Registry-Eintrag bleibt Evidenz, kein Beweis für Installation. Bestehende Python-Installationen werden weder deinstalliert noch automatisch repariert oder ersetzt.
- Vorhandene Aktionen 1–9, A, B und 0 sowie die übrigen R13-Anwendungsdateien bleiben erhalten.

## Abnahmegrenzen
- Python-Regression und statische Windows-Menü-Verträge können im Linux-Buildhost überprüft werden.
- Die tatsächliche Ausführung mit Windows PowerShell 5.1, die Erkennung auf dem betroffenen PC, die Einrichtung der `.venv`, die GUI und das Tray sind **READBACK_PENDING**. Es wird **nicht** behauptet, dass Windows-Python bereits wieder funktioniert.
- `TOOLS/REPORTS/TOOL_REPORT_*.json` dient dem gezielten Readback. Wenn `python_candidates` ausschließlich `not_found` oder `execution_or_version_failed` meldet, ist die Reparatur der vorhandenen Python-Installation außerhalb des Projekts erforderlich.
