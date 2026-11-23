"""R19-only persistent visual drive mappings and native R18 bicolor pulse adapter.

No keyboard/HID commands. The R18 workspace schema is never changed.
"""
from __future__ import annotations
import json
import os
import tempfile
from pathlib import Path
from klrw.bicolor_activity import BicolorActivity
from klrw.drive_led_mapping import DriveBinding, LEDS, MODES, evaluate
from klrw.ssd import DiskRates

class VisualBindings:
    """R19-independent mapping config next to the R18 Workspace data file."""
    def __init__(self, workspace_path):
        self.path = Path(workspace_path).with_name("r19_visual_bindings.json")
        self.bindings = {led: {"device": "_total", "mode": "off", "threshold_kib": 4.0} for led in LEDS}
        self.load()

    @staticmethod
    def _check(led, device, mode, threshold):
        import math
        if led not in LEDS or mode not in MODES or not isinstance(device, str) or not device or len(device) > 256:
            raise ValueError("Invalid visual LED mapping")
        if isinstance(threshold, bool) or not isinstance(threshold, (float, int)):
            raise ValueError("Invalid mapping threshold")
        if not math.isfinite(threshold) or not 0 <= threshold <= 1048576:
            raise ValueError("Mapping threshold out of bounds")
        binding = DriveBinding(led=led, drive=device, mode=mode, threshold_kib=float(threshold))
        binding.validate()
        return {"device": device, "mode": mode, "threshold_kib": float(threshold)}

    def load(self):
        if not self.path.is_file():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or data.get("schema") != 1 or not isinstance(data.get("bindings"), dict):
                return
            proposed = {}
            for led in LEDS:
                entry = data["bindings"].get(led)
                if not isinstance(entry, dict):
                    return
                proposed[led] = self._check(led, entry.get("device"), entry.get("mode"), entry.get("threshold_kib"))
            self.bindings = proposed
        except (OSError, ValueError, TypeError, UnicodeError):
            # Preserve unreadable originals untouched and use safe defaults.
            return

    def set_binding(self, led, device, mode, threshold, available):
        if not isinstance(available, (set, frozenset)) or device not in available:
            raise ValueError("Physical device currently unavailable")
        candidate = self._check(led, device, mode, threshold)
        previous = self.bindings.get(led)
        self.bindings[led] = candidate
        try:
            self.save()
        except Exception:
            self.bindings[led] = previous
            raise

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".r19_visual_", suffix=".json", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump({"schema": 1, "bindings": self.bindings}, handle, indent=2, ensure_ascii=False)
            os.replace(tmp, self.path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

    def preview(self, rates):
        bindings = [DriveBinding(led, data["device"], data["mode"], data["threshold_kib"])
                    for led, data in self.bindings.items()]
        known = {key: DiskRates(key, float(value[0]), float(value[1]))
                 for key, value in rates.items() if value is not None}
        return evaluate(bindings, known)

class VolumePulseMonitor:
    """R18 BicolorActivity baseline, hold and quiet; no hardware effects."""
    def __init__(self):
        self.engine = BicolorActivity()

    def sample(self, volumes, now_ms, settings):
        self.engine.forget_missing({v["id"] for v in volumes})
        result = {}
        for v in volumes:
            read, write = v["read_bps"], v["write_bps"]
            rate = DiskRates(v["id"], read, write) if isinstance(read, (int, float)) and isinstance(write, (int, float)) else None
            result[v["id"]] = self.engine.sample(v["id"], rate, now_ms,
                threshold_bps=settings["activity_threshold_bps"],
                burst_bps=settings.get("burst_bps", 16384),
                hold_ms=settings["led_hold_ms"], quiet_ms=settings["led_quiet_ms"])
        return result
