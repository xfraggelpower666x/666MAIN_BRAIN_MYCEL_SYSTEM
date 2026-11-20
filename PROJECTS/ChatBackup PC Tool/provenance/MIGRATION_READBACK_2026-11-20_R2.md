# ChatBackup migration — R2 repository readback (2026-11-20)

STATUS=REPO_REGRESSION_VERIFIED / PFS_DETACH_PENDING / REAL_HOST_READBACK_PENDING
SOURCE=direct GitHub connector readback; current migration branch only
REPO=xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM
BRANCH=migration/chatbackup-r1-detach-20261120
ROOT=PROJECTS/ChatBackup PC Tool
PR=https://github.com/xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM/pull/22

## Confirmed on branch

- Editable PC and Scriptable sources are present; runtime PC v1.10.5, Scriptable v1.0.9.
- `tests/host_acceptance_probe.py` exists. Previous missing-file blocker is fixed in this branch.
- `bootstrap/bootstrap.ps1` Git blob: `70844f51d42dc63ee3b2112634c604980ad32ac8` (R1 expected).
- `mobile_scriptable/source/MANIFEST.sha256` Git blob: `25562cf4cdc3e38908c13ba315838a15d30576b5` (R1 expected).
- GitHub Actions receipt `provenance/REPO_REGRESSION_READBACK.json`: status PASS, 2026-11-20T21:36:14.848288+00:00.
- Receipt records pytest 50 PASS, baseline 16 PASS, release integrity exit 0 with no failed checks, Scriptable Node VM 6 PASS.
- Historic PFS original `666_CHATBACKUP_PC_TOOL_v1.10.0.zip`: `git hash-object` confirms `75547ff2dcd365b30a434d546803ae773ce07bc6`.
- PFS source `xfraggelpower666x/666PFS_CSM`, `main`, `children/CHATBACKUP-8001/CURRENT_STATE.md` still exists and remains unchanged by this audit.

## Superseded intermediary reports

- `provenance/PFS_DETACH_READBACK_2026-11-20.md` documents an earlier 9/10 migration before the binary mirror; it is historical and MUST NOT overrule this direct readback.
- `MIGRATION_FROM_PFS_R1.md` also describes previous file parity gaps. The bootstrap and iPhone manifest gap are now directly closed.
- No claim of full production migration, real-device test or PFS deletion follows from the Linux CI receipt.

## Open blockers / protected gates

1. Windows physical GUI + public-share import/export + EXE build/readback: READBACK_PENDING.
2. Scriptable iPhone real-device host acceptance: READBACK_PENDING. Test doubles do not close it.
3. Image downloader URL/redirect/DNS/content-type/SSRF hardening remains open from R1 audit.
4. `app/chatbackup_gui.py` vs `app/chatbackup_gui.pyw` divergence requires a scoped audit, not blind consolidation.
5. Migration branch PR #22 has not been verified as merged; release/current must not be promoted based solely on this receipt.
6. PFS detach is a separate protected mutation. Verify native PFS current registry/lock/version/authorization, pre-change backup, child-specific deletion, direct readback, and pointer LAST under a valid PFS update. Do not remove PFS child on this audit alone.

## Next executable work

Perform scoped security regression on image-download handling, close device gates with genuine host receipts, review PR #22, and then execute a separately authorized PFS native detach. Preserve source ZIPs as historical provenance, not live authority.
