# CODING PROFI — Three Layer Live Backup R03

This additive module belongs to **L.Y.V.R.A. CODING PROFI**. It does not
create a native CodeForge Alliance authority, second plugin, executable agent,
or independent peer-dispatch runtime.

## Three bound layers

1. **Authority:** installed Coding Profi plugin `plugins_6af753996b5c81918daadc40df266ce7`. Its Plugin Creator release remains authoritative for active skills.
2. **Live development:** `PROJECTS/LYVRA_CODING_PROFI/` on `666MAIN_BRAIN`, including the CodeForge Alliance cooperation subfunction and this verifier.
3. **Unpacked live backup:** `PROJECTS/666_CODEFORGE_ALLIANCE/CODING_PROFI_LIVE/`, containing an *exact Git tree mirror* of the entire live development subtree. The original Alliance R01 files remain preserved next to the mirror as historical artifacts.

## Publisher contract

After **each authorized development change**, the source-owning update flow must:

- Read the freshest target branch HEAD and existing source/backup tree SHAs.
- Preserve an immutable recovery point or protected recovery branch.
- Apply only permitted Coding Profi source changes; never alter sibling projects or the plugin by implication.
- Select the entire **new** `PROJECTS/LYVRA_CODING_PROFI` Git tree SHA and set `PROJECTS/666_CODEFORGE_ALLIANCE/CODING_PROFI_LIVE` to that same tree SHA in the **same commit** (not ZIP, not textual approximation).
- Update the separate `LIVE_BACKUP_STATUS_R03.json` with truthful evidence about source and backup revision. Published receipt cannot self-attest completed readback: mark it `READBACK_PENDING` until checked externally.
- Publish with optimistic branch-HEAD concurrency (`expected_sha`); on a different HEAD, stop and recheck. Never force-update.
- Read back both tree objects and commit SHA independently, then evaluate `verify_tree_pair` with those retrieved values. Only then report `BACKUP_SYNC_VERIFIED` for that specific commit.
- Do not modify any GitHub Current pointer, LYVRA `lyvra` branch, other native project, private plugin release, or foreign authority.

**Important:** Neither this Python module nor this README is a self-running GitHub Action or a plugin-host hook. Updates performed outside the source-owning pipeline are **not automatically captured**. The source-owned update pipeline must invoke this procedure on every authorized change. This release sets the first exact, full-tree backup and verifier but not an always-on cross-repository trigger.

Run local tests using `python -m unittest -v test_live_backup.py`. The verifier has zero external dependencies and never writes files.
