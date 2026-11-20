# 666 ChatBackup — Read-only audit & minimal repair release R1

Datum: 2026-11-20. Paketstand: R1; Anwendungsversionen bleiben **PC 1.10.5** und **Scriptable 1.0.9**. Keine stille Versionserhoehung.

## Bestandswahrung
- Original-ZIP-Dateien bleiben unveraendert, die R1-Pakete sind neue Lieferkopien.
- Historische iPhone-Versionen 1.0.0, 1.0.6, 1.0.7, 1.0.8 verbleiben ausschliesslich im PC-Historienpfad.
- Scriptable-JavaScript wurde bewusst **nicht** umgeschrieben: kein dort bestaetigter Quellcodefehler.
- Die separate mobile R1-ZIP und die im PC-Paket eingebettete mobile R1-ZIP sind identisch.

## Verifizierte Befunde und Repair
- B-01 HOCH: `tests/host_acceptance_probe.py` fehlt im Original-PC-Paket, obwohl Bootstrap, Tests und Release-Guard die Datei voraussetzen. R1 liefert eine offline-testbare und live-funktionsfaehige Host-Probe. Das Fixture erzeugt niemals einen Host-PASS (Exitcode 3).
- B-02 MITTEL: `normalize_and_validate_share_url` akzeptierte URL-Userinfo, Ports ausserhalb 443 und Nicht-HTTP-Schemes. R1 verwirft diese Eingaben und behält HTTP->HTTPS Normalisierung fuer saubere Links bei. Security-Regression in `tests/test_core.py`.
- B-03 OFFEN: Die GUI-Bildfunktion kann externe URLs aus nicht vertrauenswuerdigem Share-HTML abrufen. Der Downloadpfad muss vor produktivem Einsatz mit unbekannten Chats auf SSRF/Redirect-, DNS- und Content-Type-Risiken gehaertet werden. Hier **nicht** ungetestet geaendert, da Drittanbieter-Bildhosts eine vorhandene Funktion sind. Keine umfassende Netzwerksicherheits-Freigabe.
- B-04 OFFEN: `app/chatbackup_gui.py` und `app/chatbackup_gui.pyw` weichen in Recovery- und Dialogfunktionen ab; die .pyw ist der fuer Windows-Hostabnahme dokumentierte produktive GUI-Einstieg. Kein blindes Ueberschreiben/Zusammenfuehren.

## Nachweise
- `pytest tests`: 50/50 PASS auf Linux/Python 3.13.
- Windows-Host-Fixture: 12/12 PASS, Status `FIXTURE_ACCEPTANCE_PASS_HOST_GATE_NOT_CLOSED` (Exitcode 3).
- Scriptable Node-VM: 6/6 PASS **mit Testdoubles** (kein echter iPhone-Host).
- Lokales Quellcode-Build: Python-Syntax pruefbar; Windows-EXE und reale GUI nicht ausgefuehrt.
- Originale SHA-256 in separater Lieferdokumentation; die Host-Receipts in `runtime_readback/` sind Testbelege, keine realen Geraete-Receipts.

## Gate-Status
- Lokal testbare Quellcode- und Release-Vertraege: nach finalem R1-Readback PASS, siehe `R1_VALIDATION_RESULTS.json`.
- Echte Windows-Hostabnahme (GUI + Live-Share): READBACK_PENDING.
- Echte Scriptable-iPhone-Abnahme und Live-Share-Export: READBACK_PENDING.
- Kompilierte Windows-EXE: READBACK_PENDING.

## Freeze
`LOCAL_SOURCE_FREEZE_R1`, **nicht** Production Host Acceptance. Bei anstehendem Release die unveraenderten produktiven Entry-Points auf realen Geraeten pruefen. Kein Commit, kein Deployment, keine Veraenderung an externen Repositories.
