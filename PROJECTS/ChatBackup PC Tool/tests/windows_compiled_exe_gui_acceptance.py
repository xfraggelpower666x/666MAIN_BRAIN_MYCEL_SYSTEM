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
    import psutil
    import win32gui
    import win32process
    import pyautogui

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
        deadline = time.monotonic() + 45
        # PyInstaller OneFile may retain a parent bootloader while running the
        # real Tk process as a child. Never equate only the initial PID with
        # every window owned by the compiled executable.
        tracked = {process.pid}
        def list_windows():
            found = []
            def collect(hwnd, _):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    found.append({"title": title[:180], "pid": pid,
                                  "visible": bool(win32gui.IsWindowVisible(hwnd)),
                                  "hwnd": hwnd})
            win32gui.EnumWindows(collect, None)
            return found

        while time.monotonic() < deadline:
            try:
                tree = psutil.Process(process.pid)
                tracked.update(child.pid for child in tree.children(recursive=True))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            window_rows = list_windows()
            candidates = [row for row in window_rows
                          if "666 ChatBackup PC Tool v" in row["title"]
                          and row["pid"] in tracked]
            if candidates:
                for row in candidates:
                    try:
                        mainwin = desk.window(handle=row["hwnd"])
                        mainwin.window_text()
                        break
                    except Exception:
                        mainwin = None
                if mainwin is not None:
                    receipt["main_window_pid"] = candidates[0]["pid"]
                    break
            if process.poll() is not None and not any(psutil.pid_exists(pid) for pid in tracked):
                break
            time.sleep(.5)
        receipt["tracked_pids"] = sorted(tracked)
        receipt["windows_discovered"] = [
            {"title": row["title"], "pid": row["pid"], "visible": row["visible"]}
            for row in list_windows() if row["pid"] in tracked or "ChatBackup" in row["title"]
        ][:100]
        if mainwin is None:
            ImageGrab.grab().save(screenshot_dir / "compiled_window_not_found.png")
            raise AssertionError("No original EXE Tk top-level window from tracked PyInstaller process tree")
        mainwin.set_focus()
        receipt["windows"].append(mainwin.window_text())
        receipt["tests"]["compiled_main_window"] = "PASS"
        ImageGrab.grab().save(screenshot_dir / "compiled_main.png")
        controls = mainwin.descendants()
        names = [(getattr(control.element_info, "name", "") or "").strip() for control in controls]
        receipt["uia_main_controls"] = names[:150]
        matches = [control for control in controls
                   if "Archive Intelligence" in (getattr(control.element_info, "name", "") or "")]
        if matches:
            matches[0].click_input()
            receipt["archive_click_method"] = "WINDOWS_UIA"
        else:
            # Windows Tk 8.6 zeichnet seine Buttons selbst; UIA kann deshalb
            # keine beschrifteten Button-Knoten liefern. Der Screenshot des
            # verifizierten Originalfensters zeigt den dritten linken
            # Navigationsknopf (Archive Intelligence). Die CI-Auflösung und
            # das Fensterlayout werden vor einem realen Mausklick geprüft.
            bounds = mainwin.rectangle()
            viewport_w, viewport_h = pyautogui.size()
            if not (bounds.width() >= 950 and bounds.height() >= 650):
                raise AssertionError("Unexpected original main-window geometry")
            click_x = bounds.left + 130
            click_y = bounds.top + 636
            if not (0 <= click_x < viewport_w and 0 <= click_y < viewport_h):
                raise AssertionError("Archive button outside visible CI desktop")
            receipt["archive_click_method"] = "PHYSICAL_MOUSE_POSITION_VERIFIED_LAYOUT"
            receipt["archive_click_xy"] = [click_x, click_y]
            pyautogui.click(click_x, click_y)
        receipt["tests"]["compiled_archive_control_clicked"] = "PASS"
        archive = None
        deadline = time.monotonic() + 18
        while time.monotonic() < deadline:
            rows = [row for row in list_windows()
                    if "Archive Intelligence" in row["title"] and row["pid"] in tracked]
            if rows:
                try:
                    archive = desk.window(handle=rows[0]["hwnd"])
                    archive.window_text()
                    break
                except Exception:
                    archive = None
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
        # Tk buttons are drawn without accessible UIA names. For the
        # real compiled binary, click actual controls in its verified window
        # geometry and require their distinct native Windows modal dialogs.
        archive_rect = archive.rectangle()
        if not (archive_rect.width() >= 950 and archive_rect.height() >= 650):
            raise AssertionError("Unexpected compiled Archive window geometry")

        def click_archive(relative_x, relative_y, label):
            x = archive_rect.left + relative_x
            y = archive_rect.top + relative_y
            screen_w, screen_h = pyautogui.size()
            if not (0 <= x < screen_w and 0 <= y < screen_h):
                raise AssertionError(f"{label} outside the visible Windows desktop")
            pyautogui.click(x, y)
            receipt.setdefault("physical_archive_clicks", []).append(
                {"control": label, "xy": [x, y]})

        def require_modal(expected, timeout=8):
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                rows = [row for row in list_windows()
                        if expected in row["title"] and row["pid"] in tracked
                        and row["visible"]]
                if rows:
                    return rows[0]
                time.sleep(.25)
            raise AssertionError(f"Compiled EXE modal {expected!r} was not opened")

        click_archive(328, 138, "Catalog status")
        dialog = require_modal("Local catalog")
        receipt["tests"]["compiled_catalog_status_dialog"] = "PASS"
        ImageGrab.grab().save(screenshot_dir / "compiled_catalog_dialog.png")
        pyautogui.press("enter")
        time.sleep(.4)
        if win32gui.IsWindow(dialog["hwnd"]):
            raise AssertionError("Catalog status dialog did not close")

        archive.set_focus()
        click_archive(647, 138, "View conversation")
        dialog = require_modal("Conversation viewer")
        receipt["tests"]["compiled_conversation_viewer_dialog"] = "PASS"
        ImageGrab.grab().save(screenshot_dir / "compiled_conversation_prompt.png")
        pyautogui.press("esc")
        time.sleep(.4)
        if win32gui.IsWindow(dialog["hwnd"]):
            raise AssertionError("Conversation prompt did not close")

        archive.set_focus()
        click_archive(450, 214, "Search term entry")
        pyautogui.write("r55-compiled-fixture-absent", interval=.01)
        click_archive(985, 214, "Search")
        time.sleep(1)
        if process.poll() is not None:
            raise AssertionError("Compiled EXE exited while searching the catalog")
        receipt["tests"]["compiled_empty_catalog_search_no_crash"] = "PASS"
        ImageGrab.grab().save(screenshot_dir / "compiled_search.png")
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
