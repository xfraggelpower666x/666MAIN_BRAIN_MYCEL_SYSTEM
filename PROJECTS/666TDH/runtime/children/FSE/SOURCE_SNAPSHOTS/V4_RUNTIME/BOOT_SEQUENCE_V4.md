# BOOT SEQUENCE — V4

Created: 2026-04-21  
Modified: 2026-04-21  
Change Summary: Canonical boot sequence for the V4 clean-root package.  
Purpose: Define the exact order for controlled startup and reconstruction.

```text
PHASE 01 -> LOAD V4_RUNTIME/SYSTEM_ACTIVE_V4.json
PHASE 02 -> LOAD CORE
PHASE 03 -> LOAD CONTROL v4 PRO
PHASE 04 -> LOAD AUTOMATION ENGINE
PHASE 05 -> LOAD ACTIVE PATTERN SOURCE
PHASE 06 -> LOAD PRESETS
PHASE 07 -> LOAD MODULE REGISTER
PHASE 08 -> OPTIONAL UI / OPTIONAL HANDOFF / OPTIONAL MODULE MOUNT
```

## Guardrails
- Do not boot from `BACKUPS/`
- Do not treat every file in `KERNELS/` as equally active
- Do not mount module ZIPs unless the task actually requires them
- Keep V4 as the first truth layer
