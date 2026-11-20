# 666TDH Universal Update / Save Authority

CANONICAL_UNIVERSAL_UPDATE_TRIGGER=666TDH UPDATE
ROLE=UNIVERSAL_UPDATE_AND_SAVE_TRANSACTION
SUBSYSTEM_UPDATE_TRIGGERS=NONE

The update transaction covers:
HUB + TD + LCTS + DTSTE + DAEMON + HANDOFF + LIVE/HISTORY/BACKUP + PFS preservation + registries + pointer-last.

COMPLETE_VERIFIED requires:
fresh authority read
pre-change backup
history checkpoint
valid delta integration
audit
minimal repair if required
re-audit
freeze
FULL + PORTABLE packages
provider upload
provider readback
PFS release + backup readback
registry publication/readback
TDH current pointer promotion
PFS core pointer LAST
no writes after PFS pointer

Partial publication never becomes final authority.
