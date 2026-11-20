from __future__ import annotations

import json
import os
import platform
import runpy
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app"
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

# Prevent the GUI module from redirecting this already-governed probe back through bootstrap.
os.environ["CHATBACKUP_BOOTSTRAP_STATUS"] = "PASS"

report: dict[str, object] = {
    "status": "WINDOWS_RUNTIME_READBACK_PENDING",
    "tool": "666 ChatBackup PC Tool",
    "expectedVersion": "1.10.5",
    "executedAtUtc": datetime.now(timezone.utc).isoformat(),
    "platform": platform.platform(),
    "system": platform.system(),
    "python": sys.version,
    "pythonExecutable": sys.executable,
    "guiEntry": "app/chatbackup_gui.pyw",
    "checks": [],
}
checks: list[dict[str, object]] = report["checks"]  # type: ignore[assignment]


def add(name: str, ok: bool, detail: object = "") -> None:
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "detail": str(detail)})

try:
    from chatbackup_core import APP_VERSION
    add("CORE_IMPORT", True, APP_VERSION)
    add("VERSION_MATCH", APP_VERSION == "1.10.5", APP_VERSION)
except Exception as exc:
    add("CORE_IMPORT", False, repr(exc))

try:
    from chatbackup_backend import ChatBackend, BackendConfig  # noqa: F401
    add("BACKEND_IMPORT", True, "ChatBackend/BackendConfig")
except Exception as exc:
    add("BACKEND_IMPORT", False, repr(exc))

try:
    import tkinter as tk
    add("TKINTER_IMPORT", True, getattr(tk, "TkVersion", "unknown"))
except Exception as exc:
    tk = None  # type: ignore[assignment]
    add("TKINTER_IMPORT", False, repr(exc))

try:
    from PIL import Image  # noqa: F401
    import PIL
    add("PILLOW_IMPORT", True, getattr(PIL, "__version__", "unknown"))
except Exception as exc:
    add("PILLOW_IMPORT", False, repr(exc))

app = None
if tk is not None:
    try:
        entry = runpy.run_path(str(APP / "chatbackup_gui.pyw"))
        app = entry["ChatBackupApp"]()
        add("GUI_MODULE_IMPORT", True, report["guiEntry"])
        app.update_idletasks()
        app.update()
        title = app.title()
        geometry = app.geometry()
        report["guiTitle"] = title
        report["guiGeometry"] = geometry
        add("GUI_INSTANTIATION", True, title)
        add("GUI_TITLE_VERSION", "v1.10.5" in title, title)
        add("GUI_GEOMETRY_READBACK", bool(geometry and "x" in geometry), geometry)

        # Echten Dialog der ausgelieferten GUI pruefen, ohne Browser oder Zwischenablage zu oeffnen.
        from chatbackup_core import AuthWallDetected
        before = set(app.winfo_children())
        app.open_browser_assisted_capture(auth_error=AuthWallDetected(
            "Host-Pruefung", source_url="https://chatgpt.com/share/fixture",
            evidence={"htmlChars": 500},
        ))
        app.update_idletasks()
        dialogs = [
            child for child in app.winfo_children()
            if child not in before and isinstance(child, tk.Toplevel)
        ]
        expected_title = app._bi("Browser-Assisted Recovery", "Browser-gestützte Wiederherstellung")
        add("GUI_BROWSER_RECOVERY_DIALOG", any(expected_title in dialog.title() for dialog in dialogs),
            ", ".join(dialog.title() for dialog in dialogs))
        for dialog in dialogs:
            dialog.destroy()
    except Exception as exc:
        add("GUI_INSTANTIATION", False, repr(exc))
    finally:
        if app is not None:
            try:
                app.destroy()
            except Exception:
                pass

# This probe may be syntax-tested on non-Windows hosts, but only Windows can close the Windows gate.
is_windows = platform.system().lower() == "windows"
report["isWindowsHost"] = is_windows
failed = [c for c in checks if c["status"] != "PASS"]
if is_windows and not failed:
    report["status"] = "WINDOWS_RUNTIME_READBACK_PASS"
elif failed:
    report["status"] = "WINDOWS_RUNTIME_READBACK_FAIL"
else:
    report["status"] = "NON_WINDOWS_PROBE_PASS_HOST_GATE_NOT_CLOSED"

out_dir = ROOT / "runtime_readback"
out_dir.mkdir(exist_ok=True)
out = out_dir / "windows_runtime_readback.json"
out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
print(f"REPORT={out}")

if failed:
    raise SystemExit(2)
if not is_windows:
    raise SystemExit(3)
