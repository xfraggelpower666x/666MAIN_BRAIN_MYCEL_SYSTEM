# Open development tracks — evidence-bound

1. **P0 SOURCE_TRANSFER:** Publish actual R03 Python and Electron source files under this project with original relative path structure. Compare each readback SHA/contents with the local candidate. Do not publish legacy lyrics databases, exports, conversation content, or archives.
2. **P0 SECURITY:** Ensure Electron contextIsolation, sandbox, IPC allowlist, file limits and import path safety retain R03 behavior. Validate source file dependencies.
3. **P1 CI:** Add scoped tests only after exact source transfer. Python unit tests (10/10 local baseline) and Electron JS syntax checks. Workflows under .github require separate repository governance review; do not publish automatically.
4. **P1 WINDOWS:** One developer starter, dependency checks and explicit repair/install. Direct GUI test, then portable EXE and selectable-directory Windows installer built on Windows. Production binaries must bundle required runtimes; record validation.
5. **P1 CATALOG:** Long-file 100+ lyrics splitting; project/topic classification; JSON records; indices; chat-backup parser adapters; copy actions; structured archive verification. Preserve all existing R03 functionality.
6. **P2 RECONCILIATION:** Read-only compare candidates with independently verified owner-project Current; proposals only, never cross-system writes.
7. **P2 UX:** Neon theme and comprehensive database dashboard/browser, file-picker, drag-and-drop, English default with optional German.

No closed task is reopened solely because of missing Windows ZIP fingerprint from R02. That earlier freeze question is not a blocker for active architecture development.
