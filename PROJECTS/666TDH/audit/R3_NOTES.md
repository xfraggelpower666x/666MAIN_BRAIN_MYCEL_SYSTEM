# 666TDH R3 — Audit, Repair, Re-Audit, Freeze, Systemsicherung

Native: `666TRACKHUB-001` · GitHub `666MAIN_BRAIN/PROJECTS/666TDH` · v1.15.0 (unverändert).

## Audit und minimale Reparaturen

1. **TDH-UI-01**: `runtime/ui/render_html.py` zeigte bei einem Tab-Klick keine eigenen Inhalte. R3 zeigt verifizierte Konfigurationsdaten, aktuelle Quellen, Holds und Fakten. JavaScript-Aktionen bleiben lokal; Trigger nur kopieren.
2. **TDH-DAEMON-01**: Die neun Befehle aus `runtime/hub/daemon/DAEMON_MENU.md` waren im Repo-Parser nicht registriert. Nun werden sie über denselben Root-Router aus `runtime/TRIGGERS.json` als schreibgeschützte Begleitaktionen erkannt. STOP mutet lediglich die aktuelle Ausgabe; kein persistenter Dienst wird vorgetäuscht.
3. **TDH-RECOVERY-01**: Vollständigen getrackten TDH-Git-Baum per `STARTEN.bat` / `tools/verify_and_backup.py` außerhalb des Repos als ZIP sichern. Schutz: Git-HEAD, Dirty-Checkout, Scope, ZIP-CRC, Dateiliste und einzelne/gesamte SHA-256.
4. **TDH-CONTROL-01**: `tdh.py` weist doppelte JSON-Schlüssel in Current- und Steuerdaten zurück.

## Tatsächlicher Re-Audit

- Python: **28/28 bestanden**, einschließlich der sieben bisherigen `tests/test_tdh.py`-Tests; Umgebung **synthetischer isolierter Current**, nicht vollständiger produktiver Checkout.
- Chromium (lokal): **6/6 Oberflächen**, Hub und fünf Childs bei 390px, echte Ansichten, Kopier-Menü und Daemon, 0 externe Requests, 0 JS-Fehler.
- Git-Snapshot-Helfer: vollständig ausgeführter Test an künstlichem Git-Checkout, CRC und Hashes bestanden, Dirty-/In-Repo-Blocker bestanden. Das ist **keine** produktive Offline-Sicherung.
- Unverändert: alle fünf Childs, musikalischer Quellstand, PFS-Runtime-Authority=NONE, externes FSE-Original, Quell-HOLDs.

## Freeze und Recovery

Ausgangsbasis: `ddc4ab7318ea52f5760d88613f9ea741eda90e0b`; Git-Recovery-Branch: `backup/666TDH/pre-R3-max-work-20261120-ddc4ab73`.
Native Quellversion v1.15.0 bleibt, die Additiv-Capability wird R3.
Der vollständige Git-Prechange-Stand bleibt über den Recovery-Branch zugänglich. Ein vollständiges Offline-ZIP kann mit dem neuen Python-Helfer auf dem lokalen Repo-Checkout erzeugt werden, wurde hier aber **nicht** aus dem echten produktiven 131MB-Baum generiert.

**Offen:** tatsächlicher produktiver vollständiger Python-Testsuite-Lauf auf 352 getrackten Dateien, Windows-Doppelklick, native interaktive Chat-Host-Abnahme und Rückleseprüfung des externen FSE-Source-Vaults. Keine erfundenen Pass-Labels.

Publikationsfolge: Pre-Change-Ref → Datencommit → SHA-Readback → Pointer-only-Commit → checked fast-forward → produktiver Readback → keine weiteren Writes.
