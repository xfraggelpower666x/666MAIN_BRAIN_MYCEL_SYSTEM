# 666TRACKDESIGN HELP — 666TDH TD

Canonical operator triggers:
- `666TDH TD SYSTEMSTART` — rehydrate only the normal-track specialist.
- `666TDH TD STATUS`
- `666TDH TD HELP`
- `666TDH TD WEITER` — continue the latest valid TD session state.
- `666TDH TD NEW CHAT` — persist a single-use TD handoff. Next chat requires only `666TDH SYSTEMSTART`; the hub validates the handoff and autoresumes TD.

The shared Daemon is already active whenever the parent hub was started. It has no musical, routing, write or update authority.

Durable save/update authority: `666TDH UPDATE` at Hub level only. TD has no independent UPDATE trigger.
