# 666LCTS HELP — 666TDH LCTS

Canonical operator triggers:
- `666TDH LCTS SYSTEMSTART` — rehydrate only the Longform specialist.
- `666TDH LCTS STATUS`
- `666TDH LCTS HELP`
- `666TDH LCTS WEITER` — continue the latest valid Longform state.
- `666TDH LCTS NEW CHAT` — persist a single-use LCTS handoff. Next chat requires only `666TDH SYSTEMSTART`; the hub validates the handoff and autoresumes LCTS.

The shared Daemon is autoactive under the Hub and remains authority NONE.

Durable save/update authority: `666TDH UPDATE` at Hub level only. LCTS has no independent UPDATE trigger.
