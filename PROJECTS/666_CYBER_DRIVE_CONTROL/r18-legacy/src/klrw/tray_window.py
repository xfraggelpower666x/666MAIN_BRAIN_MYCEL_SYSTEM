"""Optional real Windows tray icon and a Tk floating lock indicator.

Requires optional ``pystray`` and ``Pillow`` (``pip install -e .[tray]``).
No keyboard state is ever changed, and no registry keys are written.
"""
import argparse
import queue
import sys
import tkinter as tk
from .lock_indicator import WindowsLockReader, PreviewLockReader
from .tray_state import make_frame, ChangeGate


def draw_icon(frame, size=64):
    """Render an original triple-bar icon from state, no upstream assets."""
    from PIL import Image, ImageDraw
    if size < 16:
        raise ValueError("size must be >= 16")
    img = Image.new("RGBA", (size, size), (13, 17, 29, 255))
    draw = ImageDraw.Draw(img)
    slots = 3
    gap = max(2, size // 16)
    margin = max(3, size // 9)
    width = (size - 2 * margin - (slots - 1) * gap) // slots
    colors = {True:(35, 224, 160, 255),False:(70, 77, 92, 255)}
    for idx in range(slots):
        enabled = frame.enabled[idx] if idx < len(frame.enabled) else False
        x0 = margin + idx * (width + gap)
        draw.rounded_rectangle((x0,margin,x0+width,size-margin),radius=max(2,width//3),fill=colors[enabled])
    return img


class TrayWindow:
    """Tk owns the GUI thread; pystray dispatches only queue messages."""
    def __init__(self, root, reader=None, *, order="NCS", interval_ms=250, tray=True):
        if not 100 <= interval_ms <= 10_000:
            raise ValueError("interval_ms must be 100..10000")
        self.root = root
        self.reader = reader if reader is not None else WindowsLockReader()
        self.order = order
        self.interval_ms = interval_ms
        self.events = queue.Queue()
        self.gate = ChangeGate()
        self.icon = None
        self.closed = False
        self.status = tk.StringVar(master=root,value="Reading lock states...")
        root.title("Keyboard Lock LEDs — R12")
        root.attributes("-topmost",True)
        root.resizable(False,False)
        root.configure(bg="#111827")
        label = tk.Label(root,textvariable=self.status,bg="#111827",fg="#25e0a0",font=("Consolas",12,"bold"),padx=16,pady=10)
        label.pack()
        root.protocol("WM_DELETE_WINDOW",self.hide)
        if tray:
            if sys.platform != "win32":
                raise OSError("The native Windows tray requires Windows; use --preview --no-tray")
            self._start_tray()
        root.after(0,self._tick)

    def _start_tray(self):
        try:
            import pystray
        except ImportError as exc:
            raise RuntimeError("Install optional tray dependencies: pip install -e '.[tray]'") from exc
        from .lock_indicator import LockSnapshot
        default = make_frame(LockSnapshot(False,False,False),self.order)
        # Avoid touching Tk from pystray callbacks (they can run in other threads).
        menu = pystray.Menu(
            pystray.MenuItem("Show/Hide",lambda icon,item:self.events.put("toggle")),
            pystray.MenuItem("Exit",lambda icon,item:self.events.put("quit")),
        )
        self.icon = pystray.Icon("KLRW Lock State",draw_icon(default),"Keyboard Lock State",menu)
        self.icon.run_detached()

    def _tick(self):
        if self.closed:return
        while True:
            try: event = self.events.get_nowait()
            except queue.Empty:break
            if event == "quit":
                self.close();return
            if event == "toggle":
                if self.root.state()=="withdrawn":self.root.deiconify()
                else:self.hide()
        try:
            frame=make_frame(self.reader.read(),self.order)
            if self.gate.accept(frame):
                self.status.set(frame.label)
                if self.icon is not None:
                    self.icon.icon=draw_icon(frame)
                    self.icon.title=frame.label[:120]
        except Exception as exc:
            # Remain visible and show a readable error rather than crashing silently.
            self.status.set(f"Lock read error: {type(exc).__name__}")
        self.root.after(self.interval_ms,self._tick)

    def hide(self):
        if self.icon is None:self.close()
        else:self.root.withdraw()

    def close(self):
        if self.closed:return
        self.closed=True
        if self.icon is not None:
            self.icon.stop()
            self.icon=None
        self.root.destroy()


def main(argv=None):
    parser=argparse.ArgumentParser(description="Read-only floating lock indicator with optional Windows tray")
    parser.add_argument("--order",default="NCS",help="N/C/S order; omit letters to hide")
    parser.add_argument("--preview",action="store_true",help="Use all-off simulated lock state")
    parser.add_argument("--no-tray",action="store_true",help="Run floating indicator only")
    parser.add_argument("--interval-ms",type=int,default=250)
    args=parser.parse_args(argv)
    from .lock_indicator import parse_order
    try: parse_order(args.order)
    except ValueError as exc: parser.error(str(exc))
    root=tk.Tk()
    try:TrayWindow(root,reader=PreviewLockReader() if args.preview else None,order=args.order,interval_ms=args.interval_ms,tray=not args.no_tray)
    except (OSError,RuntimeError,ValueError) as exc:
        root.destroy();parser.error(str(exc))
    root.mainloop()
    return 0

if __name__=="__main__":
    raise SystemExit(main())
