# CODING PROFI R04 — Push-Trigger Abnahmemarker

Stand: 2026-11-25
Status: SOURCE_PUSH_SENT / HOST_RECEIPT_PENDING
Owner: L.Y.V.R.A. CODING PROFI
Scope: repository-lokaler Live-Backup-Automatiktest.

Dieser einzelne neue Quelldatei-Commit soll den vorhandenen Workflow
`.github/workflows/coding-profi-live-backup.yml` auslösen.
Der Workflow muss den gesamten Quellbaum `PROJECTS/LYVRA_CODING_PROFI`
entpackt im Backup-Unterverzeichnis `CODING_PROFI_LIVE` nachziehen.
Er darf weder die operative Plugin-Authority noch fremde Projekte verändern.

Dieser Marker ist ein Prüfeingang, KEIN Test-Receipt.
Abnahme ausschließlich nach echtem GitHub-Actions-Run und direktem Tree-Readback.
