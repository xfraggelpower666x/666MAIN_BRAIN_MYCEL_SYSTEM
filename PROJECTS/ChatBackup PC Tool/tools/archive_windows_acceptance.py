#!/usr/bin/env python3
"""Build and verify a source-portable Windows archive-intelligence host acceptance.

Does not modify the installed ChatBackup app. No credentials, network or GUI
display assertion. Generates explicit local evidence and SHA-256 inventory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    "app/archive_intelligence.py",
    "app/archive_extensions.py",
    "app/archive_streaming.py",
    "app/archive_research.py",
    "tools/archive_intelligence_cli.py",
    "tools/archive_intelligence_gui.py",
    "tools/archive_windows_acceptance.py",
)
START = r"""@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if not errorlevel 1 (
  py -3 "tools\archive_intelligence_gui.py"
) else (
  where python >nul 2>&1
  if errorlevel 1 (
    echo Python 3 required. Existing ChatBackup remains unchanged.
    pause
    exit /b 2
  )
  python "tools\archive_intelligence_gui.py"
)
if errorlevel 1 pause
"""
CHECK = r"""@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if not errorlevel 1 (
  py -3 "tools\archive_windows_acceptance.py" --verify --report "ARCHIVE_WINDOWS_HOST_REPORT.json"
) else (
  where python >nul 2>&1
  if errorlevel 1 (
    echo Python 3 required for the optional Archive Intelligence package.
    pause
    exit /b 2
  )
  python "tools\archive_windows_acceptance.py" --verify --report "ARCHIVE_WINDOWS_HOST_REPORT.json"
)
set "STATUS=%errorlevel%"
echo.
echo Result: ARCHIVE_WINDOWS_HOST_REPORT.json
pause
exit /b %STATUS%
"""
README = """# 666 ChatBackup Archive Intelligence R5.2 - Windows host acceptance

This ZIP is a standalone **editable source** package, not an installed executable.
The existing working ChatBackup v1.10.5 and Scriptable v1.0.9 are unchanged.

1. Extract the entire ZIP to a writable local folder.
2. Double-click VERIFY_ARCHIVE_WINDOWS.cmd to run the local offline smoke test.
3. Inspect ARCHIVE_WINDOWS_HOST_REPORT.json. Status PASS means CLI/import/catalog/
   progress/cancel tests passed; it does NOT certify the visible Tk window.
4. Double-click START_ARCHIVE_INTELLIGENCE.cmd to test the actual GUI visually.
5. Official ChatGPT data exports are user-provided, optional and never uploaded.
6. The batch importer supports cancellation/progress/rollback. The standalone
   single-archive import remains bounded but is not streamed.
7. For integration with an existing frozen ChatBackup EXE, packaging and the
   add-on sidecar directory must be tested separately. This source ZIP does
   not replace or silently patch any installed EXE.

No cloud requests, cookies, access tokens or runtime installation performed.
Python 3.12+ with bundled Tkinter is expected for GUI use.
"""

def digest(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()

def build_package(destination: Path) -> dict:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(f"Refusing overwrite: {destination}")
    files: dict[str, bytes] = {}
    for name in SOURCES:
        file = ROOT / name
        if not file.is_file():
            raise FileNotFoundError(name)
        files[name] = file.read_bytes()
    files["START_ARCHIVE_INTELLIGENCE.cmd"] = START.replace("\n", "\r\n").encode("utf-8")
    files["VERIFY_ARCHIVE_WINDOWS.cmd"] = CHECK.replace("\n", "\r\n").encode("utf-8")
    files["README_WINDOWS_ABNAHME.md"] = README.encode("utf-8")
    inventory = "".join(f"{digest(files[p])} *{p}\n" for p in sorted(files))
    files["PACKAGE_SHA256SUMS.txt"] = inventory.encode("utf-8")
    folder = "666_CHATBACKUP_ARCHIVE_R52_WINDOWS/"
    with zipfile.ZipFile(destination, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(files):
            archive.writestr(folder + name, files[name])
    with zipfile.ZipFile(destination) as zf:
        for name, expected in ((n, digest(blob)) for n, blob in files.items()):
            assert digest(zf.read(folder + name)) == expected, name
    return {"package": destination.name, "sha256": digest(destination.read_bytes()),
            "files": len(files), "source_archive_readback": "PASS"}

def verify(report_path: Path) -> int:
    outcomes: list[dict[str, str]] = []
    def record(name: str, fn) -> None:
        try:
            fn()
            outcomes.append({"check": name, "status": "PASS"})
        except Exception as exc:
            outcomes.append({"check": name, "status": "FAIL",
                             "error_type": type(exc).__name__,
                             "detail": str(exc)[:180]})

    def import_modules():
        sys.path.insert(0, str(ROOT / "app"))
        import archive_intelligence
        import archive_extensions
        import archive_streaming
        import archive_research
        assert archive_intelligence.MAX_MEMBER_BYTES > 0
        assert callable(archive_streaming.iter_export_conversations)
    record("IMPORT_ALL_LOCAL_MODULES", import_modules)

    def tkinter_runtime():
        import tkinter as tk
        from tkinter import ttk
        assert callable(tk.Tk) and callable(ttk.Progressbar)
        # Tk window visible/interactive check is intentionally not claimed here.
    record("TKINTER_IMPORT_ONLY", tkinter_runtime)

    def smoke():
        from archive_intelligence import ArchiveCatalog
        from archive_extensions import import_directory, search_fts, conversation_view
        with tempfile.TemporaryDirectory(prefix="666chatbackup_accept_") as tmp:
            tmp = Path(tmp)
            source = tmp / "sources"
            source.mkdir()
            path = source / "official-format-fixture.zip"
            chats = []
            for n in range(45):
                chats.append({"id": f"accept-{n}", "title": "Offline archive verification",
                              "mapping": {"a": {"parent": None, "children": [],
                              "message": {"id": f"message-{n}",
                              "author": {"role": "user"},
                              "content": {"content_type": "text",
                              "parts": ["Dark Techno QA " + str(n)]}}}}})
            with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("conversations.json", json.dumps(chats))
            before = digest(path.read_bytes())
            db = tmp / "catalog.sqlite3"
            checkpoint = tmp / "checkpoint.json"
            events = []
            result = import_directory(source, db, checkpoint, progress=events.append)
            assert result["status"] == "PASS", result
            assert result["imported"] == 1 and result["search_index"]["count"] == 45, result
            assert any(e.get("stage") == "STREAMING" for e in events)
            with ArchiveCatalog(db) as catalog:
                assert catalog.status()["conversations"] == 45
                assert len(search_fts(catalog, "Dark Techno")) == 45
                assert conversation_view(catalog, "accept-4")["messages"][0]["role"] == "user"
            assert import_directory(source, db, checkpoint)["unchanged_files"] == 1
            assert digest(path.read_bytes()) == before
    record("ZIP_STREAM_FTS_VIEW_CHECKPOINT_SOURCE_UNCHANGED", smoke)

    def cancel():
        from archive_intelligence import ArchiveCatalog
        from archive_extensions import import_directory
        with tempfile.TemporaryDirectory(prefix="666chatbackup_cancel_") as tmp:
            tmp = Path(tmp)
            directory = tmp / "source"
            directory.mkdir()
            payload = [{"id": f"cancel-{i}", "mapping": {
                "a": {"parent": None, "children": [], "message": {
                    "id": f"message-{i}", "author": {"role": "user"},
                    "content": {"content_type": "text", "parts": ["test" * 1000]}}}}}
                for i in range(60)]
            with zipfile.ZipFile(directory / "source.zip", "w") as archive:
                archive.writestr("conversations.json", json.dumps(payload))
            state = {"cancel": False}
            def progress(event):
                if event.get("stage") == "STREAMING":
                    state["cancel"] = True
            db = tmp / "db.sqlite3"
            checkpoint = tmp / "checkpoint.json"
            result = import_directory(directory, db, checkpoint,
                                      stop=lambda: state["cancel"], progress=progress)
            assert result["stopped"] and not checkpoint.exists(), result
            with ArchiveCatalog(db) as catalog:
                assert catalog.status()["messages"] == 0
            resumed = import_directory(directory, db, checkpoint)
            assert resumed["imported"] == 1 and resumed["status"] == "PASS"
    record("CANCEL_ROLLBACK_AND_RESUME", cancel)

    report = {"schema": "666.chatbackup.r52.windows-host-acceptance.v1",
              "status": "PASS" if all(x["status"] == "PASS" for x in outcomes) else "FAIL",
              "python": platform.python_version(), "os": platform.system(),
              "gui_visible": "NOT_TESTED", "real_user_export": "NOT_TESTED",
              "installed_main_app": "NOT_MODIFIED",
              "checks": outcomes}
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1

def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--build", type=Path)
    cli.add_argument("--verify", action="store_true")
    cli.add_argument("--report", type=Path, default=Path("ARCHIVE_WINDOWS_HOST_REPORT.json"))
    args = cli.parse_args()
    if args.build:
        print(json.dumps(build_package(args.build), indent=2))
        return 0
    if args.verify:
        return verify(args.report)
    cli.error("Use --build PACKAGE.zip or --verify")
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
