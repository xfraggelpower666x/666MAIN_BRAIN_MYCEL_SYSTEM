"""Simple Tkinter UI, with explicit consent for real lock-key state changes."""
import queue
import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import replace
from .model import Config
from .runtime import Monitor
from .ssd import DiskActivitySampler, IndicatorSettings, indicator_hex
from .lock_indicator import LockIndicator, WindowsLockReader, PreviewLockReader, display_text
from . import hardware_lease

class App:
    def __init__(self, root, host=None):
        self.root = root
        self.host = host if host is not None else root
        self.embedded = host is not None
        if not self.embedded:
            root.title("Keyboard LED Remapper Windows · v1.3 · SSD + Lock Indicator")
            root.geometry("720x540")
        root.configure(bg="#141521")
        self.queue = queue.Queue()
        self.monitor = None
        self.hardware = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value="Bereit · Simulation")
        self.disk_device = tk.StringVar(value="_total")
        self.saturation = tk.StringVar(value="1024")
        head = tk.Label(self.host, text="KEYBOARD LED REMAPPER", font=("Segoe UI", 19, "bold"),
                        bg="#141521", fg="#4de9e8")
        head.pack(padx=20, pady=(24, 12), anchor="w")
        tk.Label(self.host, text="CPU / RAM / Disk / Network → Caps / Num / Scroll",
                 bg="#141521", fg="white").pack(anchor="w", padx=22)
        tk.Checkbutton(self.host, text="Echte Lock-Tasten umschalten (kann Tippen beeinflussen)",
                       variable=self.hardware, bg="#141521", fg="#ffb0d7",
                       selectcolor="#24263b", activebackground="#141521",
                       activeforeground="#ffb0d7").pack(anchor="w", padx=20, pady=15)
        disk_row = ttk.Frame(self.host)
        disk_row.pack(anchor="w", padx=20, pady=(0, 8), fill="x")
        ttk.Label(disk_row, text="SSD-Laufwerk:").pack(side="left")
        try:
            choices = DiskActivitySampler().devices()
        except (OSError, RuntimeError):
            choices = ("_total",)
        ttk.Combobox(disk_row, textvariable=self.disk_device, values=choices,
                     state="readonly", width=22).pack(side="left", padx=8)
        ttk.Label(disk_row, text="Vollausschlag KiB/s:").pack(side="left")
        ttk.Entry(disk_row, textvariable=self.saturation, width=9).pack(side="left", padx=8)
        self.ssd_visual = tk.Label(self.host, text="SSD · ◉    Lesen: 0 KiB/s    Schreiben: 0 KiB/s",
            font=("Segoe UI", 11, "bold"), bg="#20232e", fg="#eeeeee", anchor="w", padx=12, pady=9)
        self.ssd_visual.pack(fill="x", padx=20, pady=(0, 10))
        # R4: Virtual indicators are read-only. No hardware lock state changes.
        self.lock_order = tk.StringVar(value="NCS")
        self.lock_status = tk.StringVar(value="N ○   C ○   S ○")
        self.lock_reader_error = None
        try:
            reader = WindowsLockReader()
        except OSError as exc:
            reader = PreviewLockReader()
            self.lock_reader_error = str(exc)
        self.lock_indicator = LockIndicator(reader, self.lock_order.get())
        indicator_bar = ttk.Frame(self.host)
        indicator_bar.pack(fill="x", padx=20, pady=(0, 10))
        ttk.Label(indicator_bar, text="Lock-Status (N/C/S):").pack(side="left")
        ttk.Label(indicator_bar, textvariable=self.lock_status).pack(side="left", padx=10)
        ttk.Label(indicator_bar, text="Anordnung:").pack(side="left", padx=(12, 4))
        ttk.Entry(indicator_bar, textvariable=self.lock_order, width=5).pack(side="left")
        ttk.Button(indicator_bar, text="Übernehmen", command=self.update_lock_order).pack(side="left", padx=5)
        if self.lock_reader_error:
            self.lock_status.set("Vorschau · keine Windows-Hardware")
        self.refresh_lock_indicator()
        buttons = ttk.Frame(self.host)
        buttons.pack(anchor="w", padx=20)
        self.start_button = ttk.Button(buttons, text="Überwachung starten", command=self.start)
        self.start_button.pack(side="left", padx=(0, 10))
        self.stop_button = ttk.Button(buttons, text="Stoppen", command=self.stop, state="disabled")
        self.stop_button.pack(side="left")
        self.output = tk.Text(self.host, bg="#1d2131", fg="#c0fff5", insertbackground="white",
                              font=("Consolas", 10), height=9, relief="flat")
        self.output.pack(fill="both", expand=True, padx=20, pady=15)
        tk.Label(self.host, textvariable=self.status, bg="#141521", fg="#d7a3ff").pack(anchor="w", padx=20, pady=(0, 16))
        if not self.embedded:
            root.protocol("WM_DELETE_WINDOW", self.quit)
        root.after(100, self.drain)

    def update_lock_order(self):
        try:
            self.lock_indicator.set_order(self.lock_order.get().upper())
            self.lock_order.set(self.lock_order.get().upper())
            self.refresh_lock_indicator_once()
        except ValueError as exc:
            messagebox.showerror("LED-Reihenfolge", str(exc))

    def refresh_lock_indicator_once(self):
        try:
            changed = self.lock_indicator.poll()
            if changed is not None:
                self.lock_status.set(display_text(changed))
        except (OSError, RuntimeError) as exc:
            self.lock_status.set(f"Lock-Anzeige nicht verfügbar: {exc}")

    def refresh_lock_indicator(self):
        self.refresh_lock_indicator_once()
        self.root.after(250, self.refresh_lock_indicator)

    def start(self):
        if self.monitor is not None:
            return
        hw = self.hardware.get()
        if hw and not messagebox.askyesno("Hardware-Freigabe", "Caps/Num/Scroll ändern auch die Tastenfunktionen. Wirklich aktivieren?"):
            return
        try:
            if hw:
                hardware_lease.claim('B')
            cfg = replace(Config(), hardware=hw)
            indicator = IndicatorSettings(self.disk_device.get(), float(self.saturation.get()))
            indicator.validate()
            self.monitor = Monitor(cfg, indicator_settings=indicator,
                on_update=lambda sample, states: self.queue.put((sample, states,
                    self.monitor.disk_rates, indicator)))
            self.monitor.start()
        except Exception as exc:
            hardware_lease.release('B')
            self.monitor = None
            messagebox.showerror("Startfehler", str(exc))
            return
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status.set("Aktiv · " + ("Hardwaremodus" if hw else "Simulation"))

    def stop(self):
        if self.monitor:
            try:
                self.monitor.stop()
            except TimeoutError as exc:
                self.status.set(str(exc))
                return
            self.monitor = None
        hardware_lease.release('B')
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status.set("Gestoppt · Lock-Tastenzustände soweit möglich wiederhergestellt")

    def drain(self):
        while not self.queue.empty():
            sample, states, disk, indicator = self.queue.get_nowait()
            color = indicator_hex(disk, indicator)
            self.ssd_visual.configure(text=(f"SSD · ◉    Lesen: {disk.read_bps/1024:.1f} KiB/s"
                f"    Schreiben: {disk.write_bps/1024:.1f} KiB/s"),
                bg=color, fg=("#ffffff" if max(int(color[1:3],16), int(color[3:5],16)) < 125 else "#101010"))
            self.output.delete("1.0", "end")
            for name, value in vars(sample).items():
                unit = "%" if name in ("cpu", "memory") else " B/s"
                self.output.insert("end", f"{name:13s} {value:12.1f}{unit}\n")
            self.output.insert("end", "\nLED-Regeln: " + ", ".join(f"{k}={'ON' if v else 'OFF'}" for k, v in states.items()))
        if self.monitor and self.monitor.worker and not self.monitor.worker.is_alive():
            err = self.monitor.error
            self.stop()
            if err:
                messagebox.showerror("Monitorfehler", str(err))
        self.root.after(100, self.drain)

    def quit(self):
        if self.monitor:
            try:
                self.monitor.stop()
            except TimeoutError:
                messagebox.showwarning("Noch aktiv", "Hintergrundprozess läuft; bitte erneut stoppen.")
                return
        hardware_lease.release('B')
        if not self.embedded:
            self.root.destroy()

def main():
    root = tk.Tk()
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
