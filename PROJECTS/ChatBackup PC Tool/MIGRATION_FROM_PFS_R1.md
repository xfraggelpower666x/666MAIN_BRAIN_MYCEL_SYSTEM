# ChatBackup — eigenständige Repository-Migration (in Arbeit)

Status: PARTIAL / PFS_DETACH_BLOCKED / DEVICE_READBACK_PENDING
Datum: 2026-11-20
Ziel: xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM, Branch 666MAIN_BRAIN, PROJECTS/ChatBackup PC Tool/
Quelldokumentation: R1 vom 2026-11-20, PC 1.10.5, Scriptable iPhone 1.0.9.

## Eigenständigkeit
- Dieses Projekt wird unabhängig von 666PFS geführt. PFS darf keine Ausführungsautorität über dieses Projekt erhalten.
- Python-Code, Bootstrap, Tests und Dokumentation bleiben normale Git-Dateien, keine ZIP-only-Runtime.
- Keine Änderung an der 666MAIN BRAIN-Identität oder fremden Projekt-Registries.
- Der bei PFS noch vorhandene Child `CHATBACKUP-8001` gehört zum Migrations-Abgleich, nicht zur aktiven Quellcode-Autorität.

## Git-Abgleich
- Bereits im Ziel vorhandener editierbarer PC-Code: v1.10.5.
- R1-Share-URL-Sicherheitskorrektur und Regression: bytegenaue Git-Blob-Parität mit geliefertem R1-Archiv.
- R1-Windows-Host-Probe: bytegenaue Git-Blob-Parität mit R1.
- iPhone-Quellcode liegt im bisherigen Repo nur innerhalb `mobile_scriptable/666_CHATBACKUP_SCRIPTABLE_IPHONE_v1.0.9.zip`; diese Einschränkung muss durch Extraktion in normale Dateien beseitigt werden.
- Andere R1-Dateiänderungen, insbesondere Bootstrap-Dateibytes und Companion-R1-ZIP, sind vor Merge und PFS-Löschung weiterhin abzugleichen. Dieser Zwischenstand ist **kein** vollständiger R1-Paritätsnachweis.

## Geräte-Gates
- PC-Regression in lokaler R1-Lieferkopie 50/50 PASS, Host-Fixture 12/12 PASS.
- Scriptable Node-VM 6/6 PASS, keine echte iPhone-Abnahme.
- Windows EXE und echte Windows-GUI: READBACK_PENDING.
- Bilddownload-Netzwerksicherheit: OFFEN.

## PFS-Detach-Gate
1. Native PFS-Registry/Current lesen und den Scope `CHATBACKUP-8001` isolieren.
2. PFS-Child und zugehörige Provenienz in diesem Projekt vor einer Löschung vollständig spiegeln und hashprüfen.
3. Ziel-R1 samt Scriptable-Quellcode als gewöhnliche Dateien verifizieren; Tests und GitHub Readback.
4. Erst dann PFS-Registry-Detach und scoped child deletion unter PFS-Governance; Pointer zuletzt aktualisieren.
5. Finaler PFS-Readback und Readback des neuen Projektes.

Bis Schritt 3: **KEINE PFS-LÖSCHUNG**.
