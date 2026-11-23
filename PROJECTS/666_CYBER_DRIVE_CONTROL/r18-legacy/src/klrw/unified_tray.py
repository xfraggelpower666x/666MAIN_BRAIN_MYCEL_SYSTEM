"""Einheitliche optionale Windows-Tray-Anwendung ohne Hardware-Schreibzugriffe."""
import argparse
import queue
import sys
import traceback
import tkinter as tk
from .lock_indicator import WindowsLockReader, PreviewLockReader
from .ssd import DiskActivitySampler, DiskRates
from .network_directions import NetworkDirectionSampler, NetworkRates
from .metrics import SystemSampler
from .unified_state import compose_frame, icon_colors


def render_icon(frame, size=64):
    from PIL import Image, ImageDraw
    if size < 24: raise ValueError("icon size >= 24 required")
    img = Image.new('RGBA',(size,size),(13,17,29,255))
    draw = ImageDraw.Draw(img)
    colors = icon_colors(frame)
    pad = size // 9
    cell = max(3,(size-2*pad-2*max(2,size//22))//3)
    gap = max(2,size//22)
    for i,color in enumerate(colors):
        x=pad+(i%3)*(cell+gap); y=pad+(i//3)*(cell+gap)
        draw.rounded_rectangle((x,y,x+cell,y+cell),radius=max(1,cell//5),fill=(*color,255))
    return img


class UnifiedSampler:
    """Adapter über vorhandene R1/R2/R8-Sampler. Disk/NIC-Auswahl bleibt lokal."""
    def __init__(self, *, reader=None, system=None, disks=None, network=None,
                 device='_total', interface='_total', preview=False):
        self.reader = reader if reader is not None else (PreviewLockReader() if preview else WindowsLockReader())
        self.system = system if system is not None else SystemSampler()
        self.disks = disks if disks is not None else DiskActivitySampler()
        self.network = network if network is not None else NetworkDirectionSampler()
        self.device, self.interface = device,interface
        self.preview = preview

    def sample(self, *, layer=0, order='NCS'):
        if self.preview:
            # Statische Demo mit realistischen Raten, keine Hardwareabfrage.
            from .metrics import Sample
            sys_sample=Sample(24,39,0,0,0,0)
            disk=DiskRates(self.device,1048576,327680)
            net=NetworkRates(self.interface,262144,65536)
        else:
            sys_sample=self.system.sample()
            disk=self.disks.sample(self.device)
            net=self.network.sample(self.interface)
        return compose_frame(self.reader.read(),disk,net,sys_sample.cpu,sys_sample.memory,
                             layer=layer,order=order)


def activate_tray_or_fallback(window):
    """Optional tray failure must not prevent the visible desktop monitor.

    Calls only the existing tray initialization; never writes keyboard LEDs.
    """
    try:
        window._start_tray()
        return True
    except Exception as exc:
        # pystray / Win32 backend is optional: preserve the Tk UI and expose the failure.
        detail = f'{type(exc).__name__}: {exc}'
        print(f'[TRAY-WARN] Tray backend nicht gestartet: {detail}', file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        try:
            if window.icon is not None:
                window.icon.stop()
        except Exception:
            print('[TRAY-WARN] Teilinitialisiertes Tray konnte nicht beendet werden.', file=sys.stderr)
        window.icon = None
        window.tray_error = detail
        window.text.set(f'Tray nicht verfuegbar ({detail}). Fensteranzeige laeuft weiter.')
        return False


class UnifiedTrayWindow:
    """Tk ist Eigentümer des UI-Threads; pystray sendet nur Queue-Nachrichten."""
    def __init__(self,root,sampler,*,interval_ms=500,enable_tray=True,layer=0,order='NCS'):
        if not 150<=interval_ms<=10000: raise ValueError('interval_ms must be 150..10000')
        self.root,self.sampler,self.interval_ms=root,sampler,interval_ms
        self.events=queue.Queue();self.closed=False;self.icon=None;self.last_fp=None;self.tray_error=None
        self.layer=tk.IntVar(master=root,value=layer)
        self.order=order
        self.text=tk.StringVar(master=root,value='Initializing status...')
        self.disk=tk.StringVar(master=root,value=sampler.device)
        self.network=tk.StringVar(master=root,value=sampler.interface)
        root.title('Keyboard LED Remapper — Unified R13')
        root.geometry('720x280'); root.minsize(610,240)
        root.configure(bg='#101827')
        tk.Label(root,text='UNIFIED LED MONITOR',font=('Segoe UI',14,'bold'),fg='#22d3a1',bg='#101827').pack(pady=(12,4))
        tk.Label(root,textvariable=self.text,justify='left',wraplength=690,
                 font=('Consolas',9),fg='#e2e8f0',bg='#101827').pack(padx=15,pady=8)
        row=tk.Frame(root,bg='#101827');row.pack(pady=7)
        tk.Label(row,text='RGB Layer',fg='#e2e8f0',bg='#101827').pack(side='left',padx=4)
        for n in range(4):tk.Radiobutton(row,text=str(n),variable=self.layer,value=n,bg='#101827',fg='#c5d0de',selectcolor='#182f40',activebackground='#101827').pack(side='left')
        tk.Label(row,text='Disk',fg='#e2e8f0',bg='#101827').pack(side='left',padx=(20,4))
        tk.Entry(row,textvariable=self.disk,width=13).pack(side='left')
        tk.Label(row,text='NIC',fg='#e2e8f0',bg='#101827').pack(side='left',padx=(10,4))
        tk.Entry(row,textvariable=self.network,width=13).pack(side='left')
        tk.Button(root,text='Apply source selection',command=self.apply_sources).pack(pady=4)
        tk.Label(root,text='Read-only preview · RGB colors do not control physical keyboard LEDs',fg='#94a3b8',bg='#101827').pack()
        root.protocol('WM_DELETE_WINDOW',self.hide)
        if enable_tray: activate_tray_or_fallback(self)
        root.after(0,self._tick)

    def apply_sources(self):
        # Only source selectors, never arbitrary commands or paths.
        self.sampler.device=self.disk.get().strip() or '_total'
        self.sampler.interface=self.network.get().strip() or '_total'

    def _start_tray(self):
        if sys.platform!='win32': raise OSError('Native tray requires Windows; use --preview --no-tray')
        try: import pystray
        except ImportError as e: raise RuntimeError('pip install -e ".[tray]"') from e
        initial=self.sampler.sample(layer=self.layer.get(),order=self.order)
        menu=pystray.Menu(pystray.MenuItem('Show/Hide',lambda icon,item:self.events.put('toggle')),
                          pystray.MenuItem('Exit',lambda icon,item:self.events.put('quit')))
        self.icon=pystray.Icon('KLRW Unified',render_icon(initial),'KLRW Unified Monitor',menu)
        self.icon.run_detached()

    def _tick(self):
        if self.closed:return
        while True:
            try:e=self.events.get_nowait()
            except queue.Empty:break
            if e=='quit': self.close();return
            if e=='toggle':
                if self.root.state()=='withdrawn': self.root.deiconify()
                else:self.hide()
        try:
            f=self.sampler.sample(layer=self.layer.get(),order=self.order)
            if f.fingerprint != self.last_fp:
                self.last_fp=f.fingerprint
                self.text.set(f.tooltip)
                if self.icon:
                    self.icon.icon=render_icon(f)
                    self.icon.title=f.tooltip[:120]
        except Exception as exc:
            self.text.set(f'FAILED TO READ: {type(exc).__name__}: {str(exc)[:160]}')
            print(f'[TRAY-READ] Sensorfehler: {type(exc).__name__}: {exc}', file=sys.stderr, flush=True)
        self.root.after(self.interval_ms,self._tick)

    def hide(self):
        if self.icon is None:self.close()
        else:self.root.withdraw()

    def close(self):
        if self.closed:return
        self.closed=True
        if self.icon:
            self.icon.stop();self.icon=None
        self.root.destroy()


def main(argv=None):
    ap=argparse.ArgumentParser(description='Unified Windows tray: locks, disk, network and RGB preview')
    ap.add_argument('--preview',action='store_true',help='No real system/hardware reads')
    ap.add_argument('--no-tray',action='store_true',help='Desktop only; supports other OS')
    ap.add_argument('--interval-ms',type=int,default=500)
    ap.add_argument('--layer',type=int,choices=range(4),default=0)
    ap.add_argument('--order',default='NCS')
    ap.add_argument('--disk',default='_total')
    ap.add_argument('--network',default='_total')
    args=ap.parse_args(argv)
    from .lock_indicator import parse_order
    try: parse_order(args.order)
    except ValueError as e:ap.error(str(e))
    try:
        root=tk.Tk()
    except Exception as exc:
        print(f'[TRAY-ERROR] Tk-Fenster konnte nicht erstellt werden: {exc}', file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        return 2
    try:
        UnifiedTrayWindow(root,UnifiedSampler(preview=args.preview,device=args.disk,interface=args.network),
                          interval_ms=args.interval_ms,layer=args.layer,order=args.order,enable_tray=not args.no_tray)
        root.mainloop()
        return 0
    except Exception as exc:
        print(f'[TRAY-ERROR] {type(exc).__name__}: {exc}', file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        try: root.destroy()
        except Exception: pass
        return 2

if __name__=='__main__':raise SystemExit(main())
