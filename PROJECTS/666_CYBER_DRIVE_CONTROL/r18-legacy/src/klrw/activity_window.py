"""Safe Windows desktop activity widget. Read-only and portable; no drivers/lock toggles.

Launch `python -m klrw.activity_window`. Tk mainloop is started only by main().
"""
from __future__ import annotations
import argparse
import sys
from .activity_presenter import activity_visual
from .ssd import DiskActivitySampler


def formatted_bps(n):
    if n < 0: raise ValueError("negative throughput")
    if n >= 1048576: return f"{n/1048576:.1f} MiB/s"
    return f"{n/1024:.1f} KiB/s"


class DesktopActivityWidget:
    def __init__(self, root, sampler=None, device="_total", interval_ms=500, saturation_kib=1024):
        import tkinter as tk
        if not 200 <= interval_ms <= 60000: raise ValueError("interval must be 200..60000 ms")
        if saturation_kib <= 0: raise ValueError("saturation must be positive")
        self.root = root
        self.sampler = sampler or DiskActivitySampler()
        self.device = device
        self.interval_ms = interval_ms
        self.saturation_kib = saturation_kib
        self.running = True
        self.after_id = None
        root.title("KLRW Disk Activity | R9")
        root.configure(bg="#111827")
        frame = tk.Frame(root, bg="#111827", padx=12, pady=10)
        frame.pack(fill="both", expand=True)
        self.status = tk.Label(frame, text="Sampling …", fg="#f4f4f4", bg="#111827", font=("Segoe UI", 12))
        self.status.pack(anchor="w")
        self.info = tk.Label(frame, text="First sample establishes baseline", fg="#9ca3af", bg="#111827")
        self.info.pack(anchor="w")
        self.led = tk.Label(frame, text="●", fg="#000000", bg="#111827", font=("Segoe UI", 30))
        self.led.pack(side="left")
        tk.Button(frame, text="Close", command=self.close).pack(side="right")
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.tick()

    def tick(self):
        if not self.running: return
        try:
            rates = self.sampler.sample(self.device)
            visual = activity_visual(rates.read_bps, rates.write_bps, self.saturation_kib)
            self.status.configure(text=f"Disk {self.device} · {visual.status}")
            self.info.configure(text=f"Read {formatted_bps(rates.read_bps)} · Write {formatted_bps(rates.write_bps)}")
            self.led.configure(fg=visual.hex_color)
        except Exception as exc:
            self.status.configure(text="Disk monitoring unavailable")
            self.info.configure(text=f"{type(exc).__name__}: {str(exc)[:120]}")
            self.led.configure(fg="#555555")
        if self.running:
            self.after_id = self.root.after(self.interval_ms, self.tick)

    def close(self):
        self.running = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.root.destroy()


def main(argv=None):
    parser = argparse.ArgumentParser(description="KLRW safe read-only Windows disk activity widget")
    parser.add_argument("--disk", default="_total")
    parser.add_argument("--interval-ms", type=int, default=500)
    parser.add_argument("--saturation-kib", type=float, default=1024)
    args = parser.parse_args(argv)
    if not 200 <= args.interval_ms <= 60000 or not 0 < args.saturation_kib <= 100000000:
        parser.error("invalid interval or saturation")
    import tkinter as tk
    root = tk.Tk()
    DesktopActivityWidget(root, device=args.disk, interval_ms=args.interval_ms, saturation_kib=args.saturation_kib)
    root.mainloop()
    return 0

if __name__ == "__main__":
    sys.exit(main())
