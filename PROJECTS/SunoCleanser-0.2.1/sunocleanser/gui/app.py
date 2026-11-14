from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from sunocleanser.suno.pipeline import (
    ProcessingParams,
    ProcessingResult,
    process_suno_wav,
)

OUT_DIR = Path(os.environ.get("SUNOCLEANSER_OUT", "out")).resolve()

TRANSLATIONS = {
    "English": {
        "language": "Language",
        "input": "Input audio",
        "browse": "Browse…",
        "title": "Title (output file names)",
        "output": "Output: out/ folder (local only)",
        "process": "Process",
        "open_output": "Open out/",
        "select_audio": "Select audio",
        "all_files": "All files",
        "folder": "Folder: {path}",
        "invalid_audio": "Select a valid WAV or MP3 file.",
        "processing": "Processing…",
        "clean": "Clean: {name}",
        "noise": "Noise: {name}",
        "done": "Done. Check the out/ folder.",
        "error": "Error: {message}",
    },
    "Español": {
        "language": "Idioma",
        "input": "Audio de entrada",
        "browse": "Examinar…",
        "title": "Título (nombres de salida)",
        "output": "Salida: carpeta out/ (solo local)",
        "process": "Procesar",
        "open_output": "Abrir out/",
        "select_audio": "Seleccionar audio",
        "all_files": "Todos",
        "folder": "Carpeta: {path}",
        "invalid_audio": "Selecciona un archivo WAV o MP3 válido.",
        "processing": "Procesando…",
        "clean": "Limpio: {name}",
        "noise": "Ruido: {name}",
        "done": "Listo. Revisa la carpeta out/.",
        "error": "Error: {message}",
    },
}


class SunoCleanserApp:
    BG = "#080913"
    PANEL = "#12132a"
    FIELD = "#191d38"
    CYAN = "#31eaff"
    PINK = "#ff37d1"
    VIOLET = "#a476ff"
    TEXT = "#f3efff"

    def __init__(self, root: tk.Tk, initial_wav: Path | None = None) -> None:
        self.root = root
        self.root.title("SunoCleanser")
        self.root.minsize(520, 380)
        self.root.configure(bg=self.BG)

        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure(
            "Cleanser.TCombobox",
            fieldbackground=self.FIELD,
            foreground=self.TEXT,
            background=self.PANEL,
            arrowcolor=self.CYAN,
        )
        style.map(
            "Cleanser.TCombobox",
            fieldbackground=[("readonly", self.FIELD)],
            foreground=[("readonly", self.TEXT)],
            selectbackground=[("readonly", "#563282")],
            selectforeground=[("readonly", "#ffffff")],
        )

        self.language_var = tk.StringVar(value="English")
        self.text_vars = {
            key: tk.StringVar(value=value)
            for key, value in TRANSLATIONS["English"].items()
        }
        self.wav_var = tk.StringVar()
        self.title_var = tk.StringVar()
        self._processing = False

        frame = tk.Frame(root, padx=12, pady=12, bg=self.BG)
        frame.pack(fill=tk.BOTH, expand=True)

        language_row = tk.Frame(frame, bg=self.BG)
        language_row.grid(row=0, column=0, columnspan=2, sticky="e", pady=(0, 10))
        tk.Label(
            language_row,
            textvariable=self.text_vars["language"],
            bg=self.BG,
            fg=self.CYAN,
        ).pack(side=tk.LEFT)
        language_selector = ttk.Combobox(
            language_row, textvariable=self.language_var,
            values=list(TRANSLATIONS), state="readonly", width=12,
            style="Cleanser.TCombobox",
        )
        language_selector.pack(side=tk.LEFT, padx=(8, 0))
        language_selector.bind("<<ComboboxSelected>>", self._change_language)

        tk.Label(frame, textvariable=self.text_vars["input"], bg=self.BG, fg=self.CYAN).grid(
            row=1, column=0, sticky="w"
        )
        entry_row = tk.Frame(frame, bg=self.BG)
        entry_row.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(2, 0))
        tk.Entry(
            entry_row,
            textvariable=self.wav_var,
            bg=self.FIELD,
            fg=self.TEXT,
            insertbackground=self.CYAN,
            selectbackground="#563282",
            selectforeground="#ffffff",
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self.VIOLET,
            highlightcolor=self.CYAN,
        ).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        tk.Button(
            entry_row,
            textvariable=self.text_vars["browse"],
            command=self._browse,
            bg=self.PANEL,
            fg=self.CYAN,
            activebackground="#302050",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=(8, 0))

        tk.Label(frame, textvariable=self.text_vars["title"], bg=self.BG, fg=self.CYAN).grid(
            row=3, column=0, sticky="w", pady=(10, 0)
        )
        tk.Entry(
            frame,
            textvariable=self.title_var,
            bg=self.FIELD,
            fg=self.TEXT,
            insertbackground=self.CYAN,
            selectbackground="#563282",
            selectforeground="#ffffff",
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self.VIOLET,
            highlightcolor=self.CYAN,
        ).grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(2, 0)
        )

        tk.Label(frame, textvariable=self.text_vars["output"], bg=self.BG, fg=self.PINK).grid(
            row=5, column=0, sticky="w", pady=(10, 0)
        )

        actions = tk.Frame(frame, bg=self.BG)
        actions.grid(row=6, column=0, columnspan=2, sticky="w", pady=12)
        self.run_btn = tk.Button(
            actions,
            textvariable=self.text_vars["process"],
            command=self._start,
            bg=self.PINK,
            fg=self.BG,
            activebackground="#ff70db",
            activeforeground=self.BG,
            disabledforeground="#493b50",
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
        )
        self.run_btn.pack(side=tk.LEFT)
        tk.Button(
            actions,
            textvariable=self.text_vars["open_output"],
            command=self._open_out,
            bg=self.PANEL,
            fg=self.CYAN,
            activebackground="#302050",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=10,
            pady=6,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=8)

        self.log = scrolledtext.ScrolledText(
            frame,
            height=14,
            state=tk.DISABLED,
            bg=self.FIELD,
            fg=self.TEXT,
            insertbackground=self.CYAN,
            selectbackground="#563282",
            selectforeground="#ffffff",
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self.VIOLET,
            highlightcolor=self.CYAN,
        )
        self.log.grid(row=7, column=0, columnspan=2, sticky="nsew")
        self.log.vbar.configure(
            bg=self.PANEL,
            activebackground=self.VIOLET,
            troughcolor=self.BG,
            highlightthickness=0,
            bd=0,
        )

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(7, weight=1)

        if initial_wav is not None:
            self._set_wav(initial_wav)

    def _text(self, key: str, **values: object) -> str:
        return TRANSLATIONS[self.language_var.get()][key].format(**values)

    def _change_language(self, event: object = None) -> None:
        for key, value in TRANSLATIONS[self.language_var.get()].items():
            self.text_vars[key].set(value)

    def _set_wav(self, path: Path) -> None:
        self.wav_var.set(str(path))
        if not self.title_var.get().strip():
            self.title_var.set(path.stem)

    def _log(self, message: str) -> None:
        self.log.configure(state=tk.NORMAL)
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)
        self.log.configure(state=tk.DISABLED)

    def _browse(self) -> None:
        chosen = filedialog.askopenfilename(
            title=self._text("select_audio"),
            filetypes=[("WAV and MP3", "*.wav *.mp3"), (self._text("all_files"), "*.*")],
        )
        if chosen:
            self._set_wav(Path(chosen))

    def _open_out(self) -> None:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        folder = OUT_DIR.resolve()
        try:
            if sys.platform == "win32":
                os.startfile(folder)
                opened = True
            else:
                launcher = "open" if sys.platform == "darwin" else "xdg-open"
                opened = subprocess.run([launcher, folder], check=False).returncode == 0
        except OSError:
            opened = False
        if not opened:
            messagebox.showinfo("SunoCleanser", self._text("folder", path=folder))

    def _start(self) -> None:
        if self._processing:
            return
        wav = Path(self.wav_var.get().strip())
        if not wav.is_file():
            messagebox.showerror("SunoCleanser", self._text("invalid_audio"))
            return

        title = self.title_var.get().strip() or wav.stem
        self._processing = True
        self.run_btn.configure(state=tk.DISABLED)
        self._log(self._text("processing"))

        thread = threading.Thread(
            target=self._worker,
            args=(wav, title),
            daemon=True,
        )
        thread.start()

    def _worker(self, wav: Path, title: str) -> None:
        try:
            report_path = OUT_DIR / f"{wav.stem}.report.json"
            result = process_suno_wav(
                input_path=wav,
                out_dir=OUT_DIR,
                title=title,
                params=ProcessingParams(),
                report_path=report_path,
            )
            self.root.after(0, lambda r=result: self._finish_ok(r))
        except Exception as exc:  # noqa: BLE001
            # Keep unexpected processing errors inside the user-facing boundary.
            self.root.after(0, lambda msg=str(exc): self._finish_err(msg))

    def _finish_ok(self, result: ProcessingResult) -> None:
        self._log(json.dumps(result.report, indent=2))
        self._log(self._text("clean", name=result.clean_path.name))
        self._log(self._text("noise", name=result.noise_path.name))
        self._processing = False
        self.run_btn.configure(state=tk.NORMAL)
        messagebox.showinfo("SunoCleanser", self._text("done"))

    def _finish_err(self, message: str) -> None:
        self._log(self._text("error", message=message))
        self._processing = False
        self.run_btn.configure(state=tk.NORMAL)
        messagebox.showerror("SunoCleanser", message)


def run_app(argv: list[str] | None = None) -> None:
    initial: Path | None = None
    if argv:
        candidate = Path(argv[0])
        if candidate.is_file():
            initial = candidate

    root = tk.Tk()
    SunoCleanserApp(root, initial_wav=initial)
    root.mainloop()
