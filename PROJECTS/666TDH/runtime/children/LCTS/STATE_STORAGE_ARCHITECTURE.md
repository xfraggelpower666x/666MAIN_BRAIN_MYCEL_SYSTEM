# LCTS State Storage Architecture

PARENT=666TRACKDESIGNHUB
LIVE_STATE_AUTHORITY=RUNTIME_CURRENT
HISTORY_STATE_AUTHORITY=HISTORICAL_EVIDENCE
BACKUP_STATE_AUTHORITY=RECOVERY_EVIDENCE

LIVE_STATE/LCTS contains exactly one current FULL, PORTABLE and LIVE_STATE descriptor.
VERSION_PILEUP_IN_LIVE=FORBIDDEN.
History and backup remain inert unless explicit recovery is invoked.

Stable live filenames:
666LCTS_LIVE_FULL.zip
666LCTS_LIVE_PORTABLE.zip
LIVE_STATE.md

Persistent writes remain Hub-authorized through `666TDH UPDATE`.
