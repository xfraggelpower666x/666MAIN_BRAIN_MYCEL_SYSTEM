# R04 vs R05 GitHub-native reconciliation — 2026-11-22

Comparison source: live GitHub `666MAIN_BRAIN/PROJECTS/666_AUTO_DJ_STUDIO/` direct Contents API blob SHA listing and R05 local package file bytes. Main HEAD at start: `ee2aa348644dee75ca4e7e6e389afeda5e39f90f`. The GitHub Current at inspection was `R04_BLOCK_RENDER_SOURCE_LIVE`. A diff of filename names or similar features cannot prove identical behavior.

**Result:** R05 is not a verified byte-identical export of R04, and MUST NOT overwrite it. Original R03 PowerShell GUI is preserved at `legacy/tool.ps1`. Its ability to start with included FFmpeg is now exposed as Option 7 of the same BUILD.bat.

**Actions:** No GitHub writes; no production promotion; no Windows compilation or execution claimed. Candidate differs from canonical sources; details follow.

| Status | Number |
| --- | ---: |
| IDENTICAL | 0 |
| DIFFERENT | 13 |
| MISSING_IN_DELIVERY | 8 |

## Per-file SHA comparison

| Path | Result | R04 Git blob SHA | Candidate Git blob SHA |
|---|---|---|---|
| `BUILD.bat` | DIFFERENT | `75c9fe0986b974f59bcf24a103382e240e6498f5` | `ec16d39b05aa393d8e1c9c19bf92f50eda24dfb6` |
| `CURRENT.json` | MISSING_IN_DELIVERY | `14dba67697c31ad599ff50849c9690fa41fef446` | `—` |
| `README.md` | DIFFERENT | `25188fcfcfb43bcf71a6ca572ca68488848707a6` | `30e43e4f4b12cd28b3045e751b05c477c1349cca` |
| `package.json` | DIFFERENT | `c3b200f85c5f2c10dc01efd88710cbeb69beb2f4` | `e8a6e39f2c0a2c7161b103a1ed28deda86ff5b6d` |
| `app/index.html` | DIFFERENT | `b0ca1409afb59757aa62ceb98e972a02c1eb1d46` | `f1a38c3bb19a080966c84d423fb9ca0beabbe4f6` |
| `app/main.js` | DIFFERENT | `baf61ef1404532c562a6dde3b3e7647e7f5438c4` | `71e22dbad38f4ec814839043461de072182bf89f` |
| `app/preload.js` | DIFFERENT | `3363d03624e236cef9b0fe553d424d6cb6a9548c` | `2fd65eb599356e8965121535b67965c6cc3222e0` |
| `app/renderer.js` | DIFFERENT | `d92750da5c0015533f25090f96de7d99b204fd4d` | `d1d7822a27527d9200b6dcf17b0ab72497c6efb6` |
| `app/theme.css` | DIFFERENT | `d8118047f7b502dc0f7ea172eb86ac2adc7251b4` | `69b5bcef0a5dcedd1c9e34133d67a4dfc86de552` |
| `build/BUILD.ps1` | DIFFERENT | `dc9916eea0114dfa3d11295720a12b6d6bbbff29` | `8d4ee0cef6e1c4d59c7aa1f8475a4234751767b6` |
| `build/PROVISION_FFMPEG.ps1` | MISSING_IN_DELIVERY | `cc18239d9cf4d5ce38b384766898b8bdeaf2d189` | `—` |
| `docs/AUDIT_R01.md` | MISSING_IN_DELIVERY | `ab1e843c425d501db65bf55da3f43ee8a5eed1d3` | `—` |
| `docs/CONTINUITY.md` | MISSING_IN_DELIVERY | `a84bf47c071e64b32f29ee23f3b7047a5fb210ec` | `—` |
| `docs/PORT_R03.md` | MISSING_IN_DELIVERY | `96f568fe8cca3ad5dd17e42a133124b61c4c7a59` | `—` |
| `docs/R04_ACTIVE_DEVELOPMENT.md` | MISSING_IN_DELIVERY | `95f5e0767bdedbc0eeb9dbf095a18329fbde366a` | `—` |
| `engine/legacy_planner.py` | DIFFERENT | `b06812f7ead03473e43978818cb64f250e5013d8` | `61a9701a8d50217e7f49bcb65da4ea08b72e9d67` |
| `engine/playlist.py` | DIFFERENT | `6fe262bb5d11dd13de6389b453a0e3c66a023f79` | `decda8c4646c4bd71a36dc9b213f5317565db1dc` |
| `engine/worker.py` | DIFFERENT | `6d0e8d73b9071a2c022bd6f01decf3f37a5aec23` | `42796e3dc6088dff21bac979ec45e923a0eecea1` |
| `tests/test_engine.py` | MISSING_IN_DELIVERY | `6569dff0e1737b8f9263230491604952fd228fff` | `—` |
| `tests/test_legacy_planner.py` | DIFFERENT | `83135c0bc4093cb81900824d769726b7b72ab0ae` | `c67b216ca4aeb1294edf66424c0eae3a39eea596` |
| `tests/test_playlist.py` | MISSING_IN_DELIVERY | `9e3feee23d493bd827cd62b5dd68e44fae760145` | `—` |


## Repair scope
- Added direct legacy GUI entry, with hash-checked FFmpeg copy into legacy original directory; kept legacy/tool.ps1 unmodified.
- Retained one root BUILD.bat, Electron build menus and standalone FFmpeg.
- Did NOT silently substitute R05 files for the canonical GitHub R04 implementations.
- Next governed integration: apply targeted changes to canonical files after comparing caller contracts, then independent file readback and pointer-last GitHub publication. A compiled Windows portable executable and NSIS setup remain pending.
