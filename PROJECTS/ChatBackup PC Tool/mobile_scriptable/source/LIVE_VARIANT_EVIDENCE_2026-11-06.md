# Live Variant Evidence — retained for v1.0.7 (2026-11-06)

Read-only live checks during this repair session showed that ChatGPT share delivery is variant-dependent and can change between requests.

## Variant A — React-Flight

Observed on a live mobile share response:

- `streamController.enqueue(...)`: present
- `linear_conversation`: present
- legacy role/turn markers: present
- v1.0.5-compatible Flight decoder: route resolved
- decoded `linear_conversation` entries: 78

Status: **VERIFIED LIVE SOURCE**

## Variant B — server-rendered transcript

Observed on another live mobile share response in the same session:

- `data-conversation-transcript`: present
- `data-message-role="assistant|user"`: present
- `data-assistant-markdown-root`: present
- `data-user-message-copy`: present
- bounded transcript scan observed 32 message starts in that response

Status: **VERIFIED LIVE SOURCE**

## Volatility finding

Repeated fetches can return a different delivery family. Therefore a parser must not bind one Share URL permanently to one HTML shape.

## Platform limitation

No iPhone/Scriptable runtime is available in this execution environment. iPhone runtime readback remains **PENDING**, not simulated.
