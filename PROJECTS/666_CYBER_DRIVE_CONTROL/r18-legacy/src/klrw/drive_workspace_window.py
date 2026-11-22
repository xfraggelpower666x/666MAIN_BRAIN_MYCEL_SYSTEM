"""Independent drive selection, hotplug, multi-icon tray and movable LED overlays.

No direct USB HID writes. Mapping to physical keyboard LEDs remains opt-in only
in the legacy drive_led_window (GLOBAL Windows lock state), not this interface.
"""
import argparse
import time
import queue
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from .ssd import DiskActivitySampler, DiskRates
from .drive_workspace import Workspace, enumerate_drives, exact_io_map
from .drive_speed_display import describe_rate, active_channels
from .bicolor_activity import BicolorActivity, CYAN, PINK, PURPLE, OFF


def drive_hover_details(drive, rate, config, color=OFF):
    """Full accessible information shown only on pointer hover; no device I/O."""
    activity = "Lesen" if color == CYAN else "Schreiben" if color == PINK else "Ruhe"
    return (f"{drive.mount}  |  {drive.label or drive.device or 'Unbenannt'}\n"
            f"Status: {activity}\n"
            f"{describe_rate(rate, config, compact=False)}\n"
            f"Dateisystem: {drive.filesystem or 'unbekannt'}\n"
            f"Quelle: {'Messung verfügbar' if rate is not None else 'I/O nicht zugeordnet'}")


def settings_should_stack(width):
    """Keep the configuration sections legible on narrow windows."""
    return width < 990


class DriveWorkspaceWindow:
    def __init__(self, root, *, workspace=None, inventory=None, sampler=None, tray=True, host=None):
        self.root=root
        self.host=host if host is not None else root
        self.embedded=host is not None
        self.workspace=workspace or Workspace()
        self.inventory=inventory or enumerate_drives
        self.sampler=sampler or DiskActivitySampler()
        self.logical_io=None
        if sys.platform=='win32':
            try:
                from .windows_logical_io import WindowsLogicalDiskSampler
                self.logical_io=WindowsLogicalDiskSampler()
            except (OSError, AttributeError):
                pass
        self.events=queue.Queue()
        self.closed=False
        self.tray_enabled=bool(tray and sys.platform=='win32')
        self.icons={}
        self.drives=[]
        self.rows={}
        self.bicolor=BicolorActivity()
        self._latest_rates={}
        self.overlay=None
        self.overlay_canvas=None
        self._drag=None
        self._hover_regions=[]
        self._hover_popup=None
        self._hover_label=None
        self._hover_key=None
        if not self.embedded:
            self.root.title('R17 · 666 CYBER DRIVE CONTROL')
        self._set_theme()
        if not self.embedded:
            self.root.geometry('1020x680')
            self.root.minsize(720,540)

        # Distinct header, expanding drive list and non-clipped control footer.
        shell=ttk.Frame(self.host,style='Cyber.TFrame',padding=(14,10))
        shell.pack(fill='both',expand=True)
        header=ttk.Frame(shell,style='Cyber.TFrame')
        header.pack(fill='x',pady=(0,10))
        ttk.Label(header,text='666 CYBER DRIVE CONTROL',style='Cyber.Title.TLabel').pack(side='left')
        ttk.Label(header,text='  •  LIVE DRIVE HUD',style='Cyber.Subtitle.TLabel').pack(side='left')
        actions=ttk.Frame(shell,style='Cyber.TFrame')
        actions.pack(fill='x',pady=(0,10))
        ttk.Label(actions,text='LAUFWERKE · getrennte Ausgabeziele',style='Cyber.Section.TLabel').pack(side='left')
        self._neon_button(actions,'Jetzt neu erkennen',self.rescan,accent='cyan').pack(side='right',padx=(8,0))
        self._neon_button(actions,'Overlay zeigen',self.show_overlay,accent='purple').pack(side='right',padx=(8,0))
        self._neon_button(actions,'Speichern',self.save,accent='pink').pack(side='right',padx=(8,0))

        # The scrollbar is part of the frame: no absolute screen positioning.
        list_frame=ttk.Frame(shell,style='Cyber.Panel.TFrame',padding=5)
        list_frame.pack(fill='both',expand=True)
        self.scroller=tk.Canvas(list_frame,highlightthickness=0,borderwidth=0,bg='#1A1F29')
        self.scrollbar=ttk.Scrollbar(list_frame,orient='vertical',command=self.scroller.yview,
                                    style='Cyber.Vertical.TScrollbar')
        self.scroller.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='right',fill='y')
        self.scroller.pack(side='left',fill='both',expand=True)
        self.grid=ttk.Frame(self.scroller,style='Cyber.Panel.TFrame')
        self.grid_id=self.scroller.create_window((0,0),window=self.grid,anchor='nw')
        self.grid.bind('<Configure>',lambda _:self.scroller.configure(scrollregion=self.scroller.bbox('all')))
        self.scroller.bind('<Configure>',lambda e:self.scroller.itemconfigure(self.grid_id,width=e.width))
        self.scroller.bind('<Enter>',lambda e:self.scroller.bind_all('<MouseWheel>',self._scroll_wheel))
        self.scroller.bind('<Leave>',lambda e:self.scroller.unbind_all('<MouseWheel>'))

        # Footer is a separate multi-row settings surface that remains visible.
        footer=ttk.Frame(shell,style='Cyber.TFrame')
        footer.pack(fill='x',pady=(9,0))
        ttk.Label(footer,text='LED: Lesen NEON CYAN · Schreiben NEON PINK · Ruhe DUNKELGRAU  |  USB-HID bleibt gesperrt',
                  style='Cyber.Subtitle.TLabel').pack(anchor='w',pady=(0,5))
        self.status=tk.StringVar(root,'Initialisiere Laufwerksliste ...')
        ttk.Label(footer,textvariable=self.status,style='Cyber.Status.TLabel',wraplength=960).pack(fill='x',pady=(0,8))

        settings=ttk.Frame(footer,style='Cyber.Panel.TFrame',padding=9)
        settings.pack(fill='x')
        settings.columnconfigure(0,weight=1)
        settings.columnconfigure(1,weight=1)
        overlay_group=ttk.Frame(settings,style='Cyber.Panel.TFrame')
        overlay_group.grid(row=0,column=0,sticky='nw',padx=(0,10))
        meter_group=ttk.Frame(settings,style='Cyber.Panel.TFrame')
        meter_group.grid(row=0,column=1,sticky='nw')
        self._settings_meter_group=meter_group
        self._settings_container=settings
        self._settings_stacked=False
        self.root.bind('<Configure>',self._on_window_resize,add='+')

        ttk.Label(overlay_group,text='OVERLAY',style='Cyber.Section.TLabel').grid(row=0,column=0,columnspan=5,sticky='w',pady=(0,6))
        self.lock=tk.BooleanVar(root, self.workspace.data['overlay']['locked'])
        ttk.Checkbutton(overlay_group,text='Position sperren',variable=self.lock,command=self._set_lock,
                        style='Cyber.TCheckbutton').grid(row=1,column=0,columnspan=2,sticky='w',pady=3)
        self._neon_button(overlay_group,'Position speichern',self.save,accent='purple').grid(row=1,column=2,columnspan=3,sticky='w',padx=(8,0),pady=3)
        ttk.Label(overlay_group,text='Größe',style='Cyber.TLabel').grid(row=2,column=0,sticky='w',pady=3)
        self.size=tk.StringVar(root,str(self.workspace.data['overlay']['size']))
        ttk.Combobox(overlay_group,textvariable=self.size,state='readonly',values=['0.75','1.0','1.25','1.5','2.0'],width=6,
                     style='Cyber.TCombobox').grid(row=2,column=1,sticky='w',pady=3)
        self._neon_button(overlay_group,'Anwenden',self._resize_overlay).grid(row=2,column=2,sticky='w',padx=(8,0),pady=3)
        ttk.Label(overlay_group,text='Layout',style='Cyber.TLabel').grid(row=3,column=0,sticky='w',pady=3)
        self.layout=tk.StringVar(root,self.workspace.data['overlay'].get('layout','vertical'))
        ttk.Combobox(overlay_group,textvariable=self.layout,state='readonly',values=['vertical','horizontal','minimal'],
                     width=12,style='Cyber.TCombobox').grid(row=3,column=1,columnspan=2,sticky='w',pady=3)
        ttk.Label(overlay_group,text='Transparenz',style='Cyber.TLabel').grid(row=4,column=0,sticky='w',pady=3)
        self.alpha=tk.StringVar(root,str(self.workspace.data['overlay']['alpha']))
        ttk.Combobox(overlay_group,textvariable=self.alpha,state='readonly',values=['0.35','0.5','0.7','0.85','0.92','1.0'],
                     width=6,style='Cyber.TCombobox').grid(row=4,column=1,sticky='w',pady=3)

        ttk.Label(meter_group,text='AKTIVITÄTSFILTER',style='Cyber.Section.TLabel').grid(row=0,column=0,columnspan=4,sticky='w',pady=(0,6))
        ttk.Label(meter_group,text='Einheit',style='Cyber.TLabel').grid(row=1,column=0,sticky='w',pady=3)
        self.speed_unit=tk.StringVar(root,self.workspace.data['speed_unit'])
        ttk.Combobox(meter_group,state='readonly',values=['KiB/s','MiB/s','MB/s','bit/s'],textvariable=self.speed_unit,width=8,
                     style='Cyber.TCombobox').grid(row=1,column=1,sticky='w',pady=3)
        ttk.Label(meter_group,text='Dezimal',style='Cyber.TLabel').grid(row=1,column=2,sticky='w',padx=(10,3),pady=3)
        self.precision=tk.StringVar(root,str(self.workspace.data['speed_decimals']))
        ttk.Combobox(meter_group,state='readonly',values=['0','1','2','3'],textvariable=self.precision,width=4,
                     style='Cyber.TCombobox').grid(row=1,column=3,sticky='w',pady=3)
        ttk.Label(meter_group,text='Anzeige',style='Cyber.TLabel').grid(row=2,column=0,sticky='w',pady=3)
        self.mode=tk.StringVar(root,self.workspace.data['display_mode'])
        ttk.Combobox(meter_group,state='readonly',values=['compact','detailed'],textvariable=self.mode,width=10,
                     style='Cyber.TCombobox').grid(row=2,column=1,sticky='w',pady=3)
        ttk.Label(meter_group,text='Schwelle KiB/s',style='Cyber.TLabel').grid(row=2,column=2,sticky='w',padx=(10,3),pady=3)
        self.threshold=tk.StringVar(root,str(self.workspace.data['activity_threshold_bps']//1024))
        ttk.Combobox(meter_group,state='readonly',values=['0','1','4','16','64'],textvariable=self.threshold,width=5,
                     style='Cyber.TCombobox').grid(row=2,column=3,sticky='w',pady=3)
        ttk.Label(meter_group,text='Impuls ms',style='Cyber.TLabel').grid(row=3,column=0,sticky='w',pady=3)
        self.hold=tk.StringVar(root,str(self.workspace.data['led_hold_ms']))
        ttk.Combobox(meter_group,state='readonly',values=['100','180','250','400','750'],textvariable=self.hold,width=8,
                     style='Cyber.TCombobox').grid(row=3,column=1,sticky='w',pady=3)
        ttk.Label(meter_group,text='Ruhe ms',style='Cyber.TLabel').grid(row=3,column=2,sticky='w',padx=(10,3),pady=3)
        self.quiet=tk.StringVar(root,str(self.workspace.data['led_quiet_ms']))
        ttk.Combobox(meter_group,state='readonly',values=['250','450','700','1000','2000'],textvariable=self.quiet,width=8,
                     style='Cyber.TCombobox').grid(row=3,column=3,sticky='w',pady=3)
        self._neon_button(meter_group,'Einstellungen anwenden',self._apply_display,accent='pink').grid(
            row=4,column=0,columnspan=4,sticky='ew',pady=(8,0))
        if not self.embedded:
            self.root.protocol('WM_DELETE_WINDOW',self.close)
        self.rescan()
        if any(self.workspace.preferences(d)['overlay'] for d in self.drives):self.show_overlay()
        self.root.after(250,self.tick)

    def _set_theme(self):
        self.root.configure(bg='#11141A')
        style=ttk.Style(self.root)
        # On Windows the native themes ignore ttk background/foreground options.
        # clam renders the semantic Cyber styles consistently.
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        style.configure('Cyber.TFrame',background='#11141A')
        style.configure('Cyber.Panel.TFrame',background='#1A1F29')
        style.configure('Cyber.TLabel',background='#1A1F29',foreground='#EAF7FF',font=('Segoe UI',10))
        style.configure('Cyber.Title.TLabel',background='#11141A',foreground='#35E0FF',font=('Segoe UI',15,'bold'))
        style.configure('Cyber.Subtitle.TLabel',background='#11141A',foreground='#9FB6C9',font=('Segoe UI',9))
        style.configure('Cyber.Section.TLabel',background='#11141A',foreground='#A855FF',font=('Segoe UI',10,'bold'))
        style.configure('Cyber.Status.TLabel',background='#11141A',foreground='#35E0FF',font=('Segoe UI',9))
        style.configure('Cyber.TCheckbutton',background='#1A1F29',foreground='#EAF7FF')
        style.map('Cyber.TCheckbutton',background=[('active','#1A1F29')],foreground=[('disabled','#758394')])
        style.configure('Cyber.TCombobox',fieldbackground='#202535',background='#30384D',
                        foreground='#EAF7FF',arrowcolor='#35E0FF',selectbackground='#A855FF',
                        selectforeground='#FFFFFF',bordercolor='#A855FF',lightcolor='#A855FF')
        style.map('Cyber.TCombobox',fieldbackground=[('readonly','#202535')],
                  foreground=[('readonly','#EAF7FF')],selectbackground=[('readonly','#A855FF')])
        style.configure('Cyber.Vertical.TScrollbar',background='#394054',troughcolor='#11141A',
                        arrowcolor='#35E0FF',bordercolor='#11141A')
        # Existing tree of ttk labels and checkboxes stays readable after theme switch.
        style.configure('TLabel',background='#1A1F29',foreground='#EAF7FF')
        style.configure('TCheckbutton',background='#1A1F29',foreground='#EAF7FF')
        style.map('TCheckbutton',background=[('active','#1A1F29')])
        self.root.option_add('*TCombobox*Listbox.background','#202535')
        self.root.option_add('*TCombobox*Listbox.foreground','#EAF7FF')
        self.root.option_add('*TCombobox*Listbox.selectBackground','#A855FF')

    def _neon_button(self,parent,text,command,accent='cyan'):
        colors={'cyan':'#35E0FF','pink':'#FF4FD8','purple':'#A855FF'}
        color=colors[accent]
        button=tk.Button(parent,text=text,command=command,bg='#202535',fg=color,
                         activebackground='#394054',activeforeground='#FFFFFF',
                         highlightthickness=1,highlightbackground=color,
                         relief='flat',bd=1,padx=10,pady=6,cursor='hand2',
                         font=('Segoe UI',9,'bold'))
        button.bind('<Enter>',lambda e:button.configure(bg='#30304B'))
        button.bind('<Leave>',lambda e:button.configure(bg='#202535'))
        return button

    def _on_window_resize(self,event):
        if event.widget is not self.root:
            return
        stacked=settings_should_stack(event.width)
        if stacked == self._settings_stacked:
            return
        self._settings_stacked=stacked
        self._settings_meter_group.grid_forget()
        if stacked:
            self._settings_meter_group.grid(row=1,column=0,sticky='nw',pady=(8,0))
        else:
            self._settings_meter_group.grid(row=0,column=1,sticky='nw')

    def _scroll_wheel(self,event):
        if self.scroller.winfo_exists():
            self.scroller.yview_scroll(-int(event.delta/120), 'units')

    def _apply_display(self):
        self.workspace.data['speed_unit']=self.speed_unit.get()
        self.workspace.data['speed_decimals']=int(self.precision.get())
        self.workspace.data['display_mode']=self.mode.get()
        self.workspace.data['activity_threshold_bps']=int(self.threshold.get())*1024
        self.workspace.data['overlay']['alpha']=float(self.alpha.get())
        self.workspace.data['overlay']['layout']=self.layout.get()
        self.workspace.data['led_hold_ms']=int(self.hold.get())
        self.workspace.data['led_quiet_ms']=int(self.quiet.get())
        if self.overlay and self.overlay.winfo_exists():
            try:self.overlay.attributes('-alpha',self.workspace.data['overlay']['alpha'])
            except tk.TclError:pass
        self.save()
        self._hide_overlay_tooltip()
        self.redraw_overlay(self._latest_rates)

    def _set_lock(self):
        self.workspace.data['overlay']['locked']=bool(self.lock.get())
        self.save()

    def _resize_overlay(self):
        try:self.workspace.data['overlay']['size']=float(self.size.get())
        except ValueError:return
        self.save();self.redraw_overlay(self._latest_rates)

    def save(self):
        self.workspace.save()
        self.status.set('Konfiguration gespeichert: '+str(self.workspace.path))

    def rescan(self):
        old={(d.key,d.mount,d.label,d.device) for d in self.drives}
        try: current=self.inventory()
        except (OSError,RuntimeError) as exc:
            self.status.set('Laufwerksinventar fehlgeschlagen: '+str(exc));return
        if len({d.key for d in current}) != len(current):
            self.status.set('WARNUNG: doppelte Laufwerk-ID im Inventar');return
        changed={(d.key,d.mount,d.label,d.device) for d in current} != old
        self.drives=current
        self.bicolor.forget_missing({d.key for d in current})
        if changed and self.logical_io:
            try:self.logical_io.configure([d.mount for d in current])
            except OSError:
                self.logical_io.close();self.logical_io=None
        if changed:
            for child in self.grid.winfo_children():child.destroy()
            self.rows={}
            for col,header in enumerate(('Laufwerk / Label','Tray','Overlay','USB-LED','I/O-Zuordnung','Lesen / Schreiben')):
                ttk.Label(self.grid,text=header).grid(row=0,column=col,sticky='w',padx=6,pady=6)
            for row,d in enumerate(current,1):
                prefs=self.workspace.preferences(d)
                ttl=f'{d.mount}  [{d.label or d.device}]'
                ttk.Label(self.grid,text=ttl,width=37).grid(row=row,column=0,sticky='w',padx=5,pady=4)
                variables=[]
                for col,key in enumerate(('tray','overlay','keyboard'),1):
                    v=tk.BooleanVar(self.root,prefs[key]);variables.append(v)
                    cb=ttk.Checkbutton(self.grid,variable=v,command=lambda k=d.key: self._changed(k))
                    cb.grid(row=row,column=col,padx=8)
                    if key=='keyboard':cb.configure(state='disabled')
                io=ttk.Label(self.grid,text='nicht zugeordnet',width=22)
                io.grid(row=row,column=4,padx=5)
                speed=ttk.Label(self.grid,text='—',width=23)
                speed.grid(row=row,column=5,padx=5)
                self.rows[d.key]=(variables,io,speed)
            self.save()
        if changed:
            self.status.set(f'{len(current)} Laufwerke erkannt · Neuanschluss/Entfernung wird automatisch geprueft')

    def _changed(self,key):
        if key not in self.rows:return
        variables=self.rows[key][0]
        self.workspace.data['drives'][key]={k:bool(v.get()) for k,v in zip(('tray','overlay','keyboard'),variables)}
        self.save()
        self.redraw_overlay(self._latest_rates)

    def _on_drag_start(self,event):
        if self.lock.get():return
        self._drag=(event.x_root,event.y_root,self.overlay.winfo_x(),self.overlay.winfo_y())

    def _on_drag_move(self,event):
        if not self._drag or self.lock.get() or not self.overlay:return
        sx,sy,x,y=self._drag
        self.overlay.geometry(f'+{x+event.x_root-sx}+{y+event.y_root-sy}')

    def _on_drag_end(self,event):
        if not self.overlay:return
        self._drag=None
        if not self.lock.get():
            self.workspace.data['overlay']['x']=self.overlay.winfo_x()
            self.workspace.data['overlay']['y']=self.overlay.winfo_y()
            self.save()

    def _hide_overlay_tooltip(self, event=None):
        popup=getattr(self,'_hover_popup',None)
        self._hover_popup=None
        self._hover_label=None
        self._hover_key=None
        if popup is not None:
            try:popup.destroy()
            except tk.TclError:pass

    def _on_overlay_motion(self,event):
        if getattr(self,'_drag',None):
            self._hide_overlay_tooltip()
            return
        hit=None
        for key,x0,y0,x1,y1 in getattr(self,'_hover_regions',[]):
            if x0<=event.x<=x1 and y0<=event.y<=y1:
                hit=key
                break
        if hit is None:
            self._hide_overlay_tooltip()
            return
        drive=next((d for d in self.drives if d.key==hit),None)
        if drive is None:
            self._hide_overlay_tooltip()
            return
        keys=exact_io_map(self.drives,set(self.sampler.devices()))
        if 'logical:'+drive.mount in self._latest_rates:
            keys[drive.key]='logical:'+drive.mount
        rate=self._latest_rates.get(keys.get(drive.key))
        state=self.bicolor.states.get(drive.key)
        detail=drive_hover_details(drive,rate,self.workspace.data,state.color if state else OFF)
        if self._hover_popup is None:
            popup=tk.Toplevel(self.overlay)
            popup.overrideredirect(True)
            try:popup.attributes('-topmost',True)
            except tk.TclError:pass
            label=tk.Label(popup,text=detail,justify='left',bg='#202535',fg='#EAF7FF',
                           font=('Consolas',10),padx=12,pady=9,
                           highlightthickness=1,highlightbackground=PURPLE)
            label.pack()
            self._hover_popup=popup
            self._hover_label=label
        elif self._hover_key!=hit or self._hover_label.cget('text')!=detail:
            self._hover_label.configure(text=detail)
        self._hover_key=hit
        # Shift away from the pointer, avoiding tooltip interference with dragging.
        self._hover_popup.geometry(f'+{event.x_root+18}+{event.y_root+16}')

    def show_overlay(self):
        if self.overlay is not None and self.overlay.winfo_exists():
            self.overlay.deiconify();self.overlay.lift();return
        self.overlay=tk.Toplevel(self.root)
        self.overlay.title('Drive Activity Overlay')
        self.overlay.overrideredirect(True)
        self.overlay.attributes('-topmost',True)
        try:self.overlay.attributes('-alpha',self.workspace.data['overlay']['alpha'])
        except tk.TclError:pass
        p=self.workspace.data['overlay']
        self.overlay.geometry(f'+{p["x"]}+{p["y"]}')
        self.overlay_canvas=tk.Canvas(self.overlay,bg='#11141A',highlightthickness=2,highlightbackground='#A855FF')
        self.overlay_canvas.pack()
        self.overlay_canvas.bind('<Motion>',self._on_overlay_motion)
        self.overlay_canvas.bind('<Leave>',self._hide_overlay_tooltip)
        self.overlay_canvas.bind('<ButtonPress-1>',lambda event:(self._hide_overlay_tooltip(),self._on_drag_start(event)))
        self.overlay_canvas.bind('<B1-Motion>',self._on_drag_move)
        self.overlay_canvas.bind('<ButtonRelease-1>',self._on_drag_end)
        self.overlay_canvas.bind('<Button-3>',lambda event:(self._hide_overlay_tooltip(),self.overlay.withdraw()))
        self.redraw_overlay(self._latest_rates)

    def redraw_overlay(self,rates):
        if not self.overlay or not self.overlay.winfo_exists():return
        selected=[d for d in self.drives if self.workspace.preferences(d)['overlay']]
        scale=self.workspace.data['overlay']['size']
        layout=self.workspace.data['overlay'].get('layout','vertical')
        horizontal=layout=='horizontal'
        minimal=layout=='minimal'
        rowheight=max(22,int(31*scale))
        colwidth=max(40,int(60*scale))
        if horizontal:
            width=max(colwidth,len(selected)*colwidth+int(20*scale))
            height=max(30,int(49*scale))
        else:
            width=int((88 if minimal else 435 if self.workspace.data['display_mode']=='detailed' else 280)*scale)
            height=max(rowheight,len(selected)*rowheight+int(14*scale))
        self.overlay_canvas.config(width=width,height=height)
        self.overlay_canvas.delete('all')
        self._hover_regions=[]
        io_keys=exact_io_map(selected,set(self.sampler.devices()))
        for d in selected:
            if 'logical:'+d.mount in rates:io_keys[d.key]='logical:'+d.mount
        for index,d in enumerate(selected):
            state=self.bicolor.states.get(d.key)
            color=state.color if state else OFF
            radius=max(5,int(8*scale))
            if horizontal:
                x=int(10*scale)+index*colwidth+colwidth//2
                y=int(15*scale)
                self.overlay_canvas.create_text(x,y,anchor='center',fill=CYAN,
                    font=('Consolas',max(8,int(10*scale)),'bold'),text=d.mount)
                ly=y+max(12,int(18*scale))
                self.overlay_canvas.create_oval(x-radius,ly-radius,x+radius,ly+radius,
                    fill=color,outline=PURPLE if color!=OFF else '#303849',width=2)
                self._hover_regions.append((d.key,x-colwidth//2,0,x+colwidth//2,height))
            else:
                y=int(9*scale)+index*rowheight+radius
                x=int((57 if minimal else 68)*scale)
                self.overlay_canvas.create_text(int(9*scale),y,anchor='w',fill=CYAN,
                    font=('Consolas',max(9,int(11*scale)),'bold'),text=d.mount)
                self.overlay_canvas.create_oval(x-radius,y-radius,x+radius,y+radius,
                    fill=color,outline=PURPLE if color!=OFF else '#303849',width=2)
                if not minimal:
                    rate=rates.get(io_keys.get(d.key))
                    desc=describe_rate(rate,self.workspace.data,
                                       compact=self.workspace.data['display_mode']=='compact')
                    self.overlay_canvas.create_text(int(89*scale),y,anchor='w',fill='#EAF7FF',
                        font=('Consolas',max(7,int(9*scale))),text=desc)
                self._hover_regions.append((d.key,0,index*rowheight,width,(index+1)*rowheight))
        if not selected:
            self.overlay_canvas.create_text(8,8,anchor='nw',fill=CYAN,
                                            text='Keine Laufwerke fuer Overlay gewaehlt')

    def _draw_tray_icon(self,rate):
        from PIL import Image, ImageDraw
        image=Image.new('RGBA',(64,64),(17,24,39,255));draw=ImageDraw.Draw(image)
        read,write=active_channels(rate,self.workspace.data['activity_threshold_bps'])
        draw.ellipse((7,19,29,41),fill=self.workspace.data['read_color'] if read else '#244134')
        draw.ellipse((35,19,57,41),fill=self.workspace.data['write_color'] if write else '#493039')
        return image

    def _update_tray(self,rates):
        if not self.tray_enabled:return
        try:import pystray
        except ImportError:
            self.tray_enabled=False;self.status.set('pystray fehlt: nur Overlay verfuegbar');return
        wanted={d.key:d for d in self.drives if self.workspace.preferences(d)['tray']}
        for key in list(self.icons):
            if key not in wanted:
                self.icons.pop(key).stop()
        io_keys=exact_io_map(self.drives,set(self.sampler.devices()))
        for d in self.drives:
            if 'logical:'+d.mount in rates:io_keys[d.key]='logical:'+d.mount
        for key,d in wanted.items():
            rate=rates.get(io_keys.get(key))
            if key not in self.icons:
                menu=pystray.Menu(pystray.MenuItem('Laufwerksverwaltung anzeigen',lambda icon,item:self.events.put('show')),
                                  pystray.MenuItem('Beenden',lambda icon,item:self.events.put('exit')))
                icon=pystray.Icon('klrw-'+key,self._draw_tray_icon(rate),'KLRW '+d.mount,menu)
                icon.run_detached()
                self.icons[key]=icon
            else:self.icons[key].icon=self._draw_tray_icon(rate)
            self.icons[key].title=('KLRW '+d.mount+': '+describe_rate(rate,self.workspace.data,compact=True))[:127]

    def tick(self):
        if self.closed:return
        while True:
            try:event=self.events.get_nowait()
            except queue.Empty:break
            if event=='exit':self.close();return
            if event=='show':self.root.after(0,self.root.deiconify)
        self.rescan()
        available=set(self.sampler.devices())
        mapping=exact_io_map(self.drives,available)
        rates={}
        for key in set(mapping.values()):
            try:rates[key]=self.sampler.sample(key)
            except (OSError,KeyError):pass
        if self.logical_io:
            try:
                for letter,value in self.logical_io.sample_all().items():
                    rates['logical:'+letter]=value
            except OSError:pass
        for d in self.drives:
            if 'logical:'+d.mount in rates: mapping[d.key]='logical:'+d.mount
        for d in self.drives:
            if d.key not in self.rows:continue
            variables,io,speed=self.rows[d.key]
            iok=mapping.get(d.key)
            io.config(text=iok if iok else 'nicht zugeordnet')
            rate=rates.get(iok)
            speed.config(text=describe_rate(rate,self.workspace.data,compact=True) if rate else '—')
        self._latest_rates=rates
        now_ms=time.monotonic()*1000
        cfg=self.workspace.data
        for d in self.drives:
            rate=rates.get(mapping.get(d.key))
            self.bicolor.sample(d.key,rate,now_ms,
                threshold_bps=cfg['activity_threshold_bps'],
                burst_bps=cfg['burst_bps'],
                hold_ms=cfg['led_hold_ms'],
                quiet_ms=cfg['led_quiet_ms'])
        self.redraw_overlay(rates)
        try:self._update_tray(rates)
        except (OSError,RuntimeError) as exc:self.status.set('Tray: '+str(exc))
        self.root.after(self.workspace.data['interval_ms'],self.tick)

    def close(self):
        if self.closed:return
        self.closed=True
        self.save()
        for icon in self.icons.values():
            try:icon.stop()
            except Exception:pass
        self.icons.clear()
        if self.logical_io:self.logical_io.close()
        if self.overlay:
            self._hide_overlay_tooltip()
            try:self.overlay.destroy()
            except tk.TclError:pass
        if not self.embedded:
            self.root.destroy()


def main(argv=None):
    ap=argparse.ArgumentParser(description='Drive inventory, tray selection and draggable overlay (no HID writes)')
    ap.add_argument('--no-tray',action='store_true')
    ap.add_argument('--config',default=None)
    args=ap.parse_args(argv)
    root=tk.Tk()
    DriveWorkspaceWindow(root,workspace=Workspace(args.config),tray=not args.no_tray)
    root.mainloop();return 0

if __name__=='__main__':raise SystemExit(main())
