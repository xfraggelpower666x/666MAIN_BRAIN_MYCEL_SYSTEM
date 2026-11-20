# Execution Logic

PRE_CHANGE_BACKUP → AUDIT → ADDITIVE_REPAIR → RE_AUDIT → FREEZE → SYSTEM_BACKUP_ZIP → HASH_READBACK

Final export is allowed only when mandatory evidence is fully verifiable. A frozen recovery backup may still be produced when the system is SAFE_LOCK/PARTIAL, provided the status is explicit and no partial package is mislabeled as final.
