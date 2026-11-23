# 3DXChat Tools

Six standalone Python command-line tools and four original data assets from creator-provided `3dxchat_tools-master.zip`. The source is stored as individually editable files rather than a ZIP.

## Setup

```sh
python -m pip install -r requirements.txt
```

## Tools

- `gentext.py`: generate 3DXChat `.world` text with `soda` or `outline` font assets
- `getcolors.py`: report colors of nearby world objects
- `getmaterials.py`: report materials of nearby world objects
- `moveworld.py`: translate 3DXChat world positions and respawn point
- `pic23dxchat.py`: convert image pixels to colored boxes in a world
- `qr2world.py`: convert a QR code into a world of boxes

Examples:

```sh
python gentext.py -f soda -o label.world "HELLO"
python moveworld.py -x 10 -o moved.world label.world
python pic23dxchat.py -r 4 -o picture.world hcuffs.png
python qr2world.py -o qr.world "https://3dxchat.com"
```

## Source and repairs

- All original four data assets are byte-for-byte exact relative to the supplied archive. See `ORIGINAL_ASSETS_PENDING.md` (resolved transfer receipt).
- Initial source changes are narrow: Pillow resize compatibility and scale validation, in-memory QR modules avoiding the fixed temporary SVG file, and font path handling relative to the script.
- The original filenames, world JSON format, and project boundaries are preserved.
- Local Python syntax checks passed for restored scripts. Local source tests passed for Soda and Outline text generation (5 groups each), world translation, color and material inspection. Separate real 3DXChat Windows GUI acceptance remains OPEN.

Coordination: LYVRA Coding Profi. The project belongs to this repository's PROJECTS area; native authorities of connected engineering plugins remain independent.
