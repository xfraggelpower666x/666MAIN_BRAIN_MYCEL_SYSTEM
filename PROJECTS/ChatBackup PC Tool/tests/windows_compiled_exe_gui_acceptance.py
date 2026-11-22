"""Black-box Windows GUI acceptance for the *compiled original* ChatBackup EXE.

Starts and operates the built application through Windows UI Automation.
No test hooks, no import of Python app code, and no real chat/ZIP data.
A separately tested source-level Tk probe is not accepted as proof here.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path


def main() -> int:
    if os.name != "nt":
        raise SystemExit("Windows runner required")
    from pywinauto import Desktop
    from PIL import ImageGrab

    project = Path(__file__).resolve().parents[1]
    exe = project / "dist" / "666_CHATBACKUP_PC_TOOL.exe"
    destination = project / "runtime_readback" / "WINDOWS_COMPILED_EXE_GUI_PROBE.json"
    screenshot_dir = project / "runtime_readback" / "gui_screenshots"
    destination.parent.mkdir(parents=True, exist_ok=True)
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    receipt = {
        "schema": "666.chatbackup.windows-compiled-gui.v1",
        "exe": exe.name,
        "mode": "EXTERNAL_UI_AUTOMATION",
        "source_gui_test": False,
        "source_data": "NO_USER_DATA",
        "tests": {},
        "windows": [],
        "status": "PARTIAL",
    }
    process = None
    try:
        if not exe.is_file():
            raise AssertionError("Compiled original EXE missing")
        process = subprocess.Popen([str(exe)], cwd=str(exe.parent))
        desk = Desktop(backend="uia")
        mainwin = None
        deadline = time.monotonic() + 22
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise AssertionError(f"EXE exited early: {process.returncode}")
            matches = [win for win in desk.windows()
                       if "666 ChatBackup PC Tool v" in win.window_text()
                       and win.process_id() == process.pid]
            if matches:
                mainwin = matches[0]
                break
            time.sleep(.4)
        if mainwin is None:
            raise AssertionError("Original EXE main window not exposed")
        mainwin.set_focus()
        receipt["windows"].append(mainwin.window_text())
        receipt["tests"]["compiled_main_window"] = "PASS"
        ImageGrab.grab().save(screenshot_dir / "compiled_main.png")
        controls = mainwin.descendants()
        names = [(getattr(control.element_info, "name", "") or "").strip() for control in controls]
        receipt["uia_main_controls"] = names[:150]
        matches = [control for control in controls
                   if "Archive Intelligence" in (getattr(control.element_info, "name", "") or "")]
        if not matches:
            raise AssertionError("Archive Intelligence control not exposed through Windows UIA")
        matches[0].click_input()
        receipt["tests"]["compiled_archive_control_clicked"] = "PASS"
        archive = None
        deadline = time.monotonic() + 18
        while time.monotonic() < deadline:
            matches = [win for win in desk.windows()
                       if "Archive Intelligence" in win.window_text()
                       and win.process_id() == process.pid]
            if matches:
                archive = matches[0]
                break
            time.sleep(.35)
        if archive is None:
            raise AssertionError("Compiled EXE did not open integrated Archive window")
        archive.set_focus()
        receipt["windows"].append(archive.window_text())
        receipt["tests"]["compiled_archive_window"] = "PASS"
        ImageGrab.grab().save(screenshot_dir / "compiled_archive.png")
        archive_controls = archive.descendants()
        archive_names = [(getattr(control.element_info, "name", "") or "").strip()
                         for control in archive_controls]
        receipt["uia_archive_controls"] = archive_names[:150]
        if not any("View conversation" in name for name in archive_names):
            raise AssertionError("Archive conversation control missing in compiled EXE")
        if not any("Search" in name for name in archive_names):
            raise AssertionError("Archive search control missing in compiled EXE")
        receipt["tests"]["compiled_archive_actions"] = "PASS"
        receipt["status"] = "COMPILED_EXE_GUI_AUTOMATION_PASS"
        print(receipt["status"])
        return 0
    except Exception as exc:
        receipt["error_type"] = type(exc).__name__
        receipt["error"] = str(exc)[:700]
        receipt["traceback"] = traceback.format_exc(limit=5)[-1500:]
        receipt["status"] = "COMPILED_EXE_GUI_AUTOMATION_FAIL"
        print(receipt["status"], str(exc), file=sys.stderr)
        return 1
    finally:
        if process is not None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        destination.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
