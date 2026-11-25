"""Bedienoberfläche für die lokalen Medienwerkzeuge."""
from pathlib import Path
from queue import Empty, Queue
from threading import Event, Thread
import tkinter as tk
from tkinter import filedialog, ttk

from media_tools import export_media, inspect_media


class MediaWindow:
    def __init__(self, parent, ffmpeg, ffprobe, publish):
        self.window = tk.Toplevel(parent)
        self.window.title('L.Y.V.R.A. · MEDIENWERKZEUGE')
        self.window.minsize(690, 450)
        self.window.protocol('WM_DELETE_WINDOW', self.close)
        self.ffmpeg, self.ffprobe, self.publish = ffmpeg, ffprobe, publish
        self.events = Queue()
        self.cancel = Event()
        self.busy = False
        self.source = None
        self.streams = []
        self.images = []
        self.source_label = tk.StringVar(self.window, 'Keine Quelldatei gewählt')
        self.status = tk.StringVar(self.window, 'Wähle eine lokale Audio- oder Videodatei.')
        self.format = tk.StringVar(self.window, 'MP3')
        self.size = tk.StringVar(self.window, '1280 × 720')
        self.fade = tk.BooleanVar(self.window, True)

        panel = ttk.Frame(self.window, padding=16)
        panel.pack(fill='both', expand=True)
        panel.columnconfigure(1, weight=1)
        self.source_button = ttk.Button(panel, text='Quelldatei wählen …', command=self.choose_source)
        self.source_button.grid(row=0, column=0, sticky='w', pady=4)
        ttk.Label(panel, textvariable=self.source_label, wraplength=560).grid(row=0, column=1, sticky='w', padx=12)
        ttk.Label(panel, text='Audiospur').grid(row=1, column=0, sticky='w', pady=4)
        self.stream = ttk.Combobox(panel, state='readonly')
        self.stream.grid(row=1, column=1, sticky='ew')
        ttk.Label(panel, text='Ausgabeformat').grid(row=2, column=0, sticky='w', pady=4)
        self.format_box = ttk.Combobox(panel, textvariable=self.format, values=('MP3', 'WAV', 'MP4'), state='readonly')
        self.format_box.grid(row=2, column=1, sticky='ew')
        self.format_box.bind('<<ComboboxSelected>>', lambda _: self.refresh_controls())

        self.video = ttk.LabelFrame(panel, text='Covervideo', padding=8)
        self.video.grid(row=3, column=0, columnspan=2, sticky='ew', pady=8)
        self.video.columnconfigure(1, weight=1)
        ttk.Button(self.video, text='Bilder wählen …', command=self.choose_images).grid(row=0, column=0, sticky='nw')
        self.image_list = tk.Listbox(self.video, height=4, exportselection=False)
        self.image_list.grid(row=0, column=1, columnspan=2, sticky='ew', padx=5)
        ttk.Button(self.video, text='↑', width=3, command=lambda: self.move_image(-1)).grid(row=0, column=3, sticky='n')
        ttk.Button(self.video, text='↓', width=3, command=lambda: self.move_image(1)).grid(row=0, column=3, sticky='s')
        ttk.Combobox(self.video, textvariable=self.size, values=('1280 × 720', '1920 × 1080'),
                     state='readonly', width=15).grid(row=1, column=1, sticky='w', pady=4)
        ttk.Checkbutton(self.video, text='Überblendungen', variable=self.fade).grid(row=1, column=2, sticky='w')

        self.bar = ttk.Progressbar(panel, mode='determinate', maximum=100)
        self.bar.grid(row=4, column=0, columnspan=2, sticky='ew', pady=6)
        ttk.Label(panel, textvariable=self.status, wraplength=650).grid(row=5, column=0, columnspan=2, sticky='w')
        self.export_button = ttk.Button(panel, text='Exportieren …', command=self.start_export)
        self.export_button.grid(row=6, column=0, sticky='w', pady=8)
        self.stop_button = ttk.Button(panel, text='Stopp', command=self.stop)
        self.stop_button.grid(row=6, column=1, sticky='w', padx=12)
        self.refresh_controls()
        self.window.after(100, self.poll)

    def refresh_controls(self):
        if self.format.get() == 'MP4':
            self.video.grid()
        else:
            self.video.grid_remove()
        self.source_button.configure(state='disabled' if self.busy else 'normal')
        self.export_button.configure(state='normal' if self.streams and not self.busy else 'disabled')
        self.stop_button.configure(state='normal' if self.busy else 'disabled')

    def close(self):
        if self.busy:
            self.stop()
        else:
            self.window.destroy()

    def stop(self):
        self.cancel.set()
        self.status.set('Stopp angefordert …')

    def run_job(self, work):
        self.cancel.clear()
        self.busy = True
        self.bar['value'] = 0
        self.refresh_controls()

        def worker():
            try:
                self.events.put(work())
            except InterruptedError:
                self.events.put(('status', 'Auftrag gestoppt.'))
            except Exception as error:
                self.events.put(('status', str(error)))

        Thread(target=worker, daemon=True).start()

    def choose_source(self):
        path = filedialog.askopenfilename(parent=self.window, title='Audio oder Video öffnen')
        if not path:
            return
        self.streams = []
        self.stream.configure(values=())
        self.stream.set('')
        self.source_label.set(Path(path).name)
        self.status.set('Lese Audiospuren …')

        def probe():
            data = inspect_media(self.ffprobe, path, self.cancel)
            if self.cancel.is_set():
                raise InterruptedError
            return 'source', (path, data)

        self.run_job(probe)

    def choose_images(self):
        images = filedialog.askopenfilenames(parent=self.window, title='Coverbilder wählen',
                                            filetypes=[('Bilder', '*.png *.jpg *.jpeg *.bmp')])
        if images:
            self.images = list(images)
            self.refresh_images()

    def refresh_images(self):
        self.image_list.delete(0, 'end')
        for path in self.images:
            self.image_list.insert('end', Path(path).name)

    def move_image(self, step):
        selection = self.image_list.curselection()
        if selection:
            index = selection[0]
            target = index + step
            if 0 <= target < len(self.images):
                self.images[index], self.images[target] = self.images[target], self.images[index]
                self.refresh_images()
                self.image_list.selection_set(target)

    def start_export(self):
        kind = self.format.get()
        selected = self.stream.current()
        if selected < 0 or not self.source or self.busy:
            return
        if kind == 'MP4' and not 1 <= len(self.images) <= 12:
            self.status.set('Bitte 1 bis 12 Bilder auswählen.')
            return
        extension = '.' + kind.lower()
        destination = filedialog.asksaveasfilename(
            parent=self.window, title='Export speichern', defaultextension=extension,
            filetypes=[(kind, '*' + extension)], initialfile=Path(self.source).stem + '_LYVRA' + extension,
        )
        if not destination:
            return
        if Path(destination).suffix.lower() != extension:
            self.status.set('Dateiendung und Ausgabeformat stimmen nicht überein.')
            return
        source, stream = self.source, self.streams[selected]['index']
        images = tuple(self.images) if kind == 'MP4' else ()
        size = (1920, 1080) if self.size.get().startswith('1920') else (1280, 720)
        fade = self.fade.get()
        self.status.set('Export startet …')

        def export():
            export_media(self.ffmpeg, self.ffprobe, source, stream, destination, self.cancel,
                         lambda *values: self.events.put(('progress', values)),
                         self.publish, images=images, size=size, fade=fade,
                         phase=lambda message: self.events.put(('phase', message)))
            return 'done', f'Geprüft und gespeichert: {destination}'

        self.run_job(export)

    def poll(self):
        while True:
            try:
                event, value = self.events.get_nowait()
            except Empty:
                break
            if event == 'phase':
                if not self.cancel.is_set():
                    self.status.set(value)
                continue
            if event == 'progress':
                if self.cancel.is_set():
                    continue
                fraction, elapsed, seconds = value
                if fraction is not None:
                    self.bar['value'] = 100 * fraction
                eta = f' · Rest ca. {elapsed * (1-fraction) / fraction:.0f} s' if fraction and fraction < .99 else ''
                self.status.set(f'{max(0, seconds):.1f} s verarbeitet · {elapsed:.0f} s Laufzeit{eta}')
                continue
            self.busy = False
            if event == 'source':
                self.source, data = value
                self.streams = [s for s in data.get('streams', []) if s.get('codec_type') == 'audio']
                self.stream.configure(values=[
                    f"#{s['index']} · {s.get('codec_name', '?')} · {s.get('channels', '?')} Kanäle · "
                    f"{s.get('tags', {}).get('language', '—')}" for s in self.streams
                ])
                if self.streams:
                    self.stream.current(0)
                duration = data.get('format', {}).get('duration', '—')
                self.status.set(f'{len(self.streams)} Audiospur(en) · Containerdauer {duration} s')
            else:
                self.status.set(value)
                if event == 'done':
                    self.bar['value'] = 100
            self.refresh_controls()
        self.window.after(100, self.poll)
