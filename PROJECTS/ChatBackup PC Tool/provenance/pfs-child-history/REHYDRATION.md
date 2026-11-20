# Rehydration

ENTRY_ID=CHATBACKUP-8001
STATE=PARTIAL
1. Read SYSTEM_IDENTITY.md.
2. Read SOURCE_BINDING.md.
3. Do not execute or autoload this child while PAYLOAD_STATE remains pending.
4. Migrate the latest directly verified functional payload from the bound Drive recovery source.
5. Validate payload, provenance and readback.
6. Mark READY only after repository payload verification.

CHILD_AUTOLOAD=FORBIDDEN
