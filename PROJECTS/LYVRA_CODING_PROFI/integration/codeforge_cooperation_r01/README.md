# CODING PROFI — Native CodeForge cooperation R01

**Authority:** L.Y.V.R.A. CODING PROFI coordinates coding work. Every participating native system retains independent Current, owners, credentials, release gates, write paths and recovery. This is an additive companion to the existing `sceeri-coding-multisystem-orchestrator` skill; no replacement, identity merge or host installation.

**Existing plugin current on 2026-11-23:** `sceeri-intelligence` v0.87.7, release `pluginrel_6b044ff155b481918869cf4d8f68d807`.

## Actual technical capability
`coordination.py` defines typed `SourceReceipt`, `WorkOffer` and deterministic `coordination_summary`. An offer can only be READ_ONLY or PATCH_PROPOSAL. It validates family, source/owner binding, SHA and relative paths; it explicitly rejects an attempt to convey a write approval. Untrusted text, including embedded commands, remains data.

The module **does not call peer plugins**, run commands, invoke Coder's external builder, modify a repository, charge costs, or store secrets. A real cross-plugin host invocation, bidirectional exchange or end-to-end collaboration is **not yet accepted**. The read-only coordination contract is a runnable local building block, not a federated deployment.

## Known native source locator snapshots (2026-11-23)
| Family | Native repository / branch | Observed HEAD (source locator; not native pointer rehydration) |
|---|---|---|
| Coding Profi workspace | `xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM` / `666MAIN_BRAIN` | `d8f82681f0ca19722d33539f4cd1fdf180317f3f` |
| CLIC | `xfraggelpower666x/666CLICPRO` / `main` | `086d5df1d5b827c2217daeb754e998037b0fcb11` |
| DEV | `xfraggelpower666x/666SOUNDsDESIGn-APP-DEVELOPMENT` / `666DEV` | `e1ef4abf5830bcd3ef477543e4a626f0c4835aff` |
| LYVRA | `xfraggelpower666x/LYVRA-Living-Yielding-Vibration-and-Resonance-Architecture` / `lyvra` | `5c47c2d17ad676dfd6da7e376d062a03690666c3` |
| MAIN BRAIN | `xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM` / `666MAIN_BRAIN` | `d8f82681f0ca19722d33539f4cd1fdf180317f3f` |
| PFS | `xfraggelpower666x/666PFS_CSM` / `main` | `08989d5dc71259cbebf108c71d2e315aa9ac28a1` |
| Coder | External optional app | No native repository authority confirmed |

**Critical:** Repository HEAD alone is not native Current/pointer readback. Before any native work, read that system's current registry/pointer and relevant revision independently. None of these systems is activated here.

## Run tests
```
cd PROJECTS/LYVRA_CODING_PROFI/integration/codeforge_cooperation_r01
python -m unittest discover -v -p "test_*.py"
```
The locally executed initial contract test suite passed **11/11**. A GitHub readback verifies source publication, not execution inside a plugin or other native host.

## Next acceptance
Bind only verified host-provided connector call handles and explicit per-owner permissions to this contract. For each offer, keep SOURCE, OFFER, ACCEPTANCE, EXECUTION, READBACK separate; avoid automatic cost, secret access, trigger activation or foreign repository writes. No new desktop application, global router or competing authority.
