# Open development tracks — evidence-bound

1. **P0 SOURCE_TRANSFER — VERIFIED_PUBLIC_CORE:** Original R03 Electron/Python runtime, renderer, source starter, regression tests, architecture documentation, and independent Git-blob checks are published. Private R02 SQLite, lyrics and backup archives remain offline by design. GitHub CI and Windows host remain pending.
2. **P0 SECURITY — STATIC PATCHED / LOCAL REGRESSION PASS:** ZIP entry bounds/path guards; streaming import hash, archive-ID validation, IPC main-frame restriction, window/navigation block and Python subprocess timeout. Adversarial corpus and real Electron host security acceptance OPEN.
3. **P1 CI — MANUAL_WORKFLOW_REGISTERED / RUN_PENDING:** Scoped `.github/workflows/full-lyrics-intelligence-r04.yml` is workflow_dispatch only; static Python/JS checks and fixture-free 20-case public regression. Never claim Actions success before its job readback. No run initiated and no paid usage authorized.
4. **P1 WINDOWS — BUILD_SOURCE_VERIFIED / HOST_PENDING:** `BUILD.cmd`, `build/BUILD_WINDOWS.ps1`, electron-builder portable + NSIS selectable-directory setup, PyInstaller bridge with mandatory pypdf/docx packaging. Real Windows GUI, Portable EXE, Setup installation/uninstallation and offline runtime acceptance remain OPEN.
5. **P1 CATALOG:** Long-file 100+ lyrics splitting; project/topic classification; JSON records; indices; chat-backup parser adapters; copy actions; structured archive verification. Preserve all existing R03 functionality.
6. **P2 RECONCILIATION — LOCAL_TESTED / NATIVE_READBACK_OPEN:** `engine/reconciliation.py` performs read-only SQLite/category comparison and input Current-candidate fingerprinting; explicitly never promotes candidate SHA to native authority. Four tests passed. External native GitHub Current verification remains a separate owner-project gate.
7. **P2 UX:** Neon theme and comprehensive database dashboard/browser, file-picker, drag-and-drop, English default with optional German.

No closed task is reopened solely because of missing Windows ZIP fingerprint from R02. That earlier freeze question is not a blocker for active architecture development.
