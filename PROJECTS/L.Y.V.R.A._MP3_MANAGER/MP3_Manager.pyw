"""666SOUNDsDESIGn MP3-Manager, nicht-destruktive Windows-Oberfläche."""
import csv
import hashlib
import io
from PIL import ImageOps
import time
import json
import subprocess
import threading
import time
import os
import re
import shutil
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
from PIL import Image, ImageTk
from mutagen.id3 import ID3, ID3NoHeaderError, TIT2, TPE1, TPE2, TALB, TCON, TCOM, TDRC, TRCK, TPOS, COMM, WOAS, APIC
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
except ImportError:
    TkinterDnD = None
    DND_FILES = None

TIME_RE = re.compile(r'\s*\[\d+m\d+s\s*-\s*\d+m\d+s\](?=\.(?:mp3|wav)$)', re.I)
TAG_TIME_RE = re.compile(r'\s*\[\d+m\d+s\s*-\s*\d+m\d+s\]', re.I)
NUM_RE = re.compile(r'(?P<spacing>\s*)\((?P<number>\d+)\)$')
DEFAULT_COMMENT = '666SOUNDsDESIGn - https://webradio.666soundsdesign-broadcaster.com/'
DEFAULT_SOURCE = 'https://webradio.666soundsdesign-broadcaster.com/'
FIELDS = [
    ('TIT2', 'Songtitel'), ('TPE1', 'Interpret'), ('TPE2', 'Albuminterpret'),
    ('TALB', 'Album'), ('TCON', 'Genre'), ('TCOM', 'Komponist'),
    ('TDRC', 'Jahr'), ('TRCK', 'Tracknummer'), ('TPOS', 'Disc-Nummer'),
    ('COMM', 'Kommentar'), ('WOAS', 'Webquelle / URL')]
FRAME_CLASS = {'TIT2': TIT2, 'TPE1': TPE1, 'TPE2': TPE2, 'TALB': TALB, 'TCON': TCON,
               'TCOM': TCOM, 'TDRC': TDRC, 'TRCK': TRCK, 'TPOS': TPOS}
DEFAULTS = {'TPE1':'FRAGGELPOWER666', 'TPE2':'FRAGGEL', 'TCON':'PSYCHOACOUSTIC PSYTRANCE',
            'TCOM':'FRAGGELPOWER666', 'TDRC':'2026', 'TRCK':'666', 'TPOS':'666',
            'COMM':DEFAULT_COMMENT, 'WOAS':DEFAULT_SOURCE}

def file_sha256(path):
    """Stream-based read-only digest, auch für große Suno-WAV-Dateien."""
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def write_audio_evidence(output_path, source_path, *, preset, normalized, qc_result=None,
                         reference_mp3=None):
    """Neutrale Export-Evidenz; kein subjektiver Artefakt-PASS.

    Der Report wird separat angelegt und verändert kein Audio / keine ID3-Tags.
    """
    destination = Path(output_path)
    source = Path(source_path)
    reference = Path(reference_mp3) if reference_mp3 else None
    payload = {
        'schema': 'LYVRA_AUDIO_EXPORT_EVIDENCE_V1',
        'output_name': destination.name,
        'output_sha256': file_sha256(destination),
        'source_name': source.name,
        'source_sha256': file_sha256(source),
        'preset': preset,
        'normalization_applied': bool(normalized),
        'technical_qc': qc_result or {'status': 'NOT_RUN'},
        'perceptual_artifacts': 'NOT_TESTED_LISTEN_TO_A_B',
        'original_files_modified': False,
    }
    if reference:
        payload['reference_mp3'] = {
            'name': reference.name,
            'sha256': file_sha256(reference),
            'comparison': 'REFERENCE_ONLY_NOT_MODIFIED_NOT_QUALITY_PROOF'
        }
    report_path = destination.with_name(destination.name + '.quality.json')
    # Exklusiv anlegen: Reports anderer Aufträge niemals überschreiben.
    with report_path.open('x', encoding='utf-8') as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    return report_path


def check_lame_encoder(ffmpeg):
    """Prüft den tatsächlich verfügbaren libmp3lame-Encoder (kein externes LAME nötig)."""
    try:
        result = subprocess.run([str(ffmpeg), '-hide_banner', '-encoders'],
                                capture_output=True, text=True, timeout=12,
                                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0 and bool(re.search(r'(?m)^\s*[A-Z.]{6}\s+libmp3lame\s', result.stdout))


def validate_linear_loudnorm_measurement(stats, target_lufs, true_peak_limit, target_lra=11.0):
    """Fail-closed: Balanced Radio darf nicht still auf Dynamic loudnorm wechseln.

    FFmpeg loudnorm kann linear nur anwenden, wenn die Ziel-LRA nicht kleiner
    als die Quell-LRA ist und ein reiner Gain-Schritt das TP-Limit einhält.
    """
    import math
    required=('input_i', 'input_tp', 'input_lra', 'input_thresh', 'target_offset')
    try:
        data={key:float(stats[key]) for key in required}
    except (KeyError, ValueError, TypeError) as exc:
        raise RuntimeError('Balanced Radio: ungültige EBU-R128-Messwerte') from exc
    if not all(math.isfinite(value) for value in data.values()):
        raise RuntimeError('Balanced Radio: Quelle hat keine endlichen Lautheitsmesswerte')
    if data['input_lra'] > float(target_lra) + 1e-3:
        raise RuntimeError('Balanced Radio: lineare Normalisierung nicht möglich (Quell-LRA über Ziel-LRA). '
                           'Original Preserve/Maximum Quality nutzen oder Zielwerte separat prüfen; kein stiller Dynamic-Fallback.')
    projected_tp=data['input_tp'] + float(target_lufs) - data['input_i']
    if projected_tp > float(true_peak_limit) + 1e-3:
        raise RuntimeError(f'Balanced Radio: lineare Pegelanpassung würde das True-Peak-Limit überschreiten '
                           f'({projected_tp:.1f} > {float(true_peak_limit):.1f} dBTP). '
                           'Kein stiller Dynamic-Fallback; andere Ziel-Lautheit wählen oder Maximum Quality nutzen.')
    return data


def title_clean(value):
    # Runde Klammern um eine abschliessende Versionsnummer entfernen, Ziffer behalten.
    # Beispiel: TRACK (1) -> TRACK 1; sonstige Klammern bleiben unveraendert.
    return NUM_RE.sub(lambda m: ' ' + m.group('number'), TAG_TIME_RE.sub('', value)).strip()

def filename_clean(value):
    return TIME_RE.sub('', value)

def read_tags(path):
    try:
        tags = ID3(path)
    except ID3NoHeaderError:
        tags = ID3()
    result = {}
    for code, _ in FIELDS:
        if code == 'COMM':
            vals = tags.getall('COMM')
            result[code] = str(vals[0].text[0]) if vals and vals[0].text else ''
        elif code == 'WOAS':
            vals = tags.getall('WOAS')
            result[code] = str(vals[0].url) if vals else ''
        else:
            fr = tags.get(code)
            result[code] = str(fr.text[0]) if fr is not None and fr.text else ''
    result['_c2pa'] = any(x.FrameID == 'GEOB' and ('c2pa' in x.desc.lower() or x.mime == 'application/c2pa') for x in tags.getall('GEOB'))
    result['_lyrics'] = bool(tags.getall('USLT'))
    result['_cover'] = bool(tags.getall('APIC'))
    return result

def automatic_convert_tags(mp3_path, source_path, clean_stem, values):
    """Schreibt ID3 nur in die temporäre MP3; prüft anschließend jeden Pflichtwert."""
    try:
        tags = ID3(mp3_path)
    except ID3NoHeaderError:
        tags = ID3()
    final_values = dict(values)
    # Jede Datei erhält ihren individuellen, zuvor bereinigten Dateinamen als Titel.
    final_values['TIT2'] = clean_stem
    for code in ('TIT2','TPE1','TPE2','TALB','TCON','TCOM','TDRC','TRCK','TPOS'):
        tags.delall(code)
        value = final_values.get(code, '')
        if value:
            tags.add(FRAME_CLASS[code](encoding=3, text=[str(value)]))
    tags.delall('COMM')
    if final_values.get('COMM'):
        tags.add(COMM(encoding=3,lang='eng',desc='',text=[final_values['COMM']]))
    tags.delall('WOAS')
    if final_values.get('WOAS'):
        tags.add(WOAS(url=final_values['WOAS']))
    tags.save(mp3_path,v2_version=3)
    check=read_tags(mp3_path)
    for code in ('TIT2','TPE1','TPE2','TALB','TCON','TCOM','TDRC','TRCK','TPOS','COMM','WOAS'):
        expected=str(final_values.get(code,'') or '')
        if check[code] != expected:
            raise RuntimeError(f'ID3-Readback fehlgeschlagen ({code})')

def verify_encoded_mp3(ffmpeg, ffprobe, output_path, source_duration=0, runner=None):
    """Technischer Audio-QC: vollständiges Dekodieren und Dauerprüfung.

    Keine psychoakustische Qualitätsbehauptung: verlustbehaftete Artefakte
    können trotz technisch einwandfreier Dekodierung vorhanden sein.
    """
    if runner is None:
        runner=lambda cmd: subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    decode=runner([ffmpeg, '-hide_banner', '-nostdin', '-v', 'error',
                   '-xerror', '-err_detect', 'explode', '-i', str(output_path),
                   '-map', '0:a:0', '-f', 'null', '-'])
    if decode.returncode != 0:
        raise RuntimeError('Audio-QC: MP3 kann nicht fehlerfrei dekodiert werden: '+(decode.stderr or '')[-350:])
    probe=runner([ffprobe, '-v', 'error', '-show_entries', 'format=duration',
                  '-of', 'default=noprint_wrappers=1:nokey=1', str(output_path)])
    if probe.returncode != 0:
        raise RuntimeError('Audio-QC: MP3-Dauer nicht lesbar')
    try:
        duration=float(probe.stdout.strip())
    except (ValueError, AttributeError):
        raise RuntimeError('Audio-QC: ungültige Ausgabedauer')
    if not (duration > 0):
        raise RuntimeError('Audio-QC: leere oder ungültige MP3-Dauer')
    if source_duration and abs(duration-source_duration) > max(0.5, source_duration*0.015):
        raise RuntimeError(f'Audio-QC: Laufzeitabweichung Quelle {source_duration:.2f}s / MP3 {duration:.2f}s')
    return {'decode':'PASS','duration_seconds':round(duration,3),
            'scope':'TECHNICAL_DECODE_ONLY_NOT_PERCEPTUAL_ARTIFACT_PROOF'}


def audio_lab_launch_spec(tool, project_roots, platform=None):
    """Resolve an installed sibling tool without downloading or installing dependencies."""
    host = platform or sys.platform
    project_name = {
        'suno': 'Suno-Song-Remaster-main',
        'restoration': 'Restoration-Lab-main',
        'sunocleanser': 'SunoCleanser-0.2.1',
    }.get(tool)
    if project_name is None:
        raise ValueError(f'Unbekanntes Audio-Tool: {tool}')

    candidates = [Path(root) / project_name for root in project_roots]
    for project in candidates:
        if not project.is_dir():
            continue
        if tool == 'suno':
            packaged_app = project / 'AI Music Remastering.exe'
            if host == 'win32' and packaged_app.is_file():
                return [str(packaged_app)], project
            if not (project / 'package.json').is_file():
                continue
            electron_paths = (
                project / 'node_modules' / 'electron' / 'dist' / 'electron.exe',
                project / 'node_modules' / '.bin' / 'electron',
                project / 'node_modules' / 'electron' / 'dist' / 'Electron.app' / 'Contents' / 'MacOS' / 'Electron',
            )
            electron = next((path for path in electron_paths if path.is_file()), None)
            if electron is None:
                raise RuntimeError(
                    'Suno Song Remaster ist vorhanden, aber Electron fehlt. '
                    'Abhängigkeiten manuell im Projektordner installieren; der Manager installiert nichts.'
                )
            return [str(electron), '.'], project

        if tool == 'restoration':
            packaged_app = project / 'Restoration Lab.exe'
            if host == 'win32' and packaged_app.is_file():
                return [str(packaged_app)], project
            launcher = project / 'STARTEN.bat'
            if host == 'win32' and launcher.is_file():
                return ['cmd.exe', '/c', str(launcher)], project
            raise RuntimeError(
                'Restoration Lab kann hier nicht gestartet werden. '
                'Unter Windows bitte STARTEN.bat im Projektordner verwenden.'
            )

        launcher = project / ('sunocleanser-gui.bat' if host == 'win32' else 'sunocleanser-gui.sh')
        if launcher.is_file():
            if host == 'win32':
                return ['cmd.exe', '/c', str(launcher)], project
            return ['bash', str(launcher)], project
        raise RuntimeError(
            'SunoCleanser-Launcher fehlt. Bitte das Projekt mit der '
            'Conda-Umgebung "sunocleanser" einrichten.'
        )

    raise FileNotFoundError(
        f'{project_name} wurde nicht neben dem Manager oder unter external-tools gefunden.'
    )


class NeonUI:
    BG = '#080913'; PANEL = '#12132a'; FIELD = '#191d38'
    CYAN = '#31eaff'; PINK = '#ff37d1'; VIOLET = '#a476ff'; TEXT = '#f3efff'

    @classmethod
    def setup(cls, root):
        root.configure(bg=cls.BG)
        st=ttk.Style(root)
        try: st.theme_use('clam')
        except tk.TclError: pass
        st.configure('.', background=cls.BG, foreground=cls.TEXT, font=('Segoe UI', 10))
        st.configure('TFrame', background=cls.BG)
        st.configure('TLabel', background=cls.BG, foreground=cls.TEXT)
        st.configure('TLabelframe', background=cls.BG, foreground=cls.PINK, bordercolor=cls.VIOLET)
        st.configure('TLabelframe.Label', background=cls.BG, foreground=cls.PINK, font=('Segoe UI Semibold',10))
        st.configure('TButton', background=cls.PANEL, foreground=cls.CYAN, bordercolor=cls.VIOLET, padding=(10,6))
        st.map('TButton', background=[('active','#302050'),('pressed','#4b2864')],foreground=[('disabled','#777688'),('active','#ffffff')])
        st.configure('TEntry', fieldbackground=cls.FIELD, foreground=cls.TEXT, insertcolor=cls.CYAN, bordercolor=cls.VIOLET)
        st.configure('TCombobox', fieldbackground=cls.FIELD, foreground=cls.TEXT, background=cls.PANEL, arrowcolor=cls.CYAN)
        st.map('TCombobox', fieldbackground=[('readonly',cls.FIELD)], foreground=[('readonly',cls.TEXT)])
        st.configure('TCheckbutton', background=cls.BG, foreground=cls.TEXT)
        st.map('TCheckbutton', background=[('active',cls.BG)],foreground=[('active',cls.CYAN)])
        st.configure('TRadiobutton', background=cls.BG, foreground=cls.TEXT)
        st.configure('Treeview',background=cls.PANEL,fieldbackground=cls.PANEL,foreground=cls.TEXT,rowheight=27,bordercolor=cls.VIOLET)
        st.map('Treeview',background=[('selected','#563282')],foreground=[('selected','#ffffff')])
        st.configure('Treeview.Heading', background='#261a43', foreground=cls.CYAN, font=('Segoe UI Semibold',10))
        st.configure('Vertical.TScrollbar',background=cls.VIOLET,troughcolor=cls.BG)
        st.configure('TNotebook',background=cls.BG,borderwidth=0)
        st.configure('TNotebook.Tab',background=cls.PANEL,foreground=cls.TEXT,padding=(10,5),font=('Segoe UI Semibold',9))
        st.map('TNotebook.Tab',background=[('selected','#38205a'),('active','#242040')],foreground=[('selected',cls.CYAN)])
        st.configure('Action.TButton',background=cls.PINK,foreground='#ffffff',padding=(10,6),font=('Segoe UI Semibold',9))
        st.map('Action.TButton',background=[('active','#a6208b')])
        st.configure('Secondary.TButton',background=cls.PANEL,foreground=cls.CYAN,padding=(10,6),font=('Segoe UI Semibold',9))
        st.map('Secondary.TButton',background=[('active','#30244D')])
        st.configure('Progress.TLabel',background=cls.BG,foreground=cls.CYAN,font=('Segoe UI Semibold',9))
        st.configure('Rename.Horizontal.TProgressbar',troughcolor=cls.FIELD,background=cls.PINK,thickness=14)
        st.configure('Audio.Horizontal.TProgressbar',troughcolor=cls.FIELD,background=cls.CYAN,thickness=14)
        st.configure('Total.Horizontal.TProgressbar',troughcolor=cls.FIELD,background=cls.VIOLET,thickness=14)
        root.option_add('*TCombobox*Listbox.background', cls.PANEL)
        root.option_add('*TCombobox*Listbox.foreground', cls.TEXT)

class ScalableArtwork:
    def __init__(self, parent):
        self.base=Path(getattr(__import__('sys'),'_MEIPASS',Path(__file__).resolve().parent)) / 'assets'
        self.banner=self.read('banner.png')
        self.logo=self.read('logo.png')
        self.host=ttk.Frame(parent)
        self.host.pack(fill='x',pady=(0,4))
        self.banner_label=tk.Label(self.host,bg=NeonUI.BG,bd=0)
        self.banner_label.pack(fill='x')
        # Compact mode: the banner carries the branding, so the extra logo row is
        # kept intentionally minimal to preserve vertical workspace on one screen.
        self.lower=ttk.Frame(self.host)
        self.lower.pack(fill='x',pady=(1,0))
        self.caption=tk.Label(self.lower,text='L.Y.V.R.A. - MP3 MANAGER  •  666SOUNDsDESIGn',fg=NeonUI.CYAN,bg=NeonUI.BG,font=('Segoe UI Semibold',10),anchor='center')
        self.caption.pack(fill='x',expand=True)
        self.last_width=0
        self.host.bind('<Configure>',self.resize)
        self.host.after(200,self.render)

    def read(self,name):
        try: return Image.open(self.base/name).convert('RGBA')
        except (OSError, ValueError): return None

    def resized(self,img,size):
        if img is None: return None
        im=img.copy(); im.thumbnail(size,Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(im)

    def resize(self,event):
        width=event.width
        if abs(width-self.last_width)>12:
            self.last_width=width
            self.host.after_idle(self.render)

    def render(self):
        width=max(self.host.winfo_width(),320)
        if self.banner:
            screen_h=self.host.winfo_toplevel().winfo_height()
            limit=72 if 0<screen_h<760 else 92 if 0<screen_h<950 else 112
            banner_h=max(46,min(limit,int(width*self.banner.height/self.banner.width)))
            photo=self.resized(self.banner,(width,banner_h))
            self.banner_label.configure(image=photo)
            self.banner_label.image=photo
        self.caption.configure(font=('Segoe UI Semibold', 9 if width<900 else 10))

class AutoScrollTab(ttk.Frame):
    """Eigenständige, dynamische Scrollfläche je Reiter, ohne Progress-Footer zu verdecken."""
    def __init__(self, parent):
        super().__init__(parent)
        self.canvas=tk.Canvas(self,bg=NeonUI.BG,highlightthickness=0,bd=0)
        self.bar=ttk.Scrollbar(self,orient='vertical',command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.bar.set)
        self.bar.pack(side='right',fill='y')
        self.canvas.pack(side='left',fill='both',expand=True)
        self.body=ttk.Frame(self.canvas,padding=8)
        self.window=self.canvas.create_window((0,0),window=self.body,anchor='nw')
        self.body.bind('<Configure>',self._region)
        self.canvas.bind('<Configure>',self._width)
        # Scrollen nur bei Mausposition innerhalb dieses Reiters.
        self.canvas.bind('<Enter>',self._enter)
        self.canvas.bind('<Leave>',self._leave)
        self.body.bind('<Enter>',self._enter)
        self.body.bind('<Leave>',self._leave)
    def _region(self,event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
    def _width(self,event):
        self.canvas.itemconfigure(self.window,width=event.width)
    def _enter(self,event=None):
        self.canvas.bind_all('<MouseWheel>',self._wheel)
    def _leave(self,event=None):
        self.canvas.unbind_all('<MouseWheel>')
    def _wheel(self,event):
        if self.canvas.winfo_ismapped():
            self.canvas.yview_scroll(-int(event.delta/120) if event.delta else 0,'units')

class App:
    def __init__(self, root):
        self.root = root
        root.title('L.Y.V.R.A. - MP3 MANAGER v2.36 · PORTABLE QC')
        root.geometry('1360x900')
        root.minsize(760, 550)
        NeonUI.setup(root)
        icon=Path(__file__).resolve().parent/'assets'/'app.ico'
        try: root.iconbitmap(str(icon))
        except (tk.TclError, OSError): pass
        self.lang=tk.StringVar(value='DE')
        self.folder = tk.StringVar()
        self.status = tk.StringVar(value='Ordner auswählen. Scan verändert keine Dateien.')
        self.vars = {k: tk.StringVar(value=DEFAULTS.get(k,'')) for k,_ in FIELDS}
        self.flags = {k: tk.BooleanVar(value=False) for k,_ in FIELDS}
        self.rename_on = tk.BooleanVar(value=True)
        self.clean_title = tk.BooleanVar(value=True)
        self.c2pa_ok = tk.BooleanVar(value=False)
        self.rename_number_suffix = tk.BooleanVar(value=True)
        self.resolve_collisions = tk.BooleanVar(value=True)
        self.cover_global=tk.StringVar(value='')
        self.cover_per_file={}
        self.cover_quality=tk.IntVar(value=95)
        self.cover_fit=tk.StringVar(value='stretch')
        self.cover_enable=tk.BooleanVar(value=False)
        self.title_transfer=tk.StringVar(value='none')
        self.cover_info=tk.StringVar(value='Kein neues Cover ausgewählt')
        self.cover_targets_text=tk.StringVar(value='Keine MP3-Ziele geladen')
        self.cover_preview_image=None
        self.files = {}
        self.file_counts=tk.StringVar(value='GESAMT: 0  |  MP3: 0  |  WAV: 0  |  AUSGEWÄHLT: 0')
        self.selection_mode = tk.StringVar(value='all')
        self.selection_mode.trace_add('write',lambda *_: self.update_file_counts() if hasattr(self,'tree') else None)
        self.busy_rename=False
        self.cancel_rename=False
        self.cancel_audio=threading.Event()
        self.cancel_build=threading.Event()
        self.active_process=None
        self.process_lock=threading.Lock()
        self.build_busy=False
        self.monitor=None
        self.file_manager=None
        self.fm_folder=tk.StringVar(value='')
        self.fm_status=tk.StringVar(value='Dateimanager bereit')
        self.current_file=tk.StringVar(value='Keine laufende Datei')
        self.job_details=tk.StringVar(value='Bereit · Noch kein Vorgang gestartet')
        self.file_percent=tk.DoubleVar(value=0)
        self.label_file=tk.StringVar(value='Einzeldatei · 0 %')
        self.progress_rename=tk.DoubleVar(value=0)
        self.progress_metadata=tk.DoubleVar(value=0)
        self.label_metadata=tk.StringVar(value='Bereit · 0 / 0 Dateien')
        self.progress_audio=tk.DoubleVar(value=0)
        self.progress_total=tk.DoubleVar(value=0)
        self.label_rename=tk.StringVar(value='Bereit · 0 / 0 Dateien')
        self.label_audio=tk.StringVar(value='Bereit · 0 / 0 Dateien')
        self.label_total=tk.StringVar(value='Bereit · 0 %')
        wrapper=ttk.Frame(root,padding=(8,5))
        wrapper.pack(fill='both',expand=True)
        self.artwork=ScalableArtwork(wrapper)
        # Permanente Bestandsanzeige: in jedem Reiter sichtbar.
        countbar=ttk.Frame(wrapper)
        countbar.pack(fill='x',pady=(0,3))
        ttk.Label(countbar,textvariable=self.file_counts,foreground=NeonUI.CYAN,
                  font=('Segoe UI Semibold',11)).pack(side='left',anchor='w')
        ttk.Button(countbar,text='BESTAND AKTUALISIEREN',command=self.refresh_counts,
                   style='Secondary.TButton').pack(side='right')
        languagebar=ttk.Frame(wrapper);languagebar.pack(fill='x',pady=(0,3))
        ttk.Label(languagebar,text='SPRACHE / LANGUAGE',foreground=NeonUI.CYAN).pack(side='left',padx=(0,7))
        ttk.Combobox(languagebar,textvariable=self.lang,values=('DE','EN'),state='readonly',width=5).pack(side='left')
        ttk.Button(languagebar,text='? HILFE / HELP',command=self.open_help,style='Secondary.TButton').pack(side='right')
        self.lang.trace_add('write',lambda *_:self.root.after_idle(self.apply_language))
        self.tabs=ttk.Notebook(wrapper)
        self.tabs.pack(fill='both',expand=True,pady=(2,4))
        self.tab_hosts=[AutoScrollTab(self.tabs) for _ in range(4)]
        files_tab,tags_tab,audio_tab,labs_tab=[h.body for h in self.tab_hosts]
        self.tabs.add(self.tab_hosts[0],text='01  DATEIEN & UMBENENNEN')
        self.tabs.add(self.tab_hosts[1],text='02  METADATEN')
        self.tabs.add(self.tab_hosts[2],text='03  AUDIO CONVERT')
        self.tabs.add(self.tab_hosts[3],text='04  AUDIO LABS')
        self.drop_widgets=[root, files_tab, tags_tab, audio_tab, self.tabs]
        for tab in (files_tab,tags_tab,audio_tab):
            head=ttk.Frame(tab);head.pack(fill='x',pady=(0,2))
            ttk.Button(head,text='▣ DATEIMANAGER / 2. BILDSCHIRM',command=self.open_file_manager,style='Secondary.TButton').pack(side='right')
            ttk.Label(head,text='Dateien/Ordner hierher ziehen · Doppelklick im Dateimanager zum Öffnen',foreground=NeonUI.CYAN).pack(side='left')
            self.drop_widgets.append(head)
        self.register_drop_targets()
        self.build_audio_labs(labs_tab)

        bar=ttk.Frame(files_tab);bar.pack(fill='x',pady=(0,6))
        ttk.Entry(bar,textvariable=self.folder).pack(side='left',fill='x',expand=True)
        ttk.Button(bar,text='Ordner wählen',command=self.choose,style='Secondary.TButton').pack(side='left',padx=4)
        ttk.Button(bar,text='Ordner prüfen',command=self.scan,style='Secondary.TButton').pack(side='left',padx=4)
        ttk.Button(bar,text='CSV exportieren',command=self.export_csv,style='Secondary.TButton').pack(side='left',padx=4)
        ttk.Label(files_tab,text='MP3 + WAV werden angezeigt und können umbenannt werden. ID3-Bearbeitung ausschließlich für MP3.').pack(anchor='w',pady=(0,2))
        listbox=ttk.Frame(files_tab);listbox.pack(fill='both',expand=True)
        self.tree=ttk.Treeview(listbox,columns=('name','new','title','comment','c2pa'),show='headings',selectmode='extended',height=10)
        for key,label,w in [('name','Dateiname',325),('new','Neuer Dateiname',325),('title','ID3-Titel',275),('comment','Kommentar',290),('c2pa','C2PA',60)]:
            self.tree.heading(key,text=label);self.tree.column(key,width=w,anchor='w')
        sy=ttk.Scrollbar(listbox,orient='vertical',command=self.tree.yview)
        sx=ttk.Scrollbar(listbox,orient='horizontal',command=self.tree.xview)
        self.tree.configure(yscrollcommand=sy.set,xscrollcommand=sx.set)
        self.tree.grid(row=0,column=0,sticky='nsew');sy.grid(row=0,column=1,sticky='ns');sx.grid(row=1,column=0,sticky='ew')
        listbox.rowconfigure(0,weight=1);listbox.columnconfigure(0,weight=1)
        self.tree.bind('<<TreeviewSelect>>',self.selected)
        modebar=ttk.Frame(files_tab);modebar.pack(fill='x',pady=3)
        ttk.Radiobutton(modebar,text='Nur markierte Dateien',variable=self.selection_mode,value='selected').pack(side='left')
        ttk.Radiobutton(modebar,text='Alle Dateien im Ordner',variable=self.selection_mode,value='all').pack(side='left',padx=14)
        ttk.Button(modebar,text='Alle markieren',command=self.select_all,style='Secondary.TButton').pack(side='left',padx=5)
        ttk.Button(modebar,text='▶ NUR DATEINAMEN UMBENENNEN',command=self.rename_only,style='Action.TButton').pack(side='left',padx=8)
        ttk.Button(modebar,text='▶ DATEINAMEN + ID3-TITEL BEREINIGEN',command=self.save,style='Action.TButton').pack(side='left',padx=5)
        ttk.Button(modebar,text='Metadaten der Auswahl öffnen',command=lambda:(self.load_one(),self.tabs.select(tags_tab)),style='Secondary.TButton').pack(side='left',padx=5)
        opts=ttk.LabelFrame(files_tab,text='Umbenennungsoptionen',padding=5);opts.pack(fill='x',pady=(3,0))
        for var,description in [
          (self.rename_on,'Zeitblöcke [0m00s-4m56s] entfernen'),
          (self.rename_number_suffix,'Nur runde Klammern um Endnummer entfernen: (1) → 1, (2) → 2'),
          (self.resolve_collisions,'Namenskollisionen sicher auflösen: Titel 1, Titel 2, ...')]:
            ttk.Checkbutton(opts,text=description,variable=var).pack(anchor='w')
        # Dedicated, always-visible metadata selection list; sync its selection back
        # to the common file table. There is no hidden per-tab target state.
        selected_panel=ttk.LabelFrame(tags_tab,text='ZIELDATEIEN · MP3-Auswahl für Cover und Metadaten',padding=5)
        selected_panel.pack(fill='x',pady=(0,4))
        ttk.Label(selected_panel,textvariable=self.cover_targets_text,foreground=NeonUI.CYAN,wraplength=1080).pack(anchor='w')
        self.metadata_list=tk.Listbox(selected_panel,height=4,selectmode=tk.EXTENDED,exportselection=False,
                                      bg='#16112c',fg='#edf7ff',selectbackground='#d92cae',selectforeground='white',
                                      highlightthickness=1,highlightbackground='#4bd7eb',relief='flat')
        self.metadata_list.pack(fill='x',pady=(3,2))
        self.metadata_list.bind('<<ListboxSelect>>',self.metadata_select)
        target_buttons=ttk.Frame(selected_panel);target_buttons.pack(fill='x')
        ttk.Button(target_buttons,text='▶ METADATEN STARTEN / SPEICHERN',command=self.save_metadata_only,style='Action.TButton').pack(side='right',padx=(8,0))
        ttk.Button(target_buttons,text='Alle MP3 verwenden',command=self.metadata_all).pack(side='left',padx=(0,8))
        ttk.Button(target_buttons,text='Nur markierte MP3 verwenden',command=self.metadata_marked).pack(side='left')
        ttk.Button(target_buttons,text='Cover-Ziele / Vorschau aktualisieren',command=self.refresh_metadata_targets).pack(side='left',padx=8)
        editor=ttk.LabelFrame(tags_tab,text='ID3-Editor – links Haken setzen, wenn das Feld geschrieben werden soll',padding=6)
        editor.pack(fill='both',expand=True)
        for idx,(code,label) in enumerate(FIELDS):
            row=idx//2; col=(idx%2)*3
            check=ttk.Checkbutton(editor,variable=self.flags[code])
            check.grid(row=row,column=col,sticky='w',padx=2,pady=6)
            ttk.Label(editor,text=label,width=17).grid(row=row,column=col+1,sticky='w',padx=2)
            entry=ttk.Entry(editor,textvariable=self.vars[code],width=37)
            entry.grid(row=row,column=col+2,sticky='ew',padx=3,pady=6)
            if code=='TIT2':
                self.title_entry=entry
                self.title_check=check
        editor.columnconfigure(2,weight=1);editor.columnconfigure(5,weight=1)
        tools=ttk.LabelFrame(tags_tab,text='Cover 512 × 512 JPEG / Titel-Synchronisierung',padding=7)
        tools.pack(fill='x',pady=(5,3))
        row=ttk.Frame(tools);row.pack(fill='x')
        ttk.Checkbutton(row,text='Cover einbetten/ersetzen',variable=self.cover_enable).pack(side='left')
        ttk.Button(row,text='Ein Cover für alle gewählten MP3',command=self.choose_cover_all).pack(side='left',padx=7)
        ttk.Button(row,text='Cover nur für markierte MP3',command=self.choose_cover_selected).pack(side='left',padx=7)
        ttk.Button(row,text='Cover-Zuweisungen löschen',command=self.clear_cover_choices).pack(side='left',padx=7)
        coverrow=ttk.Frame(tools);coverrow.pack(fill='x',pady=(4,1))
        self.cover_thumbnail=ttk.Label(coverrow,text='Kein Cover')
        self.cover_thumbnail.pack(side='left',padx=(0,8))
        options=ttk.Frame(coverrow);options.pack(side='left',fill='both',expand=True)
        ttk.Label(options,textvariable=self.cover_info).pack(anchor='w')
        ttk.Label(options,text='JPEG-Qualität (1–100; Standard 95)  ·  Ergebnis 512 × 512 Pixel').pack(anchor='w')
        ttk.Scale(options,from_=1,to=100,variable=self.cover_quality,orient='horizontal').pack(fill='x')
        ttk.Radiobutton(options,text='Ganzes Bild (Letterbox, keine Bildteile verlieren)',variable=self.cover_fit,value='contain').pack(anchor='w')
        ttk.Radiobutton(options,text='Quadratisch zuschneiden (zentriert)',variable=self.cover_fit,value='crop').pack(anchor='w')
        ttk.Radiobutton(options,text='Dehnen wie Windows-Hintergrund (16:9 → 512×512)',variable=self.cover_fit,value='stretch').pack(anchor='w')
        titles=ttk.Frame(tools);titles.pack(fill='x',pady=(5,0))
        ttk.Label(titles,text='Titelübernahme pro MP3:').pack(side='left',padx=(0,8))
        for value,label in [('none','Aus'),('file_to_tag','Dateiname → ID3-Titel'),('tag_to_file','ID3-Titel → Dateiname')]:
            ttk.Radiobutton(titles,text=label,variable=self.title_transfer,value=value).pack(side='left',padx=(0,9))
        self.title_transfer.trace_add('write',self.sync_title_controls)
        self.flags['TIT2'].trace_add('write',self.on_manual_title_flag)
        self.vars['TIT2'].trace_add('write',self.on_manual_title_value)
        self.sync_title_controls()
        ttk.Label(tools,text='Für jede MP3 getrennt. Änderungen erst über VORSCHAU → MIT SICHERUNG SPEICHERN. WAV nur umbenennbar.',foreground=NeonUI.CYAN).pack(anchor='w')
        ttk.Checkbutton(tags_tab,text='ID3-Titel bereinigen: Zeitblöcke [0m00s-4m56s] entfernen und (1) → 1',variable=self.clean_title).pack(anchor='w',pady=5)
        ttk.Checkbutton(tags_tab,text='C2PA-WARNUNG: Änderungen an geschützten Tags ausdrücklich erlauben',variable=self.c2pa_ok).pack(anchor='w',pady=5)
        ttk.Label(tags_tab,text='Die ID3-Felder werden nur geändert, wenn der jeweilige Haken aktiv ist; sonst bleiben sie unverändert.',wraplength=920).pack(anchor='w',pady=6)
        actionbar=ttk.Frame(tags_tab);actionbar.pack(fill='x',pady=(4,2))
        ttk.Label(actionbar,text='Nur MP3-Tags/Cover; Dateinamen bleiben unverändert.').pack(side='left',padx=10)
        ttk.Label(tags_tab,textvariable=self.label_metadata,foreground=NeonUI.CYAN).pack(anchor='w')
        ttk.Progressbar(tags_tab,variable=self.progress_metadata,maximum=100,style='Total.Horizontal.TProgressbar').pack(fill='x',pady=(1,4))
        for tab,kind in ((files_tab,'rename'),(tags_tab,'rename')):
            ttk.Button(tab,text='■ STOPP-VORGANG',command=lambda k=kind:self.stop_job(k)).pack(anchor='e',pady=(2,3))
        # Audio workspace: side-by-side controls and browser.
        # The file browser now owns the full usable vertical space; it no longer
        # receives only the leftover height after the fixed conversion panels.
        self.audio_split=ttk.Panedwindow(audio_tab,orient='horizontal')
        self.audio_split.pack(fill='both',expand=True,pady=(2,2))
        self.audio_left=ttk.Frame(self.audio_split)
        self.audio_right=ttk.Frame(self.audio_split)
        self.audio_split.add(self.audio_left,weight=1)
        self.audio_split.add(self.audio_right,weight=3)
        self.build_wav_panel(self.audio_left)
        self.audio_info=ttk.LabelFrame(self.audio_left,text='LIVE · Aktuelle Datei / Konvertierungsstatus',padding=6)
        self.audio_info.pack(fill='x',pady=(7,2))
        ttk.Label(self.audio_info,textvariable=self.current_file,wraplength=420).pack(fill='x',anchor='w')
        ttk.Progressbar(self.audio_info,variable=self.file_percent,maximum=100,style='Audio.Horizontal.TProgressbar').pack(fill='x',pady=4)
        ttk.Label(self.audio_info,textvariable=self.label_file).pack(anchor='w')
        ttk.Label(self.audio_info,textvariable=self.job_details,wraplength=420).pack(anchor='w',pady=2)
        self.build_audio_browser(self.audio_right)
        self.root.after(350,self.set_audio_split_initial_position)

        # Always-visible compact control surface, independent of active tab.
        progress=ttk.LabelFrame(wrapper,text='LIVE · PROZESSE UND FORTSCHRITT',padding=(8,5))
        progress.pack(fill='x',pady=(2,2))
        header=ttk.Frame(progress);header.pack(fill='x',pady=(0,3))
        ttk.Label(header,textvariable=self.current_file,style='Progress.TLabel').pack(side='left',fill='x',expand=True)
        ttk.Button(header,text='◫ MONITOR / 2. BILDSCHIRM',command=self.open_monitor,style='Secondary.TButton').pack(side='right')
        for label,var,textvar,style in [('UMBENENNUNG',self.progress_rename,self.label_rename,'Rename.Horizontal.TProgressbar'),
                                        ('METADATEN',self.progress_metadata,self.label_metadata,'Total.Horizontal.TProgressbar'),
                                        ('AUDIO CONVERT',self.progress_audio,self.label_audio,'Audio.Horizontal.TProgressbar'),
                                        ('GESAMT',self.progress_total,self.label_total,'Total.Horizontal.TProgressbar')]:
            rr=ttk.Frame(progress);rr.pack(fill='x',pady=1)
            ttk.Label(rr,text=label,width=17).pack(side='left')
            ttk.Progressbar(rr,variable=var,maximum=100,style=style).pack(side='left',fill='x',expand=True,padx=8)
            ttk.Label(rr,textvariable=textvar,width=30).pack(side='right')
        foot=ttk.Frame(wrapper);foot.pack(fill='x',pady=(2,1))
        ttk.Label(foot,textvariable=self.status).pack(side='left',fill='x',expand=True)
        ttk.Button(foot,text='VORSCHAU',command=self.preview,style='Secondary.TButton').pack(side='right',padx=4)
        self.save_button=ttk.Button(foot,text='MIT SICHERUNG SPEICHERN',command=self.save,style='Action.TButton')
        self.save_button.pack(side='right',padx=4)
        root.title('L.Y.V.R.A. - MP3 MANAGER v2.36 · PORTABLE QC')
        root.geometry('1360x900');root.minsize(820,600)
        # WICHTIG: Footer und Fortschritt von unten reservieren, bevor der
        # Notebook-Bereich den verbleibenden Platz bekommt. Dies gilt in ALLEN Reitern.
        self.tabs.pack_forget()
        progress.pack_forget()
        foot.pack_forget()
        foot.pack(side='bottom',fill='x',pady=(1,0))
        progress.pack(side='bottom',fill='x',pady=(2,2))
        self.tabs.pack(side='top',fill='both',expand=True,pady=(2,3))
        self.root.after(120, self.start_maximized)
        self._layout_last_height=0
        self.root.bind('<Configure>',self.autoreflow,add='+')

    def autoreflow(self,event=None):
        """Automatische Reorganisation bei Windows-Maximierung, Auflösung und DPI-Wechsel."""
        if event is not None and event.widget is not self.root:return
        h=self.root.winfo_height()
        if abs(h-self._layout_last_height)<24:return
        self._layout_last_height=h
        if hasattr(self,'artwork'):
            self.artwork.host.after_idle(self.artwork.render)
        if hasattr(self,'audio_split'):
            self.root.after_idle(self.set_audio_split_initial_position)

    def open_help(self):
        win=tk.Toplevel(self.root)
        win.title('L.Y.V.R.A. - MP3 MANAGER · '+('Help / Manual' if self.lang.get()=='EN' else 'Hilfe / Bedienungsanleitung'))
        win.geometry('830x620');win.minsize(530,350)
        win.configure(bg=NeonUI.BG)
        frame=ttk.Frame(win,padding=10);frame.pack(fill='both',expand=True)
        text=tk.Text(frame,bg='#070c1b',fg='#e9e4ff',insertbackground='#2cecff',wrap='word',font=('Segoe UI',11))
        scroll=ttk.Scrollbar(frame,command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right',fill='y');text.pack(side='left',fill='both',expand=True)
        base=Path(getattr(__import__('sys'),'_MEIPASS',Path(__file__).resolve().parent))
        name='MANUAL_EN.md' if self.lang.get()=='EN' else 'BEDIENUNGSANLEITUNG_DE.md'
        try: content=(base/name).read_text(encoding='utf8')
        except OSError: content='Manual not found / Anleitung fehlt: '+name
        text.insert('1.0',content);text.configure(state='disabled')

    def apply_language(self):
        """Schaltet beschriftete GUI-Elemente zwischen Deutsch und Englisch um.
        Benutzerinhalte (Titel, Dateinamen und Metadaten) werden nie übersetzt.
        """
        translations={
         '01  DATEIEN & UMBENENNEN':'01  FILES & RENAME',
         '02  METADATEN':'02  METADATA',
         '03  AUDIO CONVERT':'03  AUDIO CONVERT',
         '04  AUDIO LABS':'04  AUDIO LABS',
         'AUDIO LABS · REMASTER & RESTAURATION':'AUDIO LABS · REMASTER & RESTORE',
         'Suno Song Remaster':'Suno Song Remaster',
         'Restoration Lab':'Restoration Lab',
         '▶ REMASTER STARTEN':'▶ START REMASTER',
         '▶ RESTORATION STARTEN':'▶ START RESTORATION',
         'MP3-Remastering, LUFS/True-Peak-Ziele und Stapelverarbeitung.':'MP3 remastering, LUFS/true-peak targets, and batch processing.',
         'Rauschminderung, A/B-Wiedergabe und WAV-Export.':'Noise reduction, A/B playback, and WAV export.',
         'Starten':'Launch',
         'Apps laufen in einem eigenen Fenster. Der Manager installiert keine zusätzlichen Pakete automatisch.':'Apps run in a separate window. The manager does not install additional packages automatically.',
         'Audio-Tools bereit.':'Audio tools ready.',
         'Ordner wählen':'Choose folder','Ordner prüfen':'Scan folder','CSV exportieren':'Export CSV',
         'Nur markierte Dateien':'Selected files only','Alle Dateien im Ordner':'All files in folder',
         'Alle markieren':'Select all','▶ NUR DATEINAMEN UMBENENNEN':'▶ RENAME FILES ONLY',
         '▶ DATEINAMEN + ID3-TITEL BEREINIGEN':'▶ CLEAN FILENAMES + ID3 TITLES',
         '▶ METADATEN STARTEN / SPEICHERN':'▶ START / SAVE METADATA',
         '■ STOPP-VORGANG':'■ STOP JOB','■ STOPP-VORGANG (AUDIO)':'■ STOP AUDIO',
         'Metadaten der Auswahl öffnen':'Edit selected metadata',
         'Umbenennungsoptionen':'Rename options','System prüfen':'Check system',
         'MIT SICHERUNG SPEICHERN':'SAVE WITH BACKUP','VORSCHAU':'PREVIEW',
         '◫ MONITOR / 2. BILDSCHIRM':'◫ MONITOR / SCREEN 2',
         '▣ DATEIMANAGER / 2. BILDSCHIRM':'▣ FILE MANAGER / SCREEN 2',
         'BESTAND AKTUALISIEREN':'REFRESH COUNTS',
         'Ein Cover für alle gewählten MP3':'One cover for selected MP3s',
         'Cover nur für markierte MP3':'Cover for marked MP3s only',
         'Cover-Zuweisungen löschen':'Clear cover assignments',
         'Cover einbetten/ersetzen':'Embed / replace cover',
         'Quadratisch zuschneiden (zentriert)':'Crop square (centered)',
         'Ganzes Bild (Letterbox, keine Bildteile verlieren)':'Fit whole image (letterbox)',
         'Dehnen wie Windows-Hintergrund (16:9 → 512×512)':'Stretch like Windows wallpaper (16:9 → 512×512)',
         'Nur MP3-Tags/Cover; Dateinamen bleiben unverändert.':'MP3 tags / cover only; filenames unchanged.',
         'Titelübernahme pro MP3:':'Title transfer per MP3:',
         'Dateiname → ID3-Titel':'Filename → ID3 title','ID3-Titel → Dateiname':'ID3 title → filename',
         'Aus':'Off', 'System-Check und Portable-EXE':'System check & portable EXE',
         'EXE-Build ausschließlich extern: BUILD_PORTABLE_EXE.bat':'EXE build external only: BUILD_PORTABLE_EXE.bat',
         'LIVE · PROZESSE UND FORTSCHRITT':'LIVE · PROCESS PROGRESS',
         'GESAMT':'TOTAL','UMBENENNUNG':'RENAMING',
         'Dateiname':'Filename','Neuer Dateiname':'New filename','Kommentar':'Comment',
         'Songtitel':'Song title',
        }
        inv={v:k for k,v in translations.items()}
        to_en=self.lang.get()=='EN'
        def visit(w):
            try:
                old=w.cget('text')
                new=translations.get(old,old) if to_en else inv.get(old,old)
                if new!=old:w.configure(text=new)
            except (tk.TclError,AttributeError,KeyError):pass
            for child in w.winfo_children():visit(child)
        visit(self.root)
        for index in range(self.tabs.index('end')):
            label=self.tabs.tab(index,'text')
            new=translations.get(label,label) if to_en else inv.get(label,label)
            if new!=label:self.tabs.tab(index,text=new)
        if hasattr(self,'tree'):
            for column in self.tree['columns']:
                title=self.tree.heading(column)['text']
                self.tree.heading(column,text=(translations.get(title,title) if to_en else inv.get(title,title)))
        self.root.title('L.Y.V.R.A. - MP3 MANAGER v2.36 · '+('NEON WORKSPACE' if to_en else 'NEON ARBEITSBEREICH'))

    def register_drop_targets(self):
        """Windows-Explorer-Drop für alle Reiter; optionales TkinterDnD2 erforderlich."""
        if DND_FILES is None:
            self.status.set('Drag & Drop benötigt tkinterdnd2 (Systemcheck/requirements); Dateimanager funktioniert weiterhin.')
            return
        for widget in self.drop_widgets:
            try:
                widget.drop_target_register(DND_FILES)
                widget.dnd_bind('<<Drop>>', self.handle_drop)
            except (tk.TclError, AttributeError):
                pass

    def handle_drop(self, event):
        try:
            paths=[Path(x) for x in self.root.tk.splitlist(event.data)]
            self.accept_paths(paths)
        except Exception as exc:
            self.status.set(f'Drag & Drop konnte nicht gelesen werden: {exc}')

    def accept_paths(self,paths):
        """Importiert Auswahl konservativ: keine Audiodateien verschieben/löschen."""
        paths=[Path(p) for p in paths if Path(p).exists()]
        folders=[p for p in paths if p.is_dir()]
        audio=[p for p in paths if p.is_file() and p.suffix.lower() in ('.mp3','.wav')]
        pictures=[p for p in paths if p.is_file() and p.suffix.lower() in ('.jpg','.jpeg','.png','.webp','.bmp','.gif','.tif','.tiff','.ico')]
        if folders:
            folder=folders[0]
        elif audio:
            folder=audio[0].parent
        else:
            folder=None
        if folder:
            self.folder.set(str(folder));self.wav_folder.set(str(folder));self.fm_folder.set(str(folder))
            self.scan();self.update_audio_counts()
            if audio:
                wanted={str(p.resolve()) for p in audio}
                matches=[item for item,(path,_) in self.files.items() if str(path.resolve()) in wanted]
                if matches:
                    self.tree.selection_set(matches)
                    self.selection_mode.set('selected')
            self.status.set(f'Importiert: Ordner {folder.name} · {len(audio)} Audiodatei(en) ausgewählt')
        if pictures:
            self.show_cover_preview(str(pictures[0]))
            self.cover_global.set(str(pictures[0]));self.cover_enable.set(True)
            self.status.set(f'Cover vorbereitet: {pictures[0].name} (noch nicht geschrieben)')
        if not (folder or pictures):
            self.status.set('Drop ignoriert: Bitte MP3, WAV, Bild oder Ordner verwenden.')
        if self.file_manager and self.file_manager.winfo_exists():
            self.fm_refresh()

    def open_file_manager(self):
        """Eigenständiger, auf Monitor 2 verschiebbarer Explorer; keine Datenmutation."""
        if self.file_manager and self.file_manager.winfo_exists():
            self.file_manager.deiconify();self.file_manager.lift();return
        win=tk.Toplevel(self.root);self.file_manager=win
        win.title('L.Y.V.R.A. - DATEIMANAGER · 2. BILDSCHIRM')
        win.geometry('790x600');win.minsize(570,400)
        try:win.iconbitmap(str(Path(__file__).resolve().parent/'assets'/'app.ico'))
        except (tk.TclError,OSError):pass
        if not self.fm_folder.get():self.fm_folder.set(self.folder.get() or str(Path.home()))
        bar=ttk.Frame(win,padding=7);bar.pack(fill='x')
        ttk.Entry(bar,textvariable=self.fm_folder).pack(side='left',fill='x',expand=True)
        ttk.Button(bar,text='Ordner...',command=self.fm_choose).pack(side='left',padx=4)
        ttk.Button(bar,text='Aktualisieren',command=self.fm_refresh).pack(side='left')
        ttk.Button(bar,text='↥ Übernehmen',command=self.fm_take_selected,style='Action.TButton').pack(side='left',padx=4)
        tools=ttk.Frame(win,padding=(7,1));tools.pack(fill='x')
        ttk.Label(tools,text='Doppelklick öffnet Ordner; Mehrfachauswahl mit Strg/Shift. Dateiübernahme ändert keine Quelldateien.',foreground=NeonUI.CYAN).pack(anchor='w')
        area=ttk.Frame(win,padding=5);area.pack(fill='both',expand=True)
        self.fm_tree=ttk.Treeview(area,columns=('type','size'),show='tree headings',selectmode='extended')
        self.fm_tree.heading('#0',text='Datei / Verzeichnis');self.fm_tree.column('#0',width=450)
        self.fm_tree.heading('type',text='Format');self.fm_tree.column('type',width=90)
        self.fm_tree.heading('size',text='Größe');self.fm_tree.column('size',width=120,anchor='e')
        sy=ttk.Scrollbar(area,orient='vertical',command=self.fm_tree.yview)
        self.fm_tree.configure(yscrollcommand=sy.set)
        self.fm_tree.pack(side='left',fill='both',expand=True);sy.pack(side='right',fill='y')
        self.fm_tree.bind('<Double-1>',self.fm_open_selected)
        self.fm_tree.bind('<Return>',self.fm_open_selected)
        ttk.Label(win,textvariable=self.fm_status,padding=(8,5)).pack(fill='x')
        self.drop_widgets.append(self.fm_tree)
        if DND_FILES is not None:
            try:
                for w in (win,self.fm_tree):
                    w.drop_target_register(DND_FILES);w.dnd_bind('<<Drop>>',self.handle_drop)
            except (tk.TclError,AttributeError):pass
        win.protocol('WM_DELETE_WINDOW',win.destroy)
        self.fm_refresh()

    def fm_choose(self):
        path=filedialog.askdirectory(parent=self.file_manager,title='Ordner anzeigen')
        if path:self.fm_folder.set(path);self.fm_refresh()

    def fm_refresh(self):
        if not self.file_manager or not self.file_manager.winfo_exists():return
        tree=self.fm_tree
        tree.delete(*tree.get_children())
        folder=Path(self.fm_folder.get())
        if not folder.is_dir():self.fm_status.set('Ordner nicht vorhanden');return
        try:
            children=sorted(folder.iterdir(),key=lambda p:(not p.is_dir(),p.name.casefold()))
            parent=folder.parent
            if parent!=folder:tree.insert('',tk.END,iid=str(parent),text='[..] Übergeordneter Ordner',values=('ORDNER',''))
            for p in children:
                try:
                    kind='ORDNER' if p.is_dir() else p.suffix.upper().lstrip('.') or 'DATEI'
                    size='' if p.is_dir() else f'{p.stat().st_size/1024/1024:.2f} MB'
                    tree.insert('',tk.END,iid=str(p),text=p.name,values=(kind,size))
                except OSError:pass
            self.fm_status.set(f'{len(children)} Einträge · {folder}')
        except OSError as exc:self.fm_status.set(f'Zugriff fehlgeschlagen: {exc}')

    def fm_open_selected(self,event=None):
        items=self.fm_tree.selection()
        if not items:return
        p=Path(items[0])
        if p.is_dir():self.fm_folder.set(str(p));self.fm_refresh()
        else:self.fm_take_selected()

    def fm_take_selected(self):
        items=[Path(item) for item in self.fm_tree.selection()]
        if not items:
            folder=Path(self.fm_folder.get())
            if folder.is_dir():items=[folder]
        self.accept_paths(items)

    def stop_job(self,kind):
        """Abbruchanforderung; Originale und abgeschlossene Ergebnisse bleiben erhalten."""
        if kind=='rename':
            if not self.busy_rename:
                self.job_details.set('Umbenennung / ID3: kein laufender Vorgang')
                return
            self.cancel_rename=True
            self.job_details.set('STOPP ANGEFORDERT · Umbenennung endet nach aktueller Datei')
        elif kind in ('audio','build'):
            busy=self.convert_busy if kind=='audio' else self.build_busy
            if not busy:
                self.job_details.set('Kein laufender '+('Audio' if kind=='audio' else 'Build')+'-Vorgang')
                return
            (self.cancel_audio if kind=='audio' else self.cancel_build).set()
            self.job_details.set('STOPP ANGEFORDERT · '+kind.upper())
            with self.process_lock:
                proc=self.active_process
            if proc is not None and proc.poll() is None:
                try: proc.terminate()
                except (OSError,ProcessLookupError): pass
        else:
            self.job_details.set('Kein unterstützter Vorgang')

    def run_interruptible(self,cmd,cancel_event,**kwargs):
        """Unterbrechbarer externer Prozess; keine Änderung an Quelldateien."""
        if cancel_event.is_set():raise InterruptedError('Abgebrochen')
        kwargs.setdefault('stdout',subprocess.PIPE)
        kwargs.setdefault('stderr',subprocess.PIPE)
        kwargs.setdefault('text',True)
        kwargs.setdefault('encoding','utf-8')
        kwargs.setdefault('errors','replace')
        kwargs.setdefault('creationflags',getattr(subprocess,'CREATE_NO_WINDOW',0))
        proc=subprocess.Popen(cmd,**kwargs)
        with self.process_lock:self.active_process=proc
        try:
            while True:
                try:stdout,stderr=proc.communicate(timeout=0.25);break
                except subprocess.TimeoutExpired:
                    if cancel_event.is_set():
                        proc.terminate()
                        try:proc.communicate(timeout=3)
                        except subprocess.TimeoutExpired:proc.kill();proc.communicate()
                        raise InterruptedError('Abgebrochen')
            if cancel_event.is_set():raise InterruptedError('Abgebrochen')
            return subprocess.CompletedProcess(cmd,proc.returncode,stdout,stderr)
        finally:
            with self.process_lock:
                if self.active_process is proc:self.active_process=None

    def start_maximized(self):
        try:
            self.root.state('zoomed')
            return
        except tk.TclError:
            pass
        try:
            w=self.root.winfo_screenwidth(); h=self.root.winfo_screenheight()
            self.root.geometry(f"{max(980,w)}x{max(680,h)}+0+0")
        except Exception:
            pass

    def open_monitor(self):
        """Unabhängiges verschiebbares Fenster mit denselben Tk-Statusvariablen."""
        if self.monitor and self.monitor.winfo_exists():
            self.monitor.deiconify();self.monitor.lift();return
        win=tk.Toplevel(self.root);self.monitor=win
        win.title('L.Y.V.R.A. - MP3 MANAGER · LIVE STATUSMONITOR')
        win.geometry('560x360');win.minsize(420,280)
        win.configure(bg=NeonUI.BG)
        try: win.iconbitmap(str(Path(__file__).resolve().parent/'assets'/'app.ico'))
        except (tk.TclError,OSError):pass
        ttk.Label(win,text='L.Y.V.R.A. - LIVE STATUSMONITOR  •  666SOUNDsDESIGn',foreground=NeonUI.CYAN,font=('Segoe UI Semibold',13)).pack(anchor='w',padx=12,pady=(13,7))
        ttk.Label(win,textvariable=self.current_file,wraplength=510).pack(anchor='w',padx=12)
        ttk.Progressbar(win,variable=self.file_percent,maximum=100,style='Audio.Horizontal.TProgressbar').pack(fill='x',padx=12,pady=(5,0))
        ttk.Label(win,textvariable=self.label_file).pack(anchor='e',padx=12)
        for name,v,t,style in [('UMBENENNUNG',self.progress_rename,self.label_rename,'Rename.Horizontal.TProgressbar'),
                                        ('METADATEN',self.progress_metadata,self.label_metadata,'Total.Horizontal.TProgressbar'),('KONVERTIERUNG',self.progress_audio,self.label_audio,'Audio.Horizontal.TProgressbar'),('GESAMT',self.progress_total,self.label_total,'Total.Horizontal.TProgressbar')]:
            ttk.Label(win,text=name,foreground=NeonUI.PINK).pack(anchor='w',padx=12,pady=(5,0))
            ttk.Progressbar(win,variable=v,maximum=100,style=style).pack(fill='x',padx=12)
            ttk.Label(win,textvariable=t).pack(anchor='e',padx=12)
        ttk.Label(win,textvariable=self.job_details,wraplength=520).pack(fill='x',padx=12,pady=7)
        win.protocol('WM_DELETE_WINDOW',win.destroy)

    def rename_only(self):
        """Nur Dateinamen ändern; niemals versehentlich ID3-Felder anfassen."""
        if self.busy_rename or self.convert_busy:return
        plans=list(self.plans())
        changes=[(p,t,issue) for p,t,old,desired,issue in plans if p!=t]
        if not changes:
            messagebox.showinfo('Umbenennen','Keine Umbenennungen geplant. Dateien markieren / Alle auswählen und Zeitblock-Option prüfen.');return
        if not messagebox.askyesno('Nur Dateinamen umbenennen',f'{len(changes)} MP3/WAV-Dateinamen ändern?\nID3-Metadaten bleiben bei diesem Vorgang vollständig unverändert.\nKollisionen werden nicht überschrieben.'):
            return
        self.cancel_rename=False
        self.busy_rename=True
        self.job_details.set('Umbenennung läuft · ID3 bleibt unverändert')
        self.progress_update('rename',0,0,len(changes),'Umbenennen')
        success=0;errors=[];backup=Path(self.folder.get())/('_666MP3_BACKUP_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
        for i,(src,target,issue) in enumerate(changes,1):
            self.root.update()
            if self.cancel_rename:break
            self.current_file.set(src.name)
            try:
                if issue:raise RuntimeError(issue)
                if not src.is_file():raise RuntimeError('Quelldatei fehlt')
                if target.exists():raise RuntimeError('Ziel bereits vorhanden')
                backup.mkdir(exist_ok=True)
                shutil.copy2(src,backup/src.name)
                src.rename(target);success+=1
            except Exception as exc:errors.append(f'{src.name}: {exc}')
            self.progress_update('rename',100*i/len(changes),i,len(changes),'Umbenennen')
            self.root.update_idletasks()
        self.busy_rename=False
        self.job_details.set(f'Umbenennung {"GESTOPPT" if self.cancel_rename else "abgeschlossen"} · {success} erfolgreich / {len(errors)} übersprungen')
        self.current_file.set('Umbenennung gestoppt' if self.cancel_rename else 'Umbenennung abgeschlossen')
        self.scan()
        msg=f'{success} erfolgreich, {len(errors)} übersprungen.\nSicherung: {backup if backup.exists() else "keine"}'
        if errors:msg+='\n\n'+'\n'.join(errors[:10])
        messagebox.showinfo('Umbenennung gestoppt' if self.cancel_rename else 'Umbenennung abgeschlossen',msg)

    def audio_progress(self,i,n,fraction,name,phase):
        fraction=max(0,min(1,float(fraction)))
        self.current_file.set(f'Datei {i}/{n}: {name} · {phase}')
        self.file_percent.set(100*fraction)
        self.label_file.set(f'Einzeldatei: {100*fraction:.1f} %')
        self.job_details.set(f'{phase} · Track {i}/{n} · {n-i} weitere Dateien nach diesem Track')
        self.progress_update('audio',100*((i-1)+fraction)/n,i-1,n,phase)

    def progress_update(self,kind,percent,done,total,detail=''):
        """Nur auf dem Tk-Hauptthread aufrufen."""
        value=max(0,min(100,float(percent)))
        if kind=='rename':
            self.progress_rename.set(value)
            self.label_rename.set(f'{done} / {total} · {value:.0f} %')
        elif kind=='metadata':
            self.progress_metadata.set(value)
            self.label_metadata.set(f'{done} / {total} · {value:.0f} % · {detail[:35]}')
        elif kind=='audio':
            self.progress_audio.set(value)
            self.label_audio.set(f'{done} / {total} · {value:.0f} %')
        self.progress_total.set(value)
        self.label_total.set(f'{value:.0f} % · {detail[:22]}')

    def wheel(self,event):
        # Leave the file grid's own scrollbar independent.
        try: self.scroll.yview_scroll(-int(event.delta/120),'units')
        except (tk.TclError,ZeroDivisionError): pass

    def set_audio_split_initial_position(self):
        """Prefer a large browser; user can still drag the divider."""
        try:
            width=self.audio_split.winfo_width()
            if width>850:
                self.audio_split.sashpos(0,max(405,min(520,int(width*0.32))))
        except (tk.TclError,AttributeError):
            pass

    def build_audio_browser(self,parent):
        """Integrierter Audio-Browser; nur ausgewählte Zeilen werden konvertiert."""
        self.audio_filter=tk.StringVar(value='')
        self.audio_selected_count=tk.StringVar(value='Auswahl: 0 · WAV: 0 · MP3: 0')
        self.audio_detail_status=tk.StringVar(value='Audiodatei auswählen, um ID3-Details anzuzeigen.')
        outer=ttk.LabelFrame(parent,text='DATEI-BROWSER · WAV + MP3 · Explorer Drag & Drop',padding=6)
        outer.pack(fill='both',expand=True,pady=(0,2))
        actions=ttk.Frame(outer);actions.pack(fill='x',pady=(0,4))
        ttk.Label(actions,textvariable=self.audio_selected_count,foreground=NeonUI.CYAN).pack(side='left',padx=(0,12))
        ttk.Button(actions,text='Alle auswählen',command=self.audio_select_all).pack(side='left',padx=3)
        ttk.Button(actions,text='Auswahl aufheben',command=self.audio_select_none).pack(side='left',padx=3)
        ttk.Button(actions,text='Auswahl aktualisieren',command=self.refresh_audio_browser).pack(side='left',padx=3)
        ttk.Label(actions,text='Filter:').pack(side='left',padx=(14,3))
        entry=ttk.Entry(actions,textvariable=self.audio_filter,width=24)
        entry.pack(side='left',fill='x',expand=True)
        self.audio_filter.trace_add('write',lambda *_:self.refresh_audio_browser())
        self.audio_browser_tabs=ttk.Notebook(outer)
        self.audio_browser_tabs.pack(fill='both',expand=True)
        browsing=ttk.Frame(self.audio_browser_tabs)
        inspection=ttk.Frame(self.audio_browser_tabs)
        self.audio_browser_tabs.add(browsing,text='DATEIEN / AUSWAHL')
        self.audio_browser_tabs.add(inspection,text='METADATEN / DETAILS')
        listing=ttk.Frame(browsing);listing.pack(fill='both',expand=True)
        cols=('format','name','duration','size','title','artist')
        self.audio_tree=ttk.Treeview(listing,columns=cols,show='headings',selectmode='extended',height=10)
        for col,label,width in [('format','Typ',56),('name','Dateiname',380),('duration','Dauer',80),('size','MB',75),('title','ID3-Titel',320),('artist','Interpret',210)]:
            self.audio_tree.heading(col,text=label);self.audio_tree.column(col,width=width,anchor='w',stretch=(col in ('name','title','artist')))
        sy=ttk.Scrollbar(listing,orient='vertical',command=self.audio_tree.yview)
        sx=ttk.Scrollbar(listing,orient='horizontal',command=self.audio_tree.xview)
        self.audio_tree.configure(yscrollcommand=sy.set,xscrollcommand=sx.set)
        self.audio_tree.grid(row=0,column=0,sticky='nsew');sy.grid(row=0,column=1,sticky='ns');sx.grid(row=1,column=0,sticky='ew')
        listing.rowconfigure(0,weight=1);listing.columnconfigure(0,weight=1)
        self.audio_tree.bind('<<TreeviewSelect>>',self.on_audio_selection)
        self.audio_tree.bind('<Double-1>',lambda e:self.audio_browser_tabs.select(inspection))
        ttk.Label(inspection,textvariable=self.audio_detail_status,foreground=NeonUI.CYAN).pack(anchor='w',pady=4)
        dt=ttk.Frame(inspection);dt.pack(fill='both',expand=True)
        self.audio_meta_tree=ttk.Treeview(dt,columns=('field','value'),show='headings',height=9)
        self.audio_meta_tree.heading('field',text='Metadaten-Feld');self.audio_meta_tree.heading('value',text='Wert')
        self.audio_meta_tree.column('field',width=190,stretch=False);self.audio_meta_tree.column('value',width=780)
        ds=ttk.Scrollbar(dt,orient='vertical',command=self.audio_meta_tree.yview)
        self.audio_meta_tree.configure(yscrollcommand=ds.set)
        self.audio_meta_tree.pack(side='left',fill='both',expand=True);ds.pack(side='right',fill='y')
        self.audio_paths={}
        self.wav_folder.trace_add('write',self.audio_folder_changed)
        self.input_kind.trace_add('write',lambda *_:self.root.after_idle(self.refresh_audio_browser))
        if DND_FILES:
            for widget in (outer,self.audio_tree, self.audio_meta_tree, entry):
                try:
                    widget.drop_target_register(DND_FILES)
                    widget.dnd_bind('<<Drop>>',self.audio_drop)
                except (tk.TclError,AttributeError):pass
        self.refresh_audio_browser()

    def audio_folder_changed(self,*_):
        self.audio_selection_initialized=False
        self.root.after_idle(self.refresh_audio_browser)

    def audio_drop(self,event):
        try:
            paths=[Path(v) for v in self.root.tk.splitlist(event.data)]
            audio=[v for v in paths if v.is_file() and v.suffix.lower() in ('.mp3','.wav')]
            dirs=[v for v in paths if v.is_dir()]
            folder=dirs[0] if dirs else (audio[0].parent if audio else None)
            if folder:
                self.wav_folder.set(str(folder));self.folder.set(str(folder))
                self.refresh_audio_browser()
                wanted={str(x.resolve()).casefold() for x in audio}
                if wanted:
                    def apply_drop_selection():
                        picks=[id for id,path in self.audio_paths.items() if str(path.resolve()).casefold() in wanted]
                        self.audio_tree.selection_set(picks)
                        self.on_audio_selection()
                    self.root.after_idle(apply_drop_selection)
            else:
                self.status.set('Drop: WAV/MP3-Dateien oder Ordner erwartet.')
        except Exception as exc:self.status.set(f'Audio Drag & Drop: {exc}')

    def refresh_audio_browser(self):
        if not hasattr(self,'audio_tree'):return
        selected={str(self.audio_paths[x]) for x in self.audio_tree.selection() if x in self.audio_paths}
        self.audio_tree.delete(*self.audio_tree.get_children());self.audio_paths={}
        folder=Path(self.wav_folder.get())
        kind=self.input_kind.get()
        accepted={'.wav','.mp3'} if kind=='mixed' else {'.'+kind}
        term=self.audio_filter.get().casefold().strip()
        try:files=sorted((x for x in folder.iterdir() if x.is_file() and x.suffix.lower() in accepted and term in x.name.casefold()),key=lambda x:x.name.casefold()) if folder.is_dir() else []
        except OSError:files=[]
        for i,path in enumerate(files):
            title=artist='';duration='—'
            if path.suffix.lower()=='.mp3':
                try:
                    tags=read_tags(path);title=tags.get('TIT2','');artist=tags.get('TPE1','')
                except Exception:pass
            row=self.audio_tree.insert('','end',values=(path.suffix[1:].upper(),path.name,duration,f'{path.stat().st_size/1048576:.1f}',title,artist))
            self.audio_paths[row]=path
        # Ordner-/Formatwechsel: alte Auswahl nicht übernehmen, neue Dateien direkt auswählbar.
        # Bei reinem Refresh bleibt dagegen eine absichtlich leere Auswahl leer.
        selection_context=(str(folder.resolve()) if folder.is_dir() else str(folder), kind)
        changed=selection_context != getattr(self,'audio_selection_context',None)
        self.audio_selection_context=selection_context
        if changed or not getattr(self,'audio_selection_initialized',False):
            self.audio_tree.selection_set(list(self.audio_paths))
        elif selected:
            self.audio_tree.selection_set([row for row,path in self.audio_paths.items() if str(path) in selected])
        self.audio_selection_initialized=True
        self.on_audio_selection()

    def audio_select_all(self):
        self.audio_tree.selection_set(list(self.audio_paths));self.on_audio_selection()

    def audio_select_none(self):
        self.audio_tree.selection_remove(self.audio_tree.selection());self.on_audio_selection()

    def on_audio_selection(self,event=None):
        if not hasattr(self,'audio_tree'):return
        selected=[self.audio_paths[k] for k in self.audio_tree.selection() if k in self.audio_paths]
        wav=sum(p.suffix.lower()=='.wav' for p in selected)
        self.audio_selected_count.set(f'AUSGEWÄHLT: {len(selected)} / {len(self.audio_paths)} · WAV: {wav} · MP3: {len(selected)-wav}')
        self.audio_meta_tree.delete(*self.audio_meta_tree.get_children())
        if len(selected)==1:
            p=selected[0]
            self.audio_detail_status.set(f'Metadaten: {p.name}')
            for field,value in [('Dateiname',p.name),('Format',p.suffix.lower()),('Größe (Bytes)',p.stat().st_size)]:
                self.audio_meta_tree.insert('','end',values=(field,value))
            if p.suffix.lower()=='.mp3':
                try:
                    for field,value in read_tags(p).items():self.audio_meta_tree.insert('','end',values=(field,str(value)))
                except Exception as exc:self.audio_meta_tree.insert('','end',values=('Fehler',str(exc)))
            else:self.audio_meta_tree.insert('','end',values=('WAV','Keine ID3-MP3-Tags; Quelle bleibt unverändert'))
        elif selected:self.audio_detail_status.set(f'{len(selected)} Titel ausgewählt – für einzelne Metadaten genau eine Datei auswählen.')
        else:self.audio_detail_status.set('Keine Dateien markiert. Wähle einzelne oder alle Dateien aus.')

    def build_wav_panel(self, parent):
        panel=ttk.LabelFrame(parent,text='WAV oder MP3 → MP3 | getrennte Ausgabe | FFmpeg erforderlich',padding=8)
        panel.pack(fill='x',pady=(8,0))
        self.wav_folder=tk.StringVar()
        self.audio_counts=tk.StringVar(value='QUELLE: 0 Dateien  |  WAV: 0  |  MP3: 0')
        self.input_kind=tk.StringVar(value='wav')
        self.sample_rate=tk.StringVar(value='48000')
        self.bitrate=tk.StringVar(value='320')
        self.pcm_format=tk.StringVar(value='fltp')
        self.channels=tk.StringVar(value='stereo')
        self.normalize=tk.BooleanVar(value=False)
        self.audio_qc=tk.BooleanVar(value=True)
        self.lufs=tk.StringVar(value='-14')
        self.true_peak=tk.StringVar(value='-2.0')
        self.quality_preset=tk.StringVar(value='maximum')
        self.wav_status=tk.StringVar(value='Konvertierung schreibt ausschließlich in _666MP3_EXPORT. WAV bleibt unverändert.')
        self.convert_busy=False
        a=ttk.Frame(panel);a.pack(fill='x')
        ttk.Entry(a,textvariable=self.wav_folder).pack(side='left',fill='x',expand=True)
        ttk.Button(a,text='Ordner…',command=self.choose_wav).pack(side='left',padx=4)
        ttk.Radiobutton(a,text='WAV',variable=self.input_kind,value='wav').pack(side='left')
        ttk.Radiobutton(a,text='MP3',variable=self.input_kind,value='mp3').pack(side='left')
        ttk.Radiobutton(a,text='Mix',variable=self.input_kind,value='mixed').pack(side='left',padx=8)
        ttk.Label(panel,textvariable=self.audio_counts,foreground=NeonUI.CYAN).pack(anchor='w',pady=(3,0))
        presets=ttk.Frame(panel);presets.pack(fill='x',pady=(3,2))
        ttk.Label(presets,text='MP3 Qualitäts-Preset:',foreground=NeonUI.CYAN).pack(side='left',padx=(2,8))
        preset_select=ttk.Combobox(presets,textvariable=self.quality_preset,state='readonly',width=20,
            values=('maximum','balanced','original'))
        preset_select.pack(side='left')
        ttk.Button(presets,text='PRESET ANWENDEN',command=self.apply_quality_preset).pack(side='left',padx=6)
        ttk.Label(presets,text='Maximum Quality | Balanced Radio | Original Preserve').pack(side='left',padx=4)
        self.wav_folder.trace_add('write',lambda *_:self.update_audio_counts())
        self.input_kind.trace_add('write',lambda *_:self.update_audio_counts())
        b=ttk.Frame(panel);b.pack(fill='x',pady=3)
        for label,var,values in [('Hz',self.sample_rate,['44100','48000']),('kbit/s',self.bitrate,['128','160','192','224','256','320']),('PCM Zwischenformat',self.pcm_format,['s16p','s16','s32p','fltp']),('Kanäle',self.channels,['stereo','mono'])]:
            row=ttk.Frame(b);row.pack(fill='x',pady=1)
            ttk.Label(row,text=label,width=20).pack(side='left',padx=(3,2))
            ttk.Combobox(row,textvariable=var,values=values,width=12,state='readonly').pack(side='left')
        c=ttk.Frame(panel);c.pack(fill='x',pady=3)
        ttk.Checkbutton(c,text='Lautheit (2-Pass EBU R128)',variable=self.normalize).pack(anchor='w')
        ttk.Checkbutton(c,text='Audio-QC nach Export: ganze MP3 dekodieren + Dauer prüfen (empfohlen)',variable=self.audio_qc).pack(anchor='w')
        levels=ttk.Frame(c);levels.pack(fill='x',pady=3)
        ttk.Label(levels,text='LUFS').pack(side='left',padx=(2,3))
        ttk.Combobox(levels,textvariable=self.lufs,values=['-9','-10','-11','-12','-13','-14','-16','-18'],width=6).pack(side='left')
        ttk.Label(levels,text='True Peak dBTP').pack(side='left',padx=(12,3))
        ttk.Combobox(levels,textvariable=self.true_peak,values=['-1.0','-1.5','-2.0','-2.5','-3.0'],width=6).pack(side='left')
        actions=ttk.Frame(panel);actions.pack(fill='x',pady=3)
        self.wav_button=ttk.Button(actions,text='▶ KONVERTIEREN',command=self.start_wav,style='Action.TButton')
        self.wav_button.pack(side='left',padx=(0,5))
        ttk.Button(actions,text='■ STOPP',command=lambda:self.stop_job('audio')).pack(side='left')
        ttk.Button(actions,text='WAV → MP3 REPAIR (A/B)',command=self.start_repair_from_wav).pack(side='left',padx=(12,3))
        ttk.Label(panel,textvariable=self.wav_status,wraplength=1080).pack(anchor='w',pady=(4,0))

    def apply_quality_preset(self):
        # Nur die vier betroffenen Audio-Optionen setzen. Kein Track wird dabei verarbeitet.
        mode=self.quality_preset.get()
        if mode not in ('maximum','balanced','original'):
            return
        self.sample_rate.set('48000')
        self.bitrate.set('320')
        self.pcm_format.set('fltp')
        self.channels.set('stereo')
        self.normalize.set(mode=='balanced')
        self.lufs.set('-14')
        self.true_peak.set('-2.0')
        self.wav_status.set('Preset gesetzt: '+{'maximum':'Maximum Quality — beste LAME-Qualität, ohne Normalisierung',
            'balanced':'Balanced Radio — 2-Pass EBU R128, -14 LUFS / -2 dBTP',
            'original':'Original Preserve — Pegel unverändert, hochwertiges Encoding'}[mode])

    @staticmethod
    def tool_path(name):
        # Portable bundle: beside EXE, in PyInstaller bundle, or on PATH.
        import sys
        local=Path(sys.executable if getattr(sys,'frozen',False) else __file__).resolve().parent/(name+'.exe')
        if local.is_file():return str(local)
        bundled=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))/(name+'.exe')
        if bundled.is_file():return str(bundled)
        tools_dir=local.parent/'tools'/(name+'.exe')
        if tools_dir.is_file():return str(tools_dir)
        return shutil.which(name) or str(local)

    def build_audio_labs(self,parent):
        ttk.Label(parent,text='AUDIO LABS · REMASTER, RESTAURATION & CLEANUP',
                  foreground=NeonUI.CYAN,font=('Segoe UI Semibold',15)).pack(anchor='w',pady=(8,2))
        ttk.Label(parent,text='Spezialisierte Audio-Werkzeuge aus dem Manager starten. Jedes Werkzeug öffnet ein eigenes Fenster.',
                  wraplength=1040,foreground=NeonUI.TEXT).pack(anchor='w',pady=(0,8))

        remaster=ttk.LabelFrame(parent,text='Suno Song Remaster',padding=12)
        remaster.pack(fill='x',pady=(0,8))
        ttk.Label(remaster,text='MP3-Remastering, LUFS/True-Peak-Ziele und Stapelverarbeitung.',
                  wraplength=760).pack(side='left',fill='x',expand=True)
        ttk.Button(remaster,text='▶ REMASTER STARTEN',
                   command=lambda:self.launch_audio_lab('suno'),
                   style='Action.TButton').pack(side='right',padx=(10,0))

        restoration=ttk.LabelFrame(parent,text='Restoration Lab',padding=12)
        restoration.pack(fill='x',pady=(0,8))
        ttk.Label(restoration,text='Rauschminderung, A/B-Wiedergabe und WAV-Export.',
                  wraplength=760).pack(side='left',fill='x',expand=True)
        ttk.Button(restoration,text='▶ RESTORATION STARTEN',
                   command=lambda:self.launch_audio_lab('restoration'),
                   style='Secondary.TButton').pack(side='right',padx=(10,0))

        cleanser=ttk.LabelFrame(parent,text='SunoCleanser',padding=12)
        cleanser.pack(fill='x',pady=(0,8))
        ttk.Label(cleanser,text='WAV- und MP3-Eingabe, Rauschminderung und 24-Bit-WAV-Export.',
                  wraplength=760).pack(side='left',fill='x',expand=True)
        ttk.Button(cleanser,text='▶ CLEANUP STARTEN',
                   command=lambda:self.launch_audio_lab('sunocleanser'),
                   style='Secondary.TButton').pack(side='right',padx=(10,0))

        ttk.Label(parent,
                  text='Die Werkzeuge bleiben getrennte Anwendungen. Fehlende Pakete oder Programme werden nicht automatisch installiert.',
                  wraplength=1040,foreground=NeonUI.PINK).pack(anchor='w',pady=(2,6))
        self.audio_lab_status=tk.StringVar(value='Audio-Tools bereit.')
        ttk.Label(parent,textvariable=self.audio_lab_status,wraplength=1040,
                  foreground=NeonUI.VIOLET).pack(anchor='w')

    def launch_audio_lab(self,tool):
        executable_dir=Path(sys.executable).resolve().parent
        source_dir=Path(__file__).resolve().parent
        roots=(source_dir.parent,executable_dir,executable_dir/'external-tools')
        try:
            command,working_directory=audio_lab_launch_spec(tool,roots)
            subprocess.Popen(command,cwd=str(working_directory))
        except (FileNotFoundError,RuntimeError,OSError) as exc:
            self.audio_lab_status.set(f'{tool}: {exc}')
            messagebox.showerror('Audio Labs',str(exc),parent=self.root)
            return
        label={
            'suno':'Suno Song Remaster',
            'restoration':'Restoration Lab',
            'sunocleanser':'SunoCleanser',
        }.get(tool,tool)
        self.audio_lab_status.set(f'{label} gestartet · eigenes Fenster')

    def build_system_panel(self,parent):
        panel=ttk.LabelFrame(parent,text='System-Check und Portable-EXE',padding=8)
        panel.pack(fill='x',pady=(8,0))
        self.sys_report=tk.StringVar(value='Noch nicht geprüft. Keine Installation ohne ausdrückliche Aktion.')
        row=ttk.Frame(panel);row.pack(fill='x')
        ttk.Button(row,text='System prüfen',command=self.check_system).pack(side='left',padx=3)
        ttk.Label(row,text='EXE-Build ausschließlich extern: BUILD_PORTABLE_EXE.bat').pack(side='left',padx=10)
        ttk.Label(panel,textvariable=self.sys_report,wraplength=1060,justify='left').pack(anchor='w',pady=3)

    def check_system(self):
        import sys,importlib.metadata
        items=['Python '+sys.version.split()[0]+(' (EXE)' if getattr(sys,'frozen',False) else ''),
               'Tkinter: OK']
        for pkg in ('mutagen','Pillow','PyInstaller'):
            try: items.append(pkg+': '+importlib.metadata.version(pkg))
            except importlib.metadata.PackageNotFoundError: items.append(pkg+': NICHT INSTALLIERT'+(' (optional: EXE-Build)' if pkg=='PyInstaller' else ''))
        for binary in ('ffmpeg','ffprobe'):
            path=self.tool_path(binary)
            if Path(path).is_file() or shutil.which(path):
                try:
                    r=subprocess.run([path,'-version'],capture_output=True,text=True,timeout=7,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                    items.append(binary+': '+(r.stdout.splitlines()[0] if r.returncode==0 else 'Fehler beim Start'))
                except Exception as exc:items.append(binary+': FEHLER '+str(exc))
            else:items.append(binary+': FEHLT (für Audio-Konvertierung erforderlich)')
        self.sys_report.set(' | '.join(items))
        messagebox.showinfo('Systemprüfung', '\n'.join(items)+'\n\nOnline-Update-Check ist nicht enthalten. Versionsnummern sind lokale Ist-Werte.')

    def build_exe(self):
        """Build bleibt strikt außerhalb der gestarteten GUI / der fertigen EXE."""
        messagebox.showinfo('EXE-Build / Build',
            'EXE-Build ausschließlich außerhalb der App über BUILD_PORTABLE_EXE.bat.\n'
            'Build only outside the application using BUILD_PORTABLE_EXE.bat.')

    def repair_audio_tools(self):
        # Fehlende Tools nie stillschweigend herunterladen oder installieren.
        if not messagebox.askyesno('Audio-Tools fehlen',
                'FFmpeg/FFprobe fehlen. Soll Windows Package Manager (winget) die Installation nach deiner Zustimmung starten?\n'
                'Internet und ggf. Windows-Rechte sind dafür erforderlich.\n'
                'Alternativ ffmpeg.exe und ffprobe.exe neben die EXE in tools/ kopieren.'):
            return
        if os.name != 'nt' or not shutil.which('winget'):
            messagebox.showwarning('Reparatur nicht verfügbar',
                'winget ist nicht verfügbar. Bitte ffmpeg.exe und ffprobe.exe in den tools-Ordner kopieren.')
            return
        try:
            subprocess.Popen(['winget','install','--id','Gyan.FFmpeg','--exact',
                              '--accept-source-agreements','--accept-package-agreements'],
                             creationflags=getattr(subprocess,'CREATE_NEW_CONSOLE',0))
            messagebox.showinfo('Audio-Tools Installation',
                'winget wurde separat gestartet. Nach erfolgreicher Installation die Anwendung neu starten; '
                'falls nötig, PATH aktualisieren. Ein Erfolg wird erst nach erneuter Prüfung bestätigt.')
        except Exception as exc:
            messagebox.showerror('Audio-Tools Installation',str(exc))

    def choose_wav(self):
        f=filedialog.askdirectory(title='Quellordner mit WAV/MP3 auswählen')
        if f:self.wav_folder.set(f)

    def start_repair_from_wav(self):
        """Eine beschädigt klingende MP3 aus ihrer sauberen WAV neu erzeugen.

        Kein In-place-Repair, keine verlustbehaftete MP3-zu-MP3-Rekodierung.
        Ziel liegt neben der beanstandeten MP3 im dedizierten Repair-Unterordner.
        """
        if self.convert_busy:
            messagebox.showinfo('WAV-Reparatur', 'Es läuft bereits eine Konvertierung.')
            return
        wav_name = filedialog.askopenfilename(title='Saubere Original-WAV auswählen',
                                              filetypes=[('WAV audio', '*.wav')])
        if not wav_name:
            return
        reference_name = filedialog.askopenfilename(title='Problematische MP3 auswählen (nur zum Vergleich)',
                                                    filetypes=[('MP3 audio', '*.mp3')])
        if not reference_name:
            return
        wav = Path(wav_name)
        reference = Path(reference_name)
        if not wav.is_file() or not reference.is_file() or wav.suffix.lower() != '.wav' or reference.suffix.lower() != '.mp3':
            messagebox.showerror('WAV-Reparatur', 'Nur eine existierende WAV und eine existierende MP3 auswählen.')
            return
        clean_wav = title_clean(filename_clean(wav.stem + '.wav').removesuffix('.wav')).casefold()
        clean_mp3 = title_clean(filename_clean(reference.stem + '.mp3').removesuffix('.mp3')).casefold()
        # Namen sind nur ein Hinweis und kein beweiskräftiger Audio-Fingerprint.
        if clean_wav != clean_mp3:
            if not messagebox.askyesno('WAV/MP3-Zuordnung prüfen',
                f'Die Dateinamen unterscheiden sich:\nWAV: {wav.name}\nMP3: {reference.name}\n\n'
                'Nur fortsetzen, wenn es tatsächlich derselbe Track ist. Fortfahren?'):
                return
        ffmpeg = self.tool_path('ffmpeg')
        ffprobe = self.tool_path('ffprobe')
        if not (Path(ffmpeg).is_file() or shutil.which(ffmpeg)) or not (Path(ffprobe).is_file() or shutil.which(ffprobe)):
            self.repair_audio_tools()
            return
        if not check_lame_encoder(ffmpeg):
            messagebox.showerror('Audio-Encoder','FFmpeg enthält keinen libmp3lame-Encoder. Bitte einen vollständigen FFmpeg-Build installieren.')
            return
        out = reference.parent / '_666MP3_REPAIR'
        # Reparaturprofile sind immer maximal und ohne Normalisierung.
        if not messagebox.askyesno('Quellbasierte Audio-Reparatur',
            f'WAV: {wav.name}\nReferenz-MP3: {reference.name}\n\n'
            f'Neue MP3 in: {out}\n48 kHz · 320 kbit/s · Stereo · Maximum Quality\n'
            'Normalisierung: AUS\nOriginal-WAV und Referenz-MP3 bleiben unverändert.\n'
            'Ein Hörvergleich bleibt erforderlich. Jetzt neu kodieren?'):
            return
        tags = {k:self.vars[k].get().strip() for k,_ in FIELDS}
        tags['COMM'] = tags['COMM'] or DEFAULT_COMMENT
        tags['WOAS'] = tags['WOAS'] or DEFAULT_SOURCE
        self.cancel_audio.clear()
        self.convert_busy = True
        self.wav_button.configure(state='disabled')
        self.audio_progress(1, 1, 0, wav.name, 'Quellbasierte Reparatur')
        settings = (48000, 320, 'fltp', 'stereo', False, -14.0, -2.0, 'maximum', True)
        threading.Thread(target=self.convert_wavs,
            args=([wav], out, ffmpeg, ffprobe, settings, tags),
            kwargs={'repair_mode': True, 'reference_mp3': reference}, daemon=True).start()

    def start_wav(self):
        if self.convert_busy:return
        folder=Path(self.wav_folder.get())
        if not folder.is_dir():messagebox.showerror('WAV','WAV-Ordner ungültig');return
        kind=self.input_kind.get()
        accepted={'.wav','.mp3'} if kind=='mixed' else {'.'+kind}
        tracks=sorted((self.audio_paths[k] for k in self.audio_tree.selection() if k in self.audio_paths and self.audio_paths[k].suffix.lower() in accepted),key=lambda p:p.name.casefold())
        if not tracks:messagebox.showinfo('Audio','Keine WAV/MP3-Dateien ausgewählt. Bitte einzelne Titel markieren oder „Alle auswählen“ nutzen.');return
        if self.quality_preset.get() in ('maximum','original') and self.normalize.get():
            messagebox.showerror('Preset-Schutz','Maximum Quality und Original Preserve enthalten KEINE Normalisierung. Deaktiviere Lautheit oder wähle Balanced Radio.');return
        ffmpeg=self.tool_path('ffmpeg')
        ffprobe=self.tool_path('ffprobe')
        if not Path(ffmpeg).is_file() and not shutil.which(ffmpeg):self.repair_audio_tools();return
        if not Path(ffprobe).is_file() and not shutil.which(ffprobe):self.repair_audio_tools();return
        if not check_lame_encoder(ffmpeg):
            messagebox.showerror('Audio-Encoder','FFmpeg enthält keinen libmp3lame-Encoder.')
            return
        try:
            sr=int(self.sample_rate.get()); br=int(self.bitrate.get()); target=float(self.lufs.get());tp=float(self.true_peak.get())
            if sr not in (44100,48000) or br not in (128,160,192,224,256,320) or not (-24<=target<=-8) or not (-5<=tp<=-1):raise ValueError()
        except ValueError:
            messagebox.showerror('Einstellungen','Samplerate/Bitrate/Ziel-LUFS/True-Peak ungültig.');return
        output=folder/('_666MP3_MIXED_EXPORT' if kind=='mixed' else '_666MP3_EXPORT' if kind=='wav' else '_666MP3_REENCODE')
        wav_n=sum(p.suffix.lower()=='.wav' for p in tracks)
        mp3_n=len(tracks)-wav_n
        confirm=(f'{len(tracks)} Dateien gefunden (WAV: {wav_n}, MP3: {mp3_n}).\nAusgabe: {output}\nOriginale bleiben unverändert.\n'
                 f'Bereits belegte Namen werden mit (1), (2), ... eindeutig gemacht.\n\n'
                 f'Qualität: {sr} Hz / {br} kbit/s / {self.pcm_format.get()} / {self.channels.get()}\n'
                 f'Preset: {self.quality_preset.get()} · LAME compression_level 0\n'
                 f'Normalisierung: {"EIN (2-Pass)" if self.normalize.get() else "AUS"}\n'
                 f'Audio-QC nach Export: {"EIN" if self.audio_qc.get() else "AUS"}\nFortfahren?')
        if kind in ('mp3','mixed') and any(p.suffix.lower()=='.mp3' for p in tracks):
            confirm += '\nACHTUNG: MP3-Reencoding kann keine verlorene Qualität zurückholen und verursacht Generationsverluste.\n'
        if not messagebox.askyesno('Audio → MP3',confirm):return
        settings=(sr,br,self.pcm_format.get(),self.channels.get(),self.normalize.get(),target,tp,self.quality_preset.get(),self.audio_qc.get())
        tag_values={k:self.vars[k].get().strip() for k,_ in FIELDS}
        tag_values['COMM']=tag_values['COMM'] or DEFAULT_COMMENT
        tag_values['WOAS']=tag_values['WOAS'] or DEFAULT_SOURCE
        self.cancel_audio.clear()
        self.convert_busy=True;self.wav_button.configure(state='disabled')
        self.audio_progress(1,len(tracks),0,tracks[0].name,'Start')
        threading.Thread(target=self.convert_wavs,args=(tracks,output,ffmpeg,ffprobe,settings,tag_values),daemon=True).start()

    def convert_wavs(self,tracks,output,ffmpeg,ffprobe,settings,tag_values,repair_mode=False,reference_mp3=None):
        sr,br,pcm,channels,normalize,target,tp,preset,audio_qc=settings
        output.mkdir(exist_ok=True)
        errors=[];success=0;skipped=0
        if preset in ('maximum','original') and normalize:
            raise ValueError('Maximum Quality/Original Preserve dürfen keine Normalisierung verwenden')
        def call(cmd):
            return self.run_interruptible(cmd,self.cancel_audio)
        for i,path in enumerate(tracks,1):
            if self.cancel_audio.is_set():break
            self.root.after(0,lambda i=i,n=len(tracks),p=path:self.audio_progress(i,n,0,p.name,'Vorbereitung') if not self.cancel_audio.is_set() else None)
            self.root.after(0,lambda i=i,n=len(tracks),p=path:self.wav_status.set(f'Konvertiere {i}/{n}: {p.name}'))
            name=filename_clean(path.stem+'.mp3')
            name=title_clean(Path(name).stem)+'.mp3'
            if repair_mode:
                name=Path(name).stem+' REPAIRED.mp3'
            dest=output/name
            # collisions: never overwrite, even with multiple WAVs converging to one destination
            if dest.exists():
                stem=dest.stem;counter=1
                while dest.exists():dest=output/f'{stem} {counter}.mp3';counter+=1
            temp=output/(dest.stem+'.partial.mp3')
            if temp.exists():
                errors.append(f'{path.name}: temporäre Datei existiert bereits; nicht überschrieben');skipped+=1;continue
            try:
                probe=call([ffprobe,'-v','error','-show_entries','stream=codec_type','-of','json',str(path)])
                if probe.returncode or not any(s.get('codec_type')=='audio' for s in json.loads(probe.stdout).get('streams',[])):
                    raise RuntimeError('keine gültige Audiospur')
                # 32-Bit-Float-Planar als bevorzugtes Filter-Zwischenformat; FFmpeg verhandelt danach das Encoderformat selbst.
                filters=[f'aformat=sample_fmts={pcm}',f'aresample={sr}']
                if normalize:
                    self.root.after(0,lambda i=i,n=len(tracks),p=path:self.audio_progress(i,n,0,p.name,'Lautheitsanalyse (Pass 1)'))
                    first=f'loudnorm=I={target}:TP={tp}:LRA=11:print_format=json'
                    cmd=[ffmpeg,'-hide_banner','-nostdin','-v','info','-i',str(path),'-vn','-af',','.join(filters+[first]),'-f','null','-']
                    result=call(cmd)
                    if result.returncode:raise RuntimeError('Lautheitsmessung fehlgeschlagen: '+result.stderr[-400:])
                    import re as _re
                    match=_re.findall(r'\{\s*"input_i".*?\}',result.stderr,_re.S)
                    if not match:raise RuntimeError('Keine Lautheitsmesswerte erhalten')
                    stat=json.loads(match[-1])
                    # Strikt keine dynamische Veränderung ohne ausdrückliche Freigabe.
                    validate_linear_loudnorm_measurement(stat, target, tp)
                    norm=(f'loudnorm=I={target}:TP={tp}:LRA=11:'
                          f'measured_I={stat["input_i"]}:measured_TP={stat["input_tp"]}:'
                          f'measured_LRA={stat["input_lra"]}:measured_thresh={stat["input_thresh"]}:'
                          f'offset={stat["target_offset"]}:linear=true:print_format=summary')
                    filters.append(norm)
                cmd=[ffmpeg,'-hide_banner','-nostdin','-n','-v','error','-i',str(path),'-map','0:a:0','-map_metadata','0','-vn','-af',','.join(filters),'-ar',str(sr),'-ac',('2' if channels=='stereo' else '1'),'-c:a','libmp3lame','-compression_level','0','-b:a',f'{br}k','-id3v2_version','3',str(temp)]
                # FFmpeg emits actual processed audio time, not an estimated percentage.
                duration_probe=call([ffprobe,'-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(path)])
                try: duration=max(0.001,float(duration_probe.stdout.strip()))
                except (ValueError,TypeError):duration=0
                cmd=cmd[:1]+['-progress','pipe:1','-nostats']+cmd[1:]
                with subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',errors='replace',creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)) as process:
                    with self.process_lock:self.active_process=process
                    stderr_data=[]
                    stderr_thread=threading.Thread(target=lambda:stderr_data.append(process.stderr.read()),daemon=True)
                    stderr_thread.start()
                    for line in process.stdout:
                        if self.cancel_audio.is_set():
                            process.terminate()
                            break
                        if line.startswith('out_time_us=') or line.startswith('out_time_ms='):
                            try:
                                encoded_us=int(line.split('=',1)[1]);fraction=min(.99,max(0,encoded_us/1_000_000/duration)) if duration else 0
                                percent=100*((i-1)+fraction)/len(tracks)
                                self.root.after(0,lambda f=fraction,i=i,n=len(tracks),p=path:self.audio_progress(i,n,f,p.name,'Kodierung (Pass 2)') if not self.cancel_audio.is_set() else None)
                            except (ValueError,ZeroDivisionError):pass
                    returncode=process.wait()
                    stderr_thread.join(timeout=2)
                    with self.process_lock:
                        if self.active_process is process:self.active_process=None
                if self.cancel_audio.is_set():raise InterruptedError('Konvertierung gestoppt')
                if returncode:raise RuntimeError('MP3-Encoding: '+''.join(stderr_data)[-400:])
                if not temp.is_file() or temp.stat().st_size<1024:raise RuntimeError('MP3-Ausgabe leer')
                chk=call([ffprobe,'-v','error','-show_entries','stream=codec_name,sample_rate,channels','-of','json',str(temp)])
                streams=json.loads(chk.stdout).get('streams',[])
                if chk.returncode or not streams or streams[0].get('codec_name')!='mp3' or int(streams[0].get('sample_rate',0))!=sr or int(streams[0].get('channels',0))!=(2 if channels=='stereo' else 1):raise RuntimeError('Ausgabevalidierung fehlgeschlagen')
                # Gemeinsamer Workflow: Dateiname bereinigen, MP3 ausgeben, ID3-TIT2=dest.stem ohne Dateiendung.
                # Abfolge: Dateiname zuerst endgültig vergeben, DANACH ID3-Metadaten.
                # Hardlink mit exklusiver Ziel-Neuanlage verhindert Überschreiben auch bei
                # konkurrierenden Prozessen. Verfügbares Ziel ist im selben Ausgabeordner.
                # Sollte das Dateisystem Hardlinks verweigern, bricht nur diese Datei ab.
                if dest.exists():raise RuntimeError('Zieldatei zwischenzeitlich angelegt – nicht überschrieben')
                os.link(temp, dest)
                temp.unlink()
                try:
                    if self.cancel_audio.is_set():raise InterruptedError('Vor Metadaten abgebrochen')
                    # TIT2 wird IMMER aus dem bereinigten endgültigen Dateinamen abgeleitet,
                    # niemals aus dem allgemeinen Songtitel-Feld oder mit ".mp3".
                    automatic_convert_tags(dest, path, dest.stem, tag_values)
                    qc_result = None
                    if audio_qc:
                        self.root.after(0,lambda i=i,n=len(tracks),p=path:self.audio_progress(i,n,.99,p.name,'Audio-QC: vollständige MP3 dekodieren'))
                        qc_result = verify_encoded_mp3(ffmpeg, ffprobe, dest, duration, runner=call)
                    if self.cancel_audio.is_set():raise InterruptedError('Beim Audio-QC abgebrochen')
                except Exception:
                    # Nur die von diesem Auftrag neu erzeugte Zieldatei entfernen.
                    dest.unlink(missing_ok=True)
                    raise
                # Beweisspur: Nicht auf subjektive Artefaktfreiheit schließen.
                # QC-Report ist rein additiv; Ausgabedatei wird nicht angefasst.
                try:
                    write_audio_evidence(dest, path, preset=preset, normalized=normalize,
                                         qc_result=qc_result, reference_mp3=reference_mp3 if repair_mode else None)
                except (OSError, ValueError) as report_exc:
                    errors.append(f'{dest.name}: Qualitätsbericht nicht angelegt: {report_exc}')
                success+=1
                self.root.after(0,lambda i=i,n=len(tracks),p=path:self.audio_progress(i,n,1,p.name,'Datei abgeschlossen'))
            except InterruptedError:
                if temp.exists():temp.unlink()
                self.cancel_audio.set()
                break
            except Exception as exc:
                errors.append(f'{path.name}: {exc}');skipped+=1
                if temp.exists():temp.unlink()
        def done():
            processed=success+skipped
            total=len(tracks)
            # Prozent = bearbeitete Aufträge, NICHT Erfolgsquote. Bei Fehlern nie "alles erfolgreich" behaupten.
            status='Gestoppt' if self.cancel_audio.is_set() else ('Mit Fehlern beendet' if skipped or errors else 'Erfolgreich beendet')
            self.progress_update('audio',100*processed/max(1,total),processed,total,status)
            self.convert_busy=False;self.wav_button.configure(state='normal')
            self.wav_status.set(f'Audio → MP3: {success} erfolgreich, {skipped} fehlgeschlagen, '
                                f'{total-processed} unbearbeitet; Ausgabe: {output}')
            self.current_file.set(f'{status}: {success} erfolgreich / {skipped} fehlgeschlagen')
            self.file_percent.set(0 if self.cancel_audio.is_set() else 100)
            self.label_file.set('Gestoppt' if self.cancel_audio.is_set() else 'Einzeldatei: fertig / siehe Auftragsergebnis')
            self.job_details.set(f'KONVERTIERUNG {"GESTOPPT" if self.cancel_audio.is_set() else "BEENDET"} · {success}/{len(tracks)} erfolgreich · {skipped} Fehler')
            msg=f'{success} erfolgreich; {skipped} Fehler.\n\nAusgabe: {output}'
            if errors:msg+='\n\n'+'\n'.join(errors[:10])
            messagebox.showinfo('Audio → MP3 gestoppt' if self.cancel_audio.is_set() else 'Audio → MP3 abgeschlossen',msg)
        self.root.after(0,done)

    def refresh_counts(self):
        if self.folder.get() and Path(self.folder.get()).is_dir():
            self.scan()
        self.update_audio_counts()

    def update_audio_counts(self):
        try:
            folder=Path(self.wav_folder.get())
            files=[p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in ('.wav','.mp3')] if folder.is_dir() else []
            wav=sum(p.suffix.lower()=='.wav' for p in files)
            mp3=len(files)-wav
            kind=self.input_kind.get()
            active=wav if kind=='wav' else mp3 if kind=='mp3' else len(files)
            self.audio_counts.set(f'QUELLE: {active} ausgewählt  |  WAV: {wav}  |  MP3: {mp3}')
        except OSError:
            self.audio_counts.set('QUELLE: nicht lesbar')

    def choose_cover_all(self):
        name=filedialog.askopenfilename(title='Bild für alle ausgewählten MP3',filetypes=[('Bilder','*.jpg *.jpeg *.png *.webp *.bmp *.gif *.tif *.tiff *.ico'),('Alle Dateien','*.*')])
        if name:
            self.cover_global.set(name);self.cover_enable.set(True);self.show_cover_preview(name);self.refresh_metadata_targets()

    def choose_cover_selected(self):
        ids=self.tree.selection()
        files=[self.files[item][0] for item in ids if item in self.files and self.files[item][0].suffix.lower()=='.mp3']
        if not files:
            messagebox.showinfo('Cover','Zuerst mindestens eine MP3 in der Dateiliste markieren.');return
        name=filedialog.askopenfilename(title='Bild für markierte MP3',filetypes=[('Bilder','*.jpg *.jpeg *.png *.webp *.bmp *.gif *.tif *.tiff *.ico'),('Alle Dateien','*.*')])
        if name:
            for path in files:self.cover_per_file[str(path)]=name
            self.cover_enable.set(True);self.show_cover_preview(name)
            self.cover_info.set(f'{len(files)} MP3 individuell: {Path(name).name}')
            self.selection_mode.set('selected');self.refresh_metadata_targets()

    def clear_cover_choices(self):
        self.cover_global.set('');self.cover_per_file.clear();self.cover_enable.set(False)
        self.cover_info.set('Cover-Zuweisungen gelöscht; vorhandene MP3-Cover bleiben unangetastet.')
        self.cover_thumbnail.configure(image='',text='Kein Cover');self.cover_preview_image=None
        self.refresh_metadata_targets()

    def show_cover_preview(self,path):
        try:
            with Image.open(path) as src:
                image=ImageOps.exif_transpose(src).convert('RGB')
                image.thumbnail((76,76),Image.Resampling.LANCZOS)
                photo=ImageTk.PhotoImage(image)
            self.cover_preview_image=photo
            self.cover_thumbnail.configure(image=photo,text='')
            self.cover_info.set(Path(path).name)
        except Exception as exc:
            self.cover_info.set(f'Bild nicht lesbar: {exc}')

    def cover_bytes(self,path):
        with Image.open(path) as src:
            image=ImageOps.exif_transpose(src).convert('RGB')
            if self.cover_fit.get()=='stretch':
                image=image.resize((512,512),resample=Image.Resampling.LANCZOS)
            elif self.cover_fit.get()=='crop':
                image=ImageOps.fit(image,(512,512),method=Image.Resampling.LANCZOS,centering=(0.5,0.5))
            else:
                # Kein Beschnitt; freie Flächen neutral schwarz ergänzen.
                image=ImageOps.pad(image,(512,512),method=Image.Resampling.LANCZOS,color=(0,0,0))
            output=io.BytesIO()
            image.save(output,format='JPEG',quality=max(1,min(100,int(self.cover_quality.get()))),subsampling=0,optimize=True)
            return output.getvalue()

    def choose(self):
        path=filedialog.askdirectory(title='MP3/WAV-Musikordner auswählen')
        if path:
            self.folder.set(path)
            if not self.wav_folder.get():self.wav_folder.set(path)
            self.scan()

    def update_file_counts(self):
        paths=[p for p,_ in self.files.values()]
        mp3=sum(p.suffix.lower()=='.mp3' for p in paths)
        wav=sum(p.suffix.lower()=='.wav' for p in paths)
        chosen=len(self.files) if self.selection_mode.get()=='all' else len(self.tree.selection())
        self.file_counts.set(f'GESAMT: {len(paths)}  |  MP3: {mp3}  |  WAV: {wav}  |  AUSGEWÄHLT: {chosen}')
        if hasattr(self,'metadata_list'):self.refresh_metadata_targets()

    def scan(self):
        self.tree.delete(*self.tree.get_children());self.files={}
        folder=Path(self.folder.get())
        if not folder.is_dir():
            self.update_file_counts()
            self.status.set('Kein gültiger Ordner.');return
        errors=0
        for path in sorted(folder.iterdir(),key=lambda x:x.name.casefold()):
            if not path.is_file() or path.suffix.lower() not in ('.mp3','.wav'):continue
            try:
                if path.suffix.lower()=='.mp3':
                    d=read_tags(path)
                else:
                    d={k:'' for k,_ in FIELDS}
                    d.update({'_c2pa':False,'_lyrics':False,'_cover':False})
                newname=filename_clean(path.name) if self.rename_on.get() else path.name
                if self.rename_number_suffix.get():
                    newname=title_clean(Path(newname).stem)+Path(newname).suffix
                item=self.tree.insert('',tk.END,values=(path.name,newname,d['TIT2'] if path.suffix.lower()=='.mp3' else '— WAV (kein ID3)',d['COMM'] if path.suffix.lower()=='.mp3' else '—','JA' if d['_c2pa'] else 'NEIN'))
                self.files[item]=(path,d)
            except Exception: errors+=1
        self.update_file_counts()
        self.refresh_metadata_targets()
        self.status.set(f'{len(self.files)} Audio-Dateien (MP3/WAV) gelesen; {errors} Lesefehler. Nichts geändert.')

    def metadata_select(self,event=None):
        if getattr(self,'_sync_meta',False):return
        indices=self.metadata_list.curselection()
        if not indices:return
        self.selection_mode.set('selected')
        items=[getattr(self,'metadata_ids',[])[i] for i in indices if i<len(getattr(self,'metadata_ids',[]))]
        self.tree.selection_set(items)
        self.refresh_metadata_targets()

    def metadata_all(self):
        self.selection_mode.set('all')
        self.refresh_metadata_targets()

    def metadata_marked(self):
        self.selection_mode.set('selected')
        self.refresh_metadata_targets()

    def refresh_metadata_targets(self):
        if not hasattr(self,'metadata_list'):return
        self._sync_meta=True
        try:
            targets=[(item,p,d) for item,(p,d) in self.files.items() if p.suffix.lower()=='.mp3']
            self.metadata_ids=[item for item,p,d in targets]
            self.metadata_list.delete(0,tk.END)
            selected=set(self.tree.selection())
            for idx,(item,path,d) in enumerate(targets):
                cover=(self.cover_per_file.get(str(path)) or self.cover_global.get()) if self.cover_enable.get() else ''
                cpa=' | C2PA: GESCHÜTZT' if d.get('_c2pa') and not self.c2pa_ok.get() else ''
                self.metadata_list.insert(tk.END,f'{path.name}  |  Cover: {"NEU" if cover else "vorhanden" if d.get("_cover") else "kein"}{cpa}')
                if item in selected:self.metadata_list.selection_set(idx)
            chosen=[(p,d) for item,p,d in targets if self.selection_mode.get()=='all' or item in selected]
            protected=sum(bool(d.get('_c2pa')) for p,d in chosen)
            assigned=sum(bool(self.cover_per_file.get(str(p)) or self.cover_global.get()) for p,d in chosen) if self.cover_enable.get() else 0
            names=', '.join(p.name for p,d in chosen[:3])
            if len(chosen)>3:names+=f' … (+{len(chosen)-3})'
            mode='ALLE MP3' if self.selection_mode.get()=='all' else 'MARKIERTE MP3'
            self.cover_targets_text.set(f'{mode}: {len(chosen)} von {len(targets)} · Neues Cover für {assigned} · C2PA: {protected} | {names or "Keine Ziele"}')
        finally:self._sync_meta=False

    def select_all(self):
        self.tree.selection_set(*self.tree.get_children())
        self.update_file_counts()

    def selected(self,evt=None):
        self.update_file_counts()
        self.refresh_metadata_targets()
        ids=self.tree.selection()
        if len(ids)==1:
            path,d=self.files[ids[0]]
            self.status.set(f'{path.name} | Cover: {"ja" if d["_cover"] else "nein"} | Lyrics: {"ja" if d["_lyrics"] else "nein"} | C2PA: {"ja" if d["_c2pa"] else "nein"}')

    def load_one(self):
        ids=self.tree.selection()
        if len(ids)!=1: messagebox.showinfo('Auswahl','Genau eine Datei markieren.');return
        path,d=self.files[ids[0]]
        if path.suffix.lower()!='.mp3':
            messagebox.showinfo('WAV-Datei','WAV-Dateien können umbenannt werden; der ID3-Editor verarbeitet ausschließlich MP3-Dateien.')
            return
        for k,_ in FIELDS: self.vars[k].set(d[k])
        self.status.set('Dateitags geladen. Feldhaken kontrollieren: nur aktivierte Felder werden geändert.')

    def targets(self):
        return list(self.files) if self.selection_mode.get()=='all' else list(self.tree.selection())

    def sync_title_controls(self,*_):
        """Mutually exclusive title sources: manual / filename / existing tag."""
        mode=self.title_transfer.get()
        if getattr(self,'_syncing_title',False):return
        self._syncing_title=True
        try:
            if mode!='none':self.flags['TIT2'].set(False)
            if hasattr(self,'title_entry'):
                self.title_entry.configure(state='normal' if mode=='none' else 'disabled')
                self.title_check.configure(state='normal' if mode=='none' else 'disabled')
        finally:self._syncing_title=False

    def on_manual_title_flag(self,*_):
        if getattr(self,'_syncing_title',False):return
        if self.flags['TIT2'].get() and self.title_transfer.get()!='none':
            self.title_transfer.set('none')

    def on_manual_title_value(self,*_):
        if getattr(self,'_syncing_title',False):return
        if self.title_transfer.get()!='none':return
        # Manual input is only written with an explicit enabled checkbox.

    def desired_mp3_fields(self,old):
        desired={}
        for k,_ in FIELDS:
            if self.flags[k].get() and not (k=='TIT2' and self.title_transfer.get()!='none'):
                val=self.vars[k].get()
                if k=='TIT2' and not val.strip():val=old[k]
                if k=='TIT2' and self.clean_title.get():val=title_clean(val)
                if val!=old[k]:desired[k]=val
        if self.clean_title.get() and not self.flags['TIT2'].get():
            cleaned=title_clean(old['TIT2'])
            if cleaned!=old['TIT2']:desired['TIT2']=cleaned
        return desired

    def plans(self):
        """Plant Umbenennungen deterministisch, ohne irgendeine vorhandene Datei zu ersetzen."""
        raw=[]
        for item in self.targets():
            path,old=self.files[item]
            newname=filename_clean(path.name) if self.rename_on.get() else path.name
            if self.rename_number_suffix.get():
                newname=title_clean(Path(newname).stem)+Path(newname).suffix
            desired={}
            if path.suffix.lower()=='.mp3':
                desired=self.desired_mp3_fields(old)
            if path.suffix.lower()=='.mp3':
                if self.title_transfer.get()=='file_to_tag':
                    title=title_clean(Path(newname).stem)
                    if title and title!=old['TIT2']:desired['TIT2']=title
                elif self.title_transfer.get()=='tag_to_file' and old['TIT2'].strip():
                    stem=title_clean(old['TIT2']).strip()
                    # Windows-Zieldateiname ohne verbotene Zeichen; inhaltsgebundene Titel bleiben unverändert.
                    if not any(ch in stem for ch in '<>:"/\\|?*') and not stem.endswith(('.', ' ')):
                        newname=stem+path.suffix
            raw.append((path,path.with_name(newname),old,desired))

        existing={p.name.casefold() for p in Path(self.folder.get()).iterdir() if p.is_file()}
        reserved=set(existing)
        # Files that keep the identical filename are handled as in-place metadata edits.
        out=[]
        for path,preferred,old,desired in sorted(raw,key=lambda r:r[0].name.casefold()):
            target=preferred
            issue=''
            if not path.is_file():
                issue='QUELLDATEI FEHLT – Ordner neu scannen'
            elif target!=path:
                candidate=target.name.casefold()
                if candidate in reserved:
                    if not self.resolve_collisions.get():
                        issue='ZIELKONFLIKT – Ziel existiert oder mehrfach geplant'
                    else:
                        # Numerals go immediately before .mp3, preserving title otherwise.
                        stem,suffix=target.stem,target.suffix
                        n=1
                        while candidate in reserved:
                            target=path.with_name(f'{stem} {n}{suffix}')
                            candidate=target.name.casefold()
                            n+=1
                if not issue: reserved.add(target.name.casefold())
            out.append((path,target,old,desired,issue))
        # Respect tree/selection order for reporting, but decisions above are stable.
        order={p:i for i,(p,_,_,_) in enumerate(raw)}
        yield from sorted(out,key=lambda r:order[r[0]])

    def preview(self):
        plans=list(self.plans())
        if not plans: messagebox.showinfo('Vorschau','Bitte Dateien markieren oder Alle Dateien aktivieren.');return
        lines=[];blocked=0;changed=0
        for p,t,old,d,clash in plans:
            status=clash if clash else ('C2PA: ID3 wird übersprungen; Dateiumbenennung bleibt möglich' if d and old['_c2pa'] and not self.c2pa_ok.get() and p!=t else 'C2PA: ID3 gesperrt' if d and old['_c2pa'] and not self.c2pa_ok.get() else 'OK')
            if status!='OK':blocked+=1
            if p!=t or d:changed+=1
            lines.append(f'{p.name} -> {t.name}\n  {status}; ID3: '+(', '.join(d) if d else 'unverändert'))
        msg=f'{len(plans)} Dateien gewählt; {changed} Änderungen geplant; {blocked} mit Warnung.\n\n'+'\n'.join(lines[:40])
        if len(lines)>40:msg+=f'\n... weitere {len(lines)-40} Einträge'
        win=tk.Toplevel(self.root);win.title('Lese-Vorschau – keine Änderungen');win.geometry('940x590')
        tx=tk.Text(win,wrap='word');tx.pack(fill='both',expand=True);tx.insert('1.0',msg);tx.configure(state='disabled')

    def export_csv(self):
        if not self.files:messagebox.showinfo('CSV','Zuerst Ordner prüfen.');return
        dest=filedialog.asksaveasfilename(defaultextension='.csv',filetypes=[('CSV','*.csv')],initialfile='MP3_Metadaten.csv')
        if not dest:return
        with open(dest,'w',newline='',encoding='utf-8-sig') as f:
            w=csv.writer(f,delimiter=';');w.writerow(['Dateiname']+[label for _,label in FIELDS]+['Cover','Lyrics','C2PA'])
            for path,d in self.files.values():w.writerow([path.name]+[d[k] for k,_ in FIELDS]+[d['_cover'],d['_lyrics'],d['_c2pa']])
        messagebox.showinfo('CSV','CSV erstellt. Keine Audio-Datei verändert.')

    def save_metadata_only(self):
        """Bearbeitet MP3-Tags/Cover unabhängig von der Dateinamen-Umbenennung."""
        self.save(metadata_only=True)

    def save(self, metadata_only=False):
        plans=list(self.plans())
        if metadata_only:
            plans=[(path,path,old,changes,issue) for path,target,old,changes,issue in plans if path.suffix.lower()=='.mp3']
        if not plans:messagebox.showinfo('Speichern','Keine Dateien ausgewählt.');return
        changed=[x for x in plans if x[0]!=x[1] or x[3] or (x[0].suffix.lower()=='.mp3' and self.cover_enable.get() and (str(x[0]) in self.cover_per_file or self.cover_global.get()))]
        if not changed:messagebox.showinfo('Speichern','Keine Änderungen geplant.');return
        if self.cover_enable.get():
            active_covers={self.cover_per_file.get(str(x[0])) or self.cover_global.get() for x in changed if x[0].suffix.lower()=='.mp3'}
            for cover in active_covers-{''}:
                try:
                    raw=self.cover_bytes(cover)
                    with Image.open(io.BytesIO(raw)) as test_image:
                        if test_image.size!=(512,512) or test_image.format!='JPEG':raise ValueError('kein 512×512 JPEG')
                except Exception as exc:
                    messagebox.showerror('Cover-Prüfung',f'Cover nicht verwendbar: {cover}\n{exc}\nKeine Datei verändert.')
                    return

        if not messagebox.askyesno('Verbindliche Bestätigung',f'{len(changed)} Dateien sollen bearbeitet werden.\nVor jeder Änderung wird die originale MP3/WAV in einem Sicherungsordner abgelegt.\nC2PA-Schutz: {"WARNUNG akzeptiert" if self.c2pa_ok.get() else "aktiv"}.\nFortfahren?'):return
        folder=Path(self.folder.get()); backup=folder/('_666MP3_BACKUP_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
        success=0;skip=[];created=False
        partial=[]
        self.cancel_rename=False
        self.busy_rename=True
        self.save_button.configure(state='disabled')
        progress_kind='metadata' if metadata_only else 'rename'
        self.progress_update(progress_kind,0,0,len(changed),'Metadaten starten' if metadata_only else 'Bearbeitung startet')
        self.metadata_success=0
        self.metadata_errors=0
        for index,(path,target,old,changes,issue) in enumerate(changed,1):
            self.root.update()
            if self.cancel_rename:break
            self.current_file.set(f'{index}/{len(changed)} · {path.name}')
            self.job_details.set(f'Metadaten bearbeiten · {index}/{len(changed)} · OK {success} · Fehler {len(skip)}' if metadata_only else f'Datei bearbeiten · {index}/{len(changed)}')
            self.progress_update(progress_kind,100*(index-1)/len(changed),index-1,len(changed),'Bearbeitung läuft')
            self.root.update_idletasks()
            if issue:
                skip.append(f'{path.name}: {issue}')
                self.progress_update(progress_kind,100*index/len(changed),index,len(changed),'Fehler / übersprungen')
                continue
            cover_path=(self.cover_per_file.get(str(path)) or self.cover_global.get()) if self.cover_enable.get() and path.suffix.lower()=='.mp3' else ''
            actual_changes=changes
            if (changes or cover_path) and old['_c2pa'] and not self.c2pa_ok.get():
                actual_changes={}
                cover_path=''
                if target==path:
                    skip.append(f'{path.name}: C2PA – ID3-Schreibschutz aktiv')
                    self.progress_update(progress_kind,100*index/len(changed),index,len(changed),'C2PA geschützt')
                    continue
                partial.append(f'{path.name}: nur umbenannt; ID3 wegen C2PA nicht geändert')
            try:
                # Neuen Zielstatus unmittelbar vor jeder Bearbeitung kontrollieren.
                if not path.is_file():
                    skip.append(f'{path.name}: QUELLDATEI FEHLT')
                    continue
                if target!=path and target.exists():
                    skip.append(f'{path.name}: ZIEL EXISTIERT BEREITS')
                    continue
                if not created:
                    backup.mkdir(exist_ok=False)
                    created=True
                shutil.copy2(path,backup/path.name)
                if actual_changes or cover_path:
                    try: tags=ID3(path)
                    except ID3NoHeaderError:tags=ID3()
                    for key,val in actual_changes.items():
                        tags.delall(key)
                        if val=='':continue
                        if key=='COMM':tags.add(COMM(encoding=3,lang='eng',desc='',text=[val]))
                        elif key=='WOAS':tags.add(WOAS(url=val))
                        else:tags.add(FRAME_CLASS[key](encoding=3,text=[val]))
                    if cover_path:
                        data=self.cover_bytes(cover_path)
                        tags.delall('APIC')
                        tags.add(APIC(encoding=3,mime='image/jpeg',type=3,desc='Cover',data=data))
                    tags.save(path,v2_version=4)
                    if cover_path:
                        verify=ID3(path).getall('APIC')
                        if not any(frame.mime=='image/jpeg' and frame.data==data for frame in verify):
                            raise RuntimeError('Cover-Readback fehlgeschlagen')
                if target!=path: path.rename(target)
                success+=1
            except Exception as exc:
                skip.append(f'{path.name}: {exc}')
            self.progress_update(progress_kind,100*index/len(changed),index,len(changed),f'OK {success} · Fehler {len(skip)}')
            self.root.update_idletasks()
        if not self.cancel_rename:self.progress_update(progress_kind,100,len(changed),len(changed),f'Fertig · OK {success} · Fehler {len(skip)}')
        else:self.job_details.set(f'STOPP · {success} abgeschlossen, {len(skip)} Fehler/übersprungen')
        self.busy_rename=False
        self.save_button.configure(state='normal')
        self.scan()
        self.job_details.set(f'{"Gestoppt" if self.cancel_rename else "Abgeschlossen"} · Metadaten: {success} erfolgreich, {len(skip)} Fehler/übersprungen' if metadata_only else self.job_details.get())
        result=f'{"ABGEBROCHEN · " if self.cancel_rename else ""}{success} erfolgreich, {len(skip)} übersprungen.\nSicherungen: {backup if created else "keine"}'
        if partial: result+='\n\nTEILERFOLGE (C2PA):\n'+'\n'.join(partial[:8])
        if skip:result+='\n\n'+ '\n'.join(skip[:12])
        messagebox.showinfo('Bearbeitung abgeschlossen',result)

if __name__=='__main__':
    root=TkinterDnD.Tk() if TkinterDnD is not None else tk.Tk()
    App(root)
    root.mainloop()
