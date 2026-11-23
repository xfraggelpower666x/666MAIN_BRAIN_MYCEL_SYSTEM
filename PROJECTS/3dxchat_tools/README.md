# 3DXChat Tools

Six editable Python CLI tools for 3DXChat World Editor, migrated from the user-supplied `3dxchat_tools-master.zip`.

## Installation

```sh
python -m pip install -r requirements.txt
```

## Tools

| Script | Purpose |
| --- | --- |
| `gentext.py` | 3DXChat world text, Soda/Outline fonts |
| `getcolors.py` | Find nearby object colors |
| `getmaterials.py` | Find nearby object materials |
| `moveworld.py` | Translate world and respawn positions |
| `pic23dxchat.py` | Convert RGB image pixels to world boxes |
| `qr2world.py` | Convert QR module grid to world boxes |

Examples:

```sh
python moveworld.py -x 10 -o moved.world original.world
python qr2world.py -o code.world "https://3dxchat.com"
python pic23dxchat.py -r 4 -o picture.world picture.png
python gentext.py -f soda -o words.world "HELLO"
```

## Current verified scope

The six Python scripts, this README and requirements.txt are published individually as editable source. The original four assets are **not yet committed**. Therefore `gentext.py` cannot run with a self-contained checkout until its font assets are present. See `ORIGINAL_ASSETS_PENDING.md`.

Source changes are intentionally small: Pillow resampling compatibility and positive parameter validation for image conversion, direct QR matrix generation instead of shared SVG temp files, and font lookup relative to script directory. Other scripts preserve original logic.

Local verification: Python compilation succeeded for the four restored scripts. The three original `.world` JSON assets parse successfully from the uploaded ZIP. Full Windows/3DXChat runtime acceptance remains OPEN.

Integration governance: LYVRA Coding Profi coordinates engineering; 666MAIN_BRAIN repository remains storage authority for this project. No cross-system activation or unrelated project modifications.
