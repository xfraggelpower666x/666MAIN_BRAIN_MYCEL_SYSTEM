"""R18 single-process Cyber Control Center: D is the primary control surface.

A/B/C/D/E coexist as tabs; legacy module CLIs remain intact for recovery.
No driver installs or keyboard LED writes occur on startup.
"""
from __future__ import annotations
import argparse
import queue
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox

from .drive_led_window import DriveLedWindow
from .drive_workspace_window import DriveWorkspaceWindow
from .gui import App as ClassicApp
from .overview import OverviewSampler
from .volumes import VolumeSampler

BG = '#11141A'
PANEL = '#1A1F29'
CYAN = '#35E0FF'
PURPLE = '#A855FF'
PINK = '#FF4FD8'
TEXT = '#EAF7FF'
MUTED = '#9FB6C9'
TOOL_ACTIONS = {'Diagnose', 'Setup', 'Update', 'PythonRecovery'}


def configure_theme(root):
    style=ttk.Style(root)
    if 'clam' in style.theme_names():
        style.theme_use('clam')
    style.configure('Cyber.TNotebook',background=BG,borderwidth=0)
    style.configure('Cyber.TNotebook.Tab',background=PANEL,foreground=TEXT,
                    font=('Segoe UI',10,'bold'),padding=(15,10),borderwidth=0)
    style.map('Cyber.TNotebook.Tab',background=[('selected','#342346'),('active','#27394A')],
              foreground=[('selected',CYAN)])
    style.configure('Cyber.Panel.TFrame',background=PANEL)
    style.configure('Cyber.TFrame',background=BG)
    style.configure('Cyber.TLabel',background=BG,foreground=TEXT)
    style.configure('Cyber.TButton',background='#202535',foreground=CYAN,padding=(12,8))
    style.map('Cyber.TButton',background=[('active','#30394C')])
    return style


def neon_button(parent, label, callback, color=CYAN):
    return tk.Button(parent,text=label,command=callback,bg='#202535',fg=color,
        activebackground='#30394C',activeforeground=TEXT,relief='flat',bd=1,
        highlightbackground=color,highlightthickness=1,padx=12,pady=7,
        font=('Segoe UI',9,'bold'),cursor='hand2')


class ControlCenter:
    def __init__(self,root,*,tray=True,auto_overlay=True):
        self.root=root
        self.closed=False
        self.log_events=queue.Queue()
        self._worker=None
        self._log_job=None
        self._overview_job=None
        self._capacity_job=None
        self._overview_sampler=OverviewSampler()
        self._volume_sampler=VolumeSampler()
        root.title('666 CYBER DRIVE CONTROL · R18 Unified System')
        root.geometry('1330x890')
        root.minsize(880,610)
        root.configure(bg=BG)
        configure_theme(root)
        head=tk.Frame(root,bg=BG)
        head.pack(fill='x',padx=14,pady=(9,5))
        tk.Label(head,text='666 CYBER DRIVE CONTROL',bg=BG,fg=CYAN,
                 font=('Segoe UI',19,'bold')).pack(side='left')
        tk.Label(head,text='R18  •  ONE SYSTEM  •  D CORE',bg=BG,fg=PURPLE,
                 font=('Segoe UI',10,'bold')).pack(side='right')
        self.tabs=ttk.Notebook(root,style='Cyber.TNotebook')
        self.tabs.pack(fill='both',expand=True,padx=9,pady=(4,8))
        self.panels={}
        for key,name in [('D','D · LED Mapping'),('E','E · Laufwerke / Overlay'),
                         ('A','A · Kapazität'),('B','B · Klassik'),('C','C · Tools / Recovery'),
                         ('STATUS','Systemstatus')]:
            tab=ttk.Frame(self.tabs,style='Cyber.Panel.TFrame')
            self.tabs.add(tab,text=name)
            self.panels[key]=tab
        # The two primary surfaces are instantiated in the SAME Tk root and process.
        # No extra Tk mainloop; no new Python process.
        self.mapping=DriveLedWindow(root,host=self._scrollable_host(self.panels['D']))
        self.workspace=DriveWorkspaceWindow(root,host=self.panels['E'],tray=tray)
        if not auto_overlay and self.workspace.overlay is not None:
            self.workspace.overlay.withdraw()
        self.classic=ClassicApp(root,host=self._scrollable_host(self.panels['B']))
        self._build_capacity()
        self._build_tools()
        self._build_status()
        self.tabs.select(self.panels['D'])
        root.protocol('WM_DELETE_WINDOW',self.close)
        self._overview_tick()
        self._capacity_tick()
        self._log_tick()

    def _scrollable_host(self,tab):
        """Contain historic D/B widgets in a scrollable area, preserving their controls."""
        canvas=tk.Canvas(tab,bg=PANEL,highlightthickness=0,borderwidth=0)
        scroll=ttk.Scrollbar(tab,orient='vertical',command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right',fill='y')
        canvas.pack(side='left',fill='both',expand=True)
        content=ttk.Frame(canvas,style='Cyber.Panel.TFrame')
        handle=canvas.create_window((0,0),window=content,anchor='nw')
        content.bind('<Configure>',lambda _:canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>',lambda e:canvas.itemconfigure(handle,width=e.width))
        def wheel(event):
            canvas.yview_scroll(-int(event.delta/120) if event.delta else 0,'units')
        canvas.bind('<Enter>',lambda _:canvas.bind_all('<MouseWheel>',wheel))
        canvas.bind('<Leave>',lambda _:canvas.unbind_all('<MouseWheel>'))
        return content

    def _make_text(self,tab,height=14):
        text=tk.Text(tab,bg=BG,fg=TEXT,insertbackground=CYAN,font=('Consolas',10),
                     wrap='word',height=height,relief='flat',padx=12,pady=10)
        text.pack(fill='both',expand=True,padx=15,pady=12)
        text.configure(state='disabled')
        return text

    @staticmethod
    def _set_text(widget,content):
        widget.configure(state='normal')
        widget.delete('1.0','end')
        widget.insert('end',content)
        widget.configure(state='disabled')
        widget.see('end')

    def _build_capacity(self):
        panel=self.panels['A']
        header=tk.Frame(panel,bg=PANEL)
        header.pack(fill='x',padx=14,pady=10)
        tk.Label(header,text='VOLUME CAPACITY  ·  READ ONLY',bg=PANEL,fg=CYAN,
                 font=('Segoe UI',14,'bold')).pack(side='left')
        neon_button(header,'Jetzt aktualisieren',self.refresh_capacity).pack(side='right')
        self.capacity_output=self._make_text(panel)

    def refresh_capacity(self):
        try:
            items,errors=self._volume_sampler.sample()
            lines=['LAUFWERK                 FREI           BELEGT      STATUS','─'*69]
            for item in items:
                lines.append(f'{item.mountpoint:20s} {item.free_bytes/1024**3:9.1f} GiB   {item.used_percent:6.1f}%   {item.status.upper()}')
            for drive,error in errors.items():
                lines.append(f'{drive}: nicht verfügbar ({error})')
            self._set_text(self.capacity_output,'\n'.join(lines))
        except Exception as exc:
            self._set_text(self.capacity_output,f'Kapazitätsmessung nicht verfügbar: {type(exc).__name__}: {exc}')

    def _capacity_tick(self):
        if self.closed:return
        if self.tabs.select()==str(self.panels['A']):self.refresh_capacity()
        self._capacity_job=self.root.after(5000,self._capacity_tick)

    def _build_status(self):
        panel=self.panels['STATUS']
        tk.Label(panel,text='LIVE SYSTEM STATUS',bg=PANEL,fg=CYAN,
                 font=('Segoe UI',15,'bold')).pack(anchor='w',padx=17,pady=(18,4))
        self.status_output=self._make_text(panel)
        tk.Label(panel,text='Alle Ansichten nutzen dieselbe Tk-Hauptschleife. Hardware-LED-Mapping nur nach expliziter Freigabe.',
                 bg=PANEL,fg=MUTED).pack(anchor='w',padx=17,pady=10)

    def _overview_tick(self):
        if self.closed:return
        if self.tabs.select()==str(self.panels['STATUS']):
            try:
                snap=self._overview_sampler.sample()
                info=(f'CPU                 {snap.cpu_pct:.1f}%\n'
                      f'RAM                 {snap.memory_pct:.1f}%\n'
                      f'DISK READ           {snap.disk_read_bps/1024:.1f} KiB/s\n'
                      f'DISK WRITE          {snap.disk_write_bps/1024:.1f} KiB/s\n'
                      f'NETWORK RX          {snap.rx_bps/1024:.1f} KiB/s\n'
                      f'NETWORK TX          {snap.tx_bps/1024:.1f} KiB/s\n\n'
                      f'Laufwerke erkannt:   {len(self.workspace.drives)}\n'
                      f'Workspace-Tray:      {len(self.workspace.icons)} aktive Symbole\n'
                      f'Overlay:             {"sichtbar" if self.workspace.overlay and self.workspace.overlay.winfo_exists() and self.workspace.overlay.state()!="withdrawn" else "aus"}\n'
                      f'Hardware LED:        {"GLOBAL LOCK aktiv" if self.mapping.backend else "Vorschau / AUS"}\n')
                self._set_text(self.status_output,info)
            except Exception as exc:
                self._set_text(self.status_output,f'Sensorstatus nicht verfügbar: {type(exc).__name__}: {exc}')
        self._overview_job=self.root.after(1000,self._overview_tick)

    def _build_tools(self):
        panel=self.panels['C']
        title=tk.Label(panel,text='TOOLS / RECOVERY  ·  BEWUSST AUSFÜHREN',
                       bg=PANEL,fg=PURPLE,font=('Segoe UI',14,'bold'))
        title.pack(anchor='w',padx=16,pady=(17,8))
        tk.Label(panel,text='Diagnose und Recovery laufen über den vorhandenen Windows-Tool-Manager.\n'
                  'Keine Neuinstallation beim normalen Start. Setup/Update nur nach Bestätigung.',
                 bg=PANEL,fg=TEXT,justify='left').pack(anchor='w',padx=16)
        actions=tk.Frame(panel,bg=PANEL)
        actions.pack(fill='x',padx=16,pady=12)
        for name,label,color in [('Diagnose','Diagnose',CYAN),('Setup','Fehlende Tools reparieren',PURPLE),
                                 ('Update','Projekttools aktualisieren',PINK),('PythonRecovery','Python-Pfade prüfen',CYAN)]:
            neon_button(actions,label,lambda a=name:self.run_tool(a),color).pack(side='left',padx=(0,8))
        self.tool_log=self._make_text(panel,16)
        self._set_text(self.tool_log,'Tools bereit. Es wird nichts automatisch installiert.\n')

    def run_tool(self,action):
        if action not in TOOL_ACTIONS:raise ValueError('unbekannte Tool-Aktion')
        if self._worker and self._worker.is_alive():
            messagebox.showwarning('Tool läuft','Eine Tool-Aktion läuft bereits.',parent=self.root)
            return False
        if action in {'Setup','Update'} and not messagebox.askyesno('Windows-Tool-Aktion',
                     f'{action} kann Abhängigkeiten in der lokalen virtuellen Umgebung verändern. Wirklich starten?',
                     parent=self.root):
            return False
        script=Path(__file__).resolve().parents[2]/'TOOLS'/'WINDOWS_TOOL_MANAGER.ps1'
        if sys.platform!='win32' or not script.is_file():
            self._set_text(self.tool_log,'Windows-Tool-Manager an diesem Host nicht verfügbar.')
            return False
        def worker():
            try:
                p=subprocess.Popen(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass',
                                    '-File',str(script),'-Action',action],
                                   stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                                   text=True,errors='replace',cwd=str(script.parents[1]))
                for line in p.stdout:self.log_events.put(line)
                self.log_events.put(f'\n[{action}] Exit-Code: {p.wait()}\n')
            except Exception as exc:
                self.log_events.put(f'[{action}] FEHLER: {type(exc).__name__}: {exc}\n')
        self._set_text(self.tool_log,f'[{action}] gestartete Benutzeraktion\n')
        self._worker=threading.Thread(target=worker,daemon=True)
        self._worker.start()
        return True

    def _log_tick(self):
        if self.closed:return
        chunks=[]
        while True:
            try: chunks.append(self.log_events.get_nowait())
            except queue.Empty:break
        if chunks:
            self.tool_log.configure(state='normal')
            self.tool_log.insert('end',''.join(chunks))
            self.tool_log.configure(state='disabled')
            self.tool_log.see('end')
        self._log_job=self.root.after(200,self._log_tick)

    def close(self):
        if self.closed:return
        if self._worker and self._worker.is_alive():
            if not messagebox.askyesno('Tool-Aktion läuft',
                   'Eine gestartete Tool-Aktion läuft noch. Fenster schließen?\n'
                   'Die Windows-Aktion kann unabhängig davon weiterlaufen.',parent=self.root):
                return
        self.closed=True
        for job in (self._log_job,self._overview_job,self._capacity_job):
            if job is not None:
                try:self.root.after_cancel(job)
                except tk.TclError:pass
        self.classic.quit()
        self.workspace.close()
        self.mapping.close()
        self.root.destroy()


def main(argv=None):
    p=argparse.ArgumentParser(description='Single-window Keyboard LED Remapper R18')
    p.add_argument('--tab',choices=['A','B','C','D','E','STATUS'],default='D',help='Initial view')
    p.add_argument('--no-tray',action='store_true',help='Skip individual per-volume tray icons')
    p.add_argument('--no-overlay',action='store_true',help='Keep configured overlay hidden at startup')
    args=p.parse_args(argv)
    root=tk.Tk()
    try:
        controller=ControlCenter(root,tray=not args.no_tray,auto_overlay=not args.no_overlay)
        controller.tabs.select(controller.panels[args.tab])
    except Exception:
        root.destroy()
        raise
    root.mainloop()
    return 0

if __name__=='__main__':
    raise SystemExit(main())
