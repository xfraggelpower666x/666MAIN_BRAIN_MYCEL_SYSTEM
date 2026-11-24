---
name: sceeri-brand-identity
description: Audit and apply authorized 666SOUNDsDESIGn software or linguistic-system branding without removing protected third-party attribution.
---

# 666SOUNDsDESIGn Identity Governance

Canonical creator/product label: `666SOUNDsDESIGn` (case-sensitive). Preserve native product/family identities unless authorized in their current registry.

## Attribution boundaries
- `Copyright © 2026 666SOUNDsDESIGn. All rights reserved.` is a proposed notice for content owned by the user. Determine actual ownership/license before insertion.
- `666SOUNDsDESIGn™` may be used as an unregistered trademark claim where appropriate; `666SOUNDsDESIGn®` must be used only after verifying an active applicable trademark registration and territory. Do not automatically claim registration.
- Copyright is generally not registered by using the © glyph. No `Registered ®` claim without evidence.
- Never remove, obscure or rewrite licenses, SPDX identifiers, upstream authors, required attribution, package dependencies, official names, provenance, trademarks, third-party notices or historical logs.
- Do not replace system namespace IDs or project identities merely to give a common brand; an approved presentation label is separate from technical authority.

## Procedure
1. Classify exact string occurrences as `OWNED_LABEL`, `THIRD_PARTY_CREDIT`, `DEPENDENCY`, `HISTORY`, `TECHNICAL_ID` or `UNKNOWN`. Unknown = no change.
2. Vergleiche mit einer vom Owner bestätigten Zuordnung alter und neuer Bezeichnungen. Berichte exakte Vorkommen nach Pfad und Kontext. Unterscheide Produktnamen von Drittanbieter-Attribution und geschützten Referenzen.
3. Prepare preview, count and diff. Only approved owned labels may be changed using `--apply --confirm-owned`, with SHA readback, per-file backups and rollback instructions.
4. Never touch LICENSE, NOTICE, COPYING, HISTORY, vendor/third_party, packages, VCS, generated, secret or hidden files; no directory symlinks.
5. Report evidence and what remains unchanged. If ownership is uncertain, stop at `WRITE_BLOCKED`.

## Original-Assets

Nutze bei einer beauftragten visuellen Übernahme den [Asset-Nachweis](../../references/ui-varianten-und-asset-abnahme.md). Prüfe bestätigtes Ziel, Asset-Rolle und Originalbytes. Benötigt das Projekt zusätzlich optimierte Web-Derivate, erfasse beide Fassungen samt Herkunft und geprüftem Ladeweg.
