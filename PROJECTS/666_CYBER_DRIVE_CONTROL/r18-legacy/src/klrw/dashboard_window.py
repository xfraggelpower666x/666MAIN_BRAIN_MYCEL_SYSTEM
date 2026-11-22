"""Optional consolidated tkinter desktop widget. No hardware changes, no drivers."""
import argparse
from .overview import OverviewSampler, colored_meter
from .activity_window import formatted_bps


class DashboardWidget:
    def __init__(self, root, sampler=None, interval_ms=750):
        import tkinter as tk
        if not 250 <= interval_ms <= 60000: raise ValueError("interval must be 250..60000")
        self.root=root; self.sampler=sampler or OverviewSampler(); self.interval_ms=interval_ms
        self.running=True; self.job=None
        root.title("KLRW | System Dashboard R10"); root.configure(bg="#101320")
        self.labels={}
        frame=tk.Frame(root,bg="#101320",padx=18,pady=14);frame.pack(fill="both",expand=True)
        for key in ("CPU", "RAM", "Disk Read", "Disk Write", "Network RX", "Network TX"):
            lbl=tk.Label(frame,text=f"{key}: warming up",fg="#29d4c7",bg="#101320",font=("Consolas",11),anchor="w")
            lbl.pack(fill="x",pady=3);self.labels[key]=lbl
        self.status=tk.Label(frame,text="Sampling...",fg="#bfc3d4",bg="#101320");self.status.pack(anchor="w")
        tk.Button(frame,text="Exit",command=self.close).pack(anchor="e",pady=4)
        root.protocol("WM_DELETE_WINDOW",self.close)
        self.tick()

    def tick(self):
        if not self.running:return
        try:
            data=self.sampler.sample()
            for k,v in (("CPU",f"{data.cpu_pct:.1f}% {colored_meter(data.cpu_pct)}"),("RAM",f"{data.memory_pct:.1f}% {colored_meter(data.memory_pct)}"),
                        ("Disk Read",formatted_bps(data.disk_read_bps)),("Disk Write",formatted_bps(data.disk_write_bps)),
                        ("Network RX",formatted_bps(data.rx_bps)),("Network TX",formatted_bps(data.tx_bps))):
                self.labels[k].configure(text=f"{k}: {v}")
            self.status.configure(text=f"Selected disk: {data.disk} (baseline needed on first sample)")
        except Exception as exc:
            self.status.configure(text=f"Metrics unavailable: {type(exc).__name__}: {str(exc)[:80]}")
        if self.running:self.job=self.root.after(self.interval_ms,self.tick)

    def close(self):
        self.running=False
        if self.job is not None:self.root.after_cancel(self.job);self.job=None
        self.root.destroy()


def main(argv=None):
    p=argparse.ArgumentParser(description="KLRW read-only dashboard")
    p.add_argument("--interval-ms",type=int,default=750)
    args=p.parse_args(argv)
    if not 250 <= args.interval_ms <= 60000:p.error("interval must be 250..60000")
    import tkinter as tk
    root=tk.Tk();DashboardWidget(root,interval_ms=args.interval_ms);root.mainloop();return 0

if __name__=="__main__":raise SystemExit(main())
