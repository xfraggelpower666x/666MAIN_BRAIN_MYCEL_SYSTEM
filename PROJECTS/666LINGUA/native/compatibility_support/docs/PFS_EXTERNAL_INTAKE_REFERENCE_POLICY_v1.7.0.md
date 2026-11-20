# 666PFS External Intake Reference Policy — LYVRA DOLMETSCHER v1.7.0

## Status

```text
REFERENCE_MODE=INERT_ONLY
DOCUMENT_STATUS=DRAFT_NOT_CANONICAL
PFS_CORE_DEVELOPMENT=FORBIDDEN_IN_THIS_PROJECT
REGISTRY_WRITE=NOT_PERFORMED
POINTER_WRITE=NOT_PERFORMED
DRIVE_WRITE=NOT_PERFORMED
LYVRA_MUTATION=FALSE
```

## Zweck

Die beigefügten 666PFS-Draftdateien werden ausschließlich verwendet, damit zukünftige LYVRA-DOLMETSCHER-Versionen einen vollständigen, prüfbaren **externen Child-Kandidaten** liefern. Sie aktivieren weder 666PFS noch 666CSM und erzeugen keinen Router, Bootstrap, Updateweg oder globalen Trigger.

## Lokale Lieferregel

Jede zukünftige Kandidatenfreigabe muss mindestens `PFS_INTEGRATION_MANIFEST.json`, `CHILD_PASSPORT_CANDIDATE.json`, `README.md`, `CHANGELOG.md`, `AUDIT.md`, `TEST_REPORT.md` und `MIGRATION_NOTES.md` enthalten. Lokal belegte Paketwerte werden detached ausgewiesen; nicht belegte externe Zustände bleiben `READBACK_PENDING` oder `NOT_WRITTEN`.

## Autoritätsgrenze

Der externe Entwicklungs-Chat darf Fachlogik, Tests, Audit, Freeze und Kandidatenpaket erzeugen. Er darf keine 666PFS-Registry-, Pointer-, Menü-, Drive- oder Core-Ergebnisse behaupten. Die spätere Identitäts-, Versions- und Hashklassifikation bleibt beim autorisierten 666PFS-Host.
