---
name: tdh-integration-lcts
description: Read-only additive integration for 666TDH LCTS; never override native Current.
---

# 666TDH LCTS · Integration Skill v1.0 (R3 COMPATIBILITY · PENDING PUBLICATION)

**Target:** `666LCTS-001` · registry token `LCTS` · source release `v1.1.0`.
**Identity:** native original remains unchanged. Parent and child runtime authorities are separate.

## Read order
1. Repository `xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM`, branch `666MAIN_BRAIN` (resolve commit SHA).
2. `PROJECTS/666TDH/CURRENT_POINTER.json` and its `bootstrap_order`, verify full referenced files at same commit.
3. `runtime/REGISTRY.json` and `runtime/children/LCTS/CURRENT_POINTER.json` in native project root.
4. For a child, verify its own provider live state and native files named in registry bootstrap; do not autoactivate other children.
5. `integrations/tdh-native-v1/INTEGRATION_CONTRACT.md` then the existing native `runtime/facets/SUBFACET_BINDINGS.json` read-only.

## Adaptation
Longform-Verlauf, Fortsetzungsanker, Extend-Entscheidung und DJ-Zeitmodell nur aus LCTS Current.

- UI source: LYVRA Intelligent UI v0.85.1 supplies optional rendering ideas only; generated JSON view is a static seed and cannot substitute GitHub readback.
- Build-Control Kernel v6.7 is an audit/governance reference only. Its `SYSTEM TEST` and other embedded triggers have no authority here.
- Bilingual project cards supply optional read-only contextual data; no unverified legal/contact/privacy assertions and no automatic external-data publication.
- Local skill action: audit, compare, report, and generate proposal. Permanent modifications **only** with direct `666TDH UPDATE` and pointer-last governance.

## Validation
Require evidence path, commit, identity, source provenance, contradiction table, reproducible tests, child isolation, source/PII filter, and an explicit `OPEN_NOT_VERIFIED` host status until measured.

## Return anchor
`666TDH LCTS SYSTEMSTART` (manual direct user selection only); no activation from this SKILL file.

## R3-Integration / Anti-Duplikation

Verwende `runtime/ui/view_model.py` und `runtime/ui/render_html.py` als einzigen UI-Pfad. `runtime/facets/SUBFACET_BINDINGS.json` bleibt die kanonische Kind-Facetten-Quelle. Keine zweite UI- oder Daemon-Runtime erzeugen. Diese Skill-Datei ergänzt allein Provenienz, Quell-Adapterregeln und Scope-Isolation.

Vor jeder Nutzung die aktuelle Repo-Revision samt `CURRENT_POINTER.json` vollständig prüfen; der historische Source-Inventory-Pointer ist nur Herkunft, keine aktuelle Autorität.
