"""Read/write disk LED dashboard with opt-in GLOBAL Windows lock-key mirroring.

WindowsLockBackend changes Caps/Num/Scroll FUNCTIONAL lock states system-wide.
It cannot target a single USB keyboard or independently control its LEDs.
Default is visual-only; no disk writes or drivers are installed.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from .ssd import DiskActivitySampler, DiskRates
from .drive_led_mapping import DriveBinding, evaluate, LEDS, MODES
from . import hardware_lease

READ_COLOR = '#36df77'
WRITE_COLOR = '#ff465a'
BG = '#111827'
FG = '#e2e8f0'

class DriveLedWindow:
    def __init__(self, root, sampler=None, backend_factory=None, interval_ms=300, host=None):
        if not 150 <= interval_ms <= 10000:
            raise ValueError('Polling interval must be 150..10000 ms')
        self.root = root
        self.host = host if host is not None else root
        self.embedded = host is not None
        self.sampler = sampler or DiskActivitySampler()
        self.backend_factory = backend_factory
        self.backend = None
        self.closed = False
        self.interval_ms = interval_ms
        self.disks = list(self.sampler.devices())
        self.disks = list(dict.fromkeys(self.disks)) or ['_total']
        self.rows = {}
        self.config = {}
        if not self.embedded:
            root.title('Keyboard LED Remapper — Drive Read/Write + Keyboard Mapping')
            root.geometry('850x670')
            root.minsize(700, 530)
        self.host.configure(style="Cyber.Panel.TFrame") if isinstance(self.host, ttk.Frame) else self.host.configure(bg=BG)
        tk.Label(self.host, text='DRIVE ACTIVITY · READ / WRITE', bg=BG, fg=FG,
                 font=('Segoe UI', 16, 'bold')).pack(pady=(12, 6))
        tk.Label(self.host, text='READ = GRUEN   |   WRITE = ROT   |   GEMISCHT = BEIDE',
                 bg=BG, fg=FG).pack()
        self.drive_frame = ttk.Frame(self.host)
        self.drive_frame.pack(fill='both', expand=True, padx=18, pady=10)
        self._build_drive_rows()
        ttk.Label(self.host, text='USB-Tastatur Lock-LED-Zuordnung (zunaechst nur Vorschau)').pack(pady=(7, 3))
        grid = ttk.Frame(self.host)
        grid.pack(fill='x', padx=18)
        for i, col in enumerate(('LED', 'Laufwerk', 'Aktivitaet', 'Schwelle KiB/s', 'Vorschau')):
            ttk.Label(grid, text=col).grid(row=0, column=i, sticky='w', padx=6)
        for i, led in enumerate(LEDS, 1):
            drive = tk.StringVar(root, self.disks[0])
            mode = tk.StringVar(root, 'off')
            threshold = tk.StringVar(root, '4')
            state = tk.StringVar(root, 'AUS')
            self.config[led] = (drive, mode, threshold, state)
            ttk.Label(grid, text=led.upper()).grid(row=i, column=0, sticky='w', padx=6, pady=3)
            ttk.Combobox(grid, textvariable=drive, state='readonly', values=self.disks, width=19).grid(row=i, column=1, padx=6)
            ttk.Combobox(grid, textvariable=mode, state='readonly', values=MODES, width=10).grid(row=i, column=2, padx=6)
            ttk.Entry(grid, textvariable=threshold, width=12).grid(row=i, column=3, padx=6)
            ttk.Label(grid, textvariable=state).grid(row=i, column=4, padx=6)
        buttons = ttk.Frame(self.host)
        buttons.pack(pady=12)
        self.hardware_button = ttk.Button(buttons, text='Echte Lock-LED-Steuerung EIN (Opt-in)', command=self.enable_hardware)
        self.hardware_button.pack(side='left', padx=8)
        ttk.Button(buttons, text='Hardware AUS / Zustaende wiederherstellen', command=self.disable_hardware).pack(side='left', padx=8)
        self.status = tk.StringVar(root, 'VORSCHAU: keine Tastaturzustaende werden veraendert')
        ttk.Label(self.host, textvariable=self.status, wraplength=780).pack(pady=(2, 14))
        if not self.embedded:
            root.protocol('WM_DELETE_WINDOW', self.close)
        root.after(0, self.tick)

    def _build_drive_rows(self):
        for widget in self.drive_frame.winfo_children():
            widget.destroy()
        self.rows = {}
        for idx, drive in enumerate(self.disks):
            ttk.Label(self.drive_frame, text=drive, width=25).grid(row=idx, column=0, padx=6, pady=3, sticky='w')
            read = ttk.Progressbar(self.drive_frame, length=165, maximum=100)
            write = ttk.Progressbar(self.drive_frame, length=165, maximum=100)
            read.grid(row=idx, column=1, padx=6)
            write.grid(row=idx, column=2, padx=6)
            txt = tk.StringVar(self.root, 'R 0 / W 0 KiB/s')
            ttk.Label(self.drive_frame, textvariable=txt, width=29).grid(row=idx, column=3, padx=6)
            self.rows[drive] = (read, write, txt)
        # Actual unambiguous colors are displayed in the per-drive dual indicators below.
        self.colors = tk.Canvas(self.drive_frame, height=max(32, len(self.disks)*28), width=48, highlightthickness=0)
        self.colors.grid(row=0, column=4, rowspan=max(1,len(self.disks)), sticky='ns')

    def _bindings(self):
        bindings=[]
        for led, (drive, mode, threshold, _) in self.config.items():
            bindings.append(DriveBinding(led, drive.get(), mode.get(), float(threshold.get())))
        return bindings

    def enable_hardware(self):
        if self.backend is not None:
            return
        if not messagebox.askyesno('GLOBALER Lock-Key-Eingriff',
            'ACHTUNG: Windows aendert Caps Lock, Num Lock und Scroll Lock systemweit!\n'
            'Es wird NICHT nur eine bestimmte USB-Tastatur-LED gesteuert.\n'
            'Dies kann die Texteingabe und den Nummernblock beeinflussen.\n'
            'Beim normalen Beenden werden die anfangs erkannten Zustaende wiederhergestellt.\n\n'
            'Trotzdem ECHTE Lock-Key-Steuerung einschalten?', parent=self.root):
            return
        try:
            bindings = self._bindings()
            if all(binding.mode == 'off' for binding in bindings):
                raise ValueError('Mindestens eine LED-Zuordnung aktivieren (read/write/either)')
            hardware_lease.claim('D')
            if self.backend_factory is None:
                from .leds import WindowsLockBackend
                self.backend = WindowsLockBackend()
            else:
                self.backend = self.backend_factory()
            self.status.set('ACHTUNG: globale Windows Lock-Key-Zustaende werden aktiv geschrieben')
        except Exception as exc:
            hardware_lease.release('D')
            self.backend = None
            messagebox.showerror('Hardware nicht aktiv', str(exc), parent=self.root)

    def disable_hardware(self):
        backend, self.backend = self.backend, None
        if backend is not None:
            try:
                backend.close()
            except Exception as exc:
                self.status.set('WARNUNG: Wiederherstellung fehlgeschlagen: ' + str(exc))
                return
        hardware_lease.release('D')
        self.status.set('VORSCHAU: keine Tastaturzustaende werden veraendert')

    def tick(self):
        if self.closed:
            return
        try:
            rates={drive:self.sampler.sample(drive) for drive in self.disks}
            self.colors.delete('all')
            for i, (drive, snapshot) in enumerate(rates.items()):
                read,write,txt=self.rows[drive]
                read['value']=min(100, snapshot.read_bps/1024/10)
                write['value']=min(100, snapshot.write_bps/1024/10)
                txt.set(f'R {snapshot.read_bps/1024:.1f} / W {snapshot.write_bps/1024:.1f} KiB/s')
                y=3+i*28
                self.colors.create_rectangle(2,y,21,y+18,fill=READ_COLOR if snapshot.read_bps>4096 else '#283c35',outline='')
                self.colors.create_rectangle(25,y,44,y+18,fill=WRITE_COLOR if snapshot.write_bps>4096 else '#45313b',outline='')
            targets=evaluate(self._bindings(),rates)
            for led, active in targets.items():
                self.config[led][3].set('AN' if active else 'AUS')
            if self.backend is not None:
                try:
                    for binding in self._bindings():
                        # OFF means no control. If an actively controlled key is later
                        # disabled, restore its original state (best effort).
                        if binding.mode == 'off':
                            if led_original := getattr(self.backend, 'original', None):
                                if binding.led in getattr(self.backend, 'touched', set()):
                                    self.backend.apply(binding.led, led_original[binding.led])
                        else:
                            self.backend.apply(binding.led, targets[binding.led])
                except Exception as exc:
                    self.disable_hardware()
                    self.status.set('Hardware-Fehler, deaktiviert: '+str(exc))
        except (ValueError, OSError, RuntimeError) as exc:
            self.status.set('Pruefung: '+str(exc))
        self.root.after(self.interval_ms,self.tick)

    def close(self):
        if self.closed:
            return
        self.closed=True
        self.disable_hardware()
        if not self.embedded:
            self.root.destroy()


def main(argv=None):
    import argparse
    ap=argparse.ArgumentParser(description='Disk read/write virtual LEDs + optional GLOBAL Caps/Num/Scroll mapping')
    ap.add_argument('--interval-ms',type=int,default=300)
    args=ap.parse_args(argv)
    root=tk.Tk()
    try:
        DriveLedWindow(root,interval_ms=args.interval_ms)
    except Exception:
        root.destroy()
        raise
    root.mainloop()
    return 0

if __name__=='__main__':
    raise SystemExit(main())
