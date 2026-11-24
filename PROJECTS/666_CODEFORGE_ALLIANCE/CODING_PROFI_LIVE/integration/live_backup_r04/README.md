# CODING PROFI — Live-Backup Auto-Sync R04

**Owner:** L.Y.V.R.A. CODING PROFI (eine operative Plugin-Authority).

**Quelle:** `PROJECTS/LYVRA_CODING_PROFI/`.
**Zusätzliche entpackte Sicherung:** `PROJECTS/666_CODEFORGE_ALLIANCE/CODING_PROFI_LIVE/`.
**Trigger:** Ein Push auf Branch `666MAIN_BRAIN`, der die Quelle verändert; zusätzlich manuell auslösbar per `workflow_dispatch`.

Der Workflow `.github/workflows/coding-profi-live-backup.yml` prüft mit einem unveränderten `node --test` die isolierte lokale Implementierung und startet anschließend `sync-live-backup.mjs`. Der Sync liest den *aktuellen* GitHub-HEAD, die beiden Tree-Objekte und erstellt nur bei unterschiedlichen SHAs einen neuen Commit. Dieser Commit übernimmt denselben Quell-Tree vollständig ins Backup, ohne ZIP, Datei-Auswahl oder Veränderungen an anderen Projekten. Nach der Veröffentlichung werden beide Trees direkt zurückgelesen.

## Sicherheitsgrenzen

- **Original-Plugin:** `plugins_6af753996b5c81918daadc40df266ce7` bleibt alleinige Plugin-Authority. Diese Synchronisierung ist kein Plugin-Release und besitzt keine Plugin-Toolhandles.
- **Kein Cross-Repository-Auto-Trigger:** Der Workflow sieht ausschließlich GitHub-Push-Ereignisse *dieses* Repositories. Änderungen im privaten Coding-Profi-Plugin müssen durch dessen release-gebundenen Publikationsworkflow zuerst unter `PROJECTS/LYVRA_CODING_PROFI/plugin_source/` gespiegelt werden.
- **Keine Fremdsysteme:** Nur der Backup-Unterbaum `CODING_PROFI_LIVE` darf vom Sync geändert werden. R01-/R02-Dateien neben ihm bleiben unangetastet. Die Alliance bleibt eine Coding-Profi-Unterfunktion, keine neue Authority.
- **Konfliktschutz:** Kein `force`-Update. Auf API-Konflikte wird mit erneutem Lesen reagiert. Unerwartete Fehler und falsche Readback-Trees führen zu Fehlstatus, nicht zu erfundenem PASS.
- **Keine Secrets:** Nur das kurzlebige, von GitHub Actions injizierte `GITHUB_TOKEN` wird für den eigenen GitHub-Write verwendet und niemals protokolliert.
- **Kosten:** Standard-`ubuntu-latest`-Runner im bestehenden öffentlichen GitHub-Repository. Keine größere Runner-Klasse, keine Zusatzinfrastruktur, keine externen Provideraufrufe.

## Verifikation

```bash
node --check integration/live_backup_r04/sync-live-backup.mjs
node --test integration/live_backup_r04/test-sync-live-backup.mjs
```

**Statusgrenzen:** `LOCAL_TEST_PASS` ≠ `WORKFLOW_RUN_PASS` ≠ `PLUGIN_HOST_ACCEPTANCE`. Eine erfolgreiche GitHub-Actions-Synchronisation beweist nur die Sicherung der aktuell im Repository gespeicherten Coding-Profi-Quelle. Sie beweist nicht, dass ein nur im Plugin erfolgter Release automatisch erfasst wird.

## Weiterführung

Prüfe nach jedem relevanten Quell-Push den GitHub-Actions-Run und unabhängig die Tree-SHA-Gleichheit unter demselben verifizierten Commit. Prüfe nach jedem Plugin-Release zunächst die exakte Plugin-Release-ID und die aktualisierte `plugin_source/`-Version. Wenn diese fehlt, melde `PLUGIN_TO_SOURCE_SYNC_PENDING`.
