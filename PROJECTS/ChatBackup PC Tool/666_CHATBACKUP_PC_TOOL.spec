# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

project_dir = Path(SPECPATH)
app_dir = project_dir / "app"
tools_dir = project_dir / "tools"
assets_dir = project_dir / "assets"
icon_path = assets_dir / "chatbackup.ico"

runtime_assets = [
    (str(assets_dir / "header_banner.png"), "assets"),
    (str(assets_dir / "app_logo.png"), "assets"),
    (str(assets_dir / "app_icon_64.png"), "assets"),
    (str(assets_dir / "chatbackup.ico"), "assets"),
]

a = Analysis(
    [str(app_dir / "chatbackup_gui.pyw")],
    pathex=[str(app_dir), str(tools_dir)],
    binaries=[],
    datas=runtime_assets,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="666_CHATBACKUP_PC_TOOL",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_path) if icon_path.exists() else None,
)
