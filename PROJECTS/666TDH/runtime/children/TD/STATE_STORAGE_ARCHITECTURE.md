# TD State Storage Architecture

PARENT=666TRACKDESIGNHUB
LIVE_STATE_AUTHORITY=RUNTIME_CURRENT
HISTORY_STATE_AUTHORITY=HISTORICAL_EVIDENCE
BACKUP_STATE_AUTHORITY=RECOVERY_EVIDENCE

LIVE_STATE/TD contains exactly one current FULL, PORTABLE and LIVE_STATE descriptor.
VERSION_PILEUP_IN_LIVE=FORBIDDEN.
History and backup never become current by timestamp or discovery alone.

Stable live filenames:
666TRACKDESIGN_LIVE_FULL.zip
666TRACKDESIGN_LIVE_PORTABLE.zip
LIVE_STATE.md

All persistent writes remain Hub-authorized through `666TDH UPDATE`.
