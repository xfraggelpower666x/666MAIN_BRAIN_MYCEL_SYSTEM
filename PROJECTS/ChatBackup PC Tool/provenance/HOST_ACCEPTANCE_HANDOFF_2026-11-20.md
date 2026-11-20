# ChatBackup Host Acceptance — Stand 2026-11-20

STATUS=PARTIAL / WINDOWS_CI_READBACK_PENDING / USER_WINDOWS_HOST_PENDING / IPHONE_HOST_PENDING
TARGET_REPO=xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM
TARGET_BRANCH=666MAIN_BRAIN
TARGET_PROJECT=PROJECTS/ChatBackup PC Tool
PC_VERSION=1.10.5
SCRIPTABLE_VERSION=1.0.9

## Verifizierte Ausgangslage

- PR #24 ist in 666MAIN_BRAIN integriert (Merge 6e47a07b22c32971f87370dbec9285fc063b66d0).
- Sechs geänderte Sicherheitsdateien haben produktive Git-Blob-Parität mit dem getesteten Branch.
- Migration-Regression 72/72 Pytests, 16/16 Basistests, 6/6 Scriptable-Node-Testdoubles, Release Integrity PASS.
- Windows-CI-Workflow `.github/workflows/chatbackup-windows-host-exe-validation.yml`, Commit 97c31c6cc40c953efe7444a5b169be346b58ae61, per GitHub-Fetch zurückgelesen.
- CI-Ausführung, Windows-EXE-Artifact, GUI- und Host-Receipts sind bei Erstellung dieses Handoffs nicht gelesen/bestätigt.

## A. Windows CI (nicht Nutzer-Host)

Workflow `ChatBackup Windows host and EXE validation` prüft auf windows-latest:
1. Regression + Release Integrity.
2. GUI/Tkinter mit `tests/runtime_readback_probe.py`.
3. Offline-Share-Fixture (Exitcode 3, Gate bleibt offen).
4. Bestehenden PyInstaller-Spec und EXE-Start-Smoketest.
5. SHA-256 / Lauf-Receipt, Artifact-Upload (14 Tage).

Resultate erst nach Workflow-Run und heruntergeladenen Receipts auf PASS setzen. Ein Cloud-Runner ist **nicht** identisch mit dem tatsächlichen Windows-PC des Nutzers.

## B. Echter Windows-PC

1. Produktivprojekt als Arbeitskopie von `666MAIN_BRAIN` auschecken.
2. `VERIFY_WINDOWS_HOST_ACCEPTANCE.bat` starten; öffentlichen ChatGPT-Share-Link eingeben. Der Bootstrap prüft Abhängigkeiten und verwendet den realen Python-/Tkinter-Pfad.
3. Erfolg nur bei `WINDOWS_RUNTIME_READBACK_PASS` **und** `WINDOWS_HOST_ACCEPTANCE_PASS` mit nachprüfbarem `runtime_readback/windows_runtime_readback.json` und `runtime_readback/host_acceptance_*/windows_host_acceptance_receipt.json`.
4. `BUILD_EXE.bat` lokal starten, `dist/666_CHATBACKUP_PC_TOOL.exe` erzeugen und starten. Benutzerbedienung (Import, Vorschau, Bilddownload, Export/Readback) tatsächlich testen.
5. SHA-256 der EXE, Python-Version, Windows-Version, genaue Prüfstati und Fehlermeldungen dokumentieren. Keine Tokens/Cookies/privaten Chat-Inhalte veröffentlichen.

## C. iPhone / Scriptable v1.0.9

1. Scriptable-App auf tatsächlichem iPhone öffnen.
2. Diagnostics / Self-Test -> Run offline self-test: erwartetes `SELFTEST_PASS` (7/7).
3. Diagnostics / Self-Test -> Run host acceptance mit eigenem öffentlichen `/share/`- oder `/s/`-Link ausführen.
4. Nur `HOST_ACCEPTANCE_PASS` mit validiertem `host_acceptance_receipt.json` sowie überprüften FileManager-Readbacks schließt den Gate.
5. Kontrollierten Test der normalen Public-Share-Importfunktion durchführen; Asset-Pointer ohne echte Bytes bleiben nur als Metadaten.
6. Sichere JSON-Receipts ohne Gesprächsinhalte/URLs/Credentials in einem eigenen Governance-Schritt zur Prüfung übergeben.

## D. PFS-Detach (nicht im aktuellen Scope)

Der Child `children/CHATBACKUP-8001` bleibt unangetastet. Vor separatem PFS-Detach: aktuelle native PFS-Registry, Current/Lock, Backup, Spiegelhash und berechtigte Mutation prüfen; scoped Entfernung und Registry-Änderung in getrenntem kontrolliertem PFS-Vorgang, Pointer zuletzt, direkter Readback. Kein PFS-Detach aufgrund eines CI-PASS alleine.

## Offene Punkte

- WINDOWS_CI_READBACK_PENDING: Actions-Jobstatus, Windows-EXE-Binärhash, Runtime-Receipt, EXE-Smoketest.
- WINDOWS_USER_HOST_PENDING: reale Installation, UI, Live-Share und Export.
- IPHONE_HOST_PENDING: tatsächliches Scriptable-Receipt.
- PFS_DETACH_BLOCKED: erst nach separaten Gates und nativer Governance.
