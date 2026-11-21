# -*- mode: python ; coding: utf-8 -*-
"""Optional Archive Intelligence companion, preserving the original main EXE spec."""
from pathlib import Path

project_dir = Path(SPECPATH)
app_dir = project_dir / "app"
tools_dir = project_dir / "tools"
icon_path = project_dir / "assets" / "chatbackup.ico"

a = Analysis(
    [str(tools_dir / "archive_intelligence_gui.py")],
    pathex=[str(app_dir), str(tools_dir)],
    binaries=[],
    datas=[],
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
    pyz, a.scripts, a.binaries, a.datas, [],
    name="666_CHATBACKUP_ARCHIVE_INTELLIGENCE",
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
