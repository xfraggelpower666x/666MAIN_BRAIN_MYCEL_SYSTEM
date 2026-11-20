"""Native PSYLLO-Oberfläche für Projektstand, Rehydration und Laufbelege."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog, ttk

from core import REPO_DIR, TOOLS_DIR, current, export_workbench, tool

BACKGROUND = "#080a16"
PANEL = "#11152a"
FIELD = "#171e37"
INK = "#e9edff"
MUTED = "#aeb9d8"
CYAN = "#3de7ff"
PINK = "#f672d7"
VIOLET = "#bd8cff"
SECTIONS = {
    "Current": ("MAIN BRAIN Current", "Pointer, Revision und Arbeitsbaum im lokalen Checkout."),
    "Checkpoint": ("Git-Rehydration", "Checkpoint und unabhängig ermittelte Projektbindung abgleichen."),
    "Laufbelege": ("Laufbelege", "Vertrag und Receipt gegen tatsächlich vorhandene Artefakte prüfen."),
    "Workbench": ("Coding Workbench", "Eine interaktive HTML-Ansicht aus einem Projekt-Datensatz exportieren."),
}


class Desktop:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.checkout = tk.StringVar(value=str(REPO_DIR))
        self.status = tk.StringVar(value="Bereit")
        data = Path.home() / ".666mainbrain"
        self.log_path = data / "desktop.log"
        root.title("666 MAIN BRAIN · PSYLLO Desktop")
        root.geometry("1020x720")
        root.minsize(820, 640)
        root.configure(background=BACKGROUND)
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.style()
        rail = ttk.Frame(root, padding=(22, 26), style="Rail.TFrame")
        rail.pack(side="left", fill="y")
        ttk.Label(rail, text="PSYLLO", style="Brand.TLabel").pack(anchor="w")
        ttk.Label(rail, text="666 MAIN BRAIN", style="Rail.TLabel").pack(anchor="w", pady=(3, 24))
        for name in SECTIONS:
            ttk.Button(rail, text=name, style="Nav.TButton",
                       command=lambda section=name: self.open(section)).pack(fill="x", pady=4)
        ttk.Label(rail, text="666SOUNDsDESIGn", style="Rail.TLabel").pack(side="bottom", anchor="w")
        self.main = ttk.Frame(root, padding=25)
        self.main.pack(side="left", fill="both", expand=True)
        self.title = ttk.Label(self.main, style="Title.TLabel")
        self.title.pack(anchor="w")
        self.description = ttk.Label(self.main, style="Muted.TLabel", wraplength=590)
        self.description.pack(anchor="w", pady=(5, 20))
        self.form = ttk.Frame(self.main)
        self.form.pack(fill="x")
        result_panel = ttk.Frame(self.main)
        result_panel.pack(expand=True, fill="both", pady=(18, 12))
        self.output = tk.Text(result_panel, bg=PANEL, fg=INK, insertbackground=CYAN,
                              borderwidth=0, padx=15, pady=11, wrap="word",
                              selectbackground="#374576", font=("Consolas", 11), state="disabled")
        scroll = ttk.Scrollbar(result_panel, command=self.output.yview)
        self.output.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.output.pack(side="left", expand=True, fill="both")
        ttk.Label(self.main, textvariable=self.status, style="Muted.TLabel", wraplength=660).pack(anchor="w")
        self.open("Current")

    def style(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background=BACKGROUND)
        style.configure("Rail.TFrame", background=PANEL)
        style.configure("TLabel", background=BACKGROUND, foreground=INK, font=("Segoe UI", 10))
        style.configure("Title.TLabel", foreground=INK, font=("Segoe UI", 25, "bold"))
        style.configure("Muted.TLabel", foreground=MUTED)
        style.configure("Rail.TLabel", background=PANEL, foreground=MUTED)
        style.configure("Brand.TLabel", background=PANEL, foreground=PINK, font=("Segoe UI", 23, "bold"))
        style.configure("TButton", background=FIELD, foreground=INK, padding=(10, 8))
        style.map("TButton", foreground=[("active", CYAN)], background=[("active", "#242f50")])
        style.configure("Nav.TButton", font=("Segoe UI", 10, "bold"), anchor="w")
        style.configure("TEntry", fieldbackground=FIELD, foreground=INK, insertcolor=CYAN,
                        bordercolor="#354474", padding=6)

    def path(self, label, *, directory=False, save=False, variable=None):
        variable = variable or tk.StringVar()
        row = ttk.Frame(self.form)
        row.pack(fill="x", pady=4)
        ttk.Label(row, text=label, width=18).pack(side="left")
        ttk.Entry(row, textvariable=variable).pack(side="left", fill="x", expand=True)

        def select():
            if directory:
                value = filedialog.askdirectory(parent=self.root)
            elif save:
                value = filedialog.asksaveasfilename(parent=self.root, defaultextension=".html",
                                                     filetypes=[("HTML", "*.html")])
            else:
                value = filedialog.askopenfilename(parent=self.root, filetypes=[("JSON", "*.json"),
                                                                              ("Alle Dateien", "*")])
            if value:
                variable.set(value)

        ttk.Button(row, text="Auswählen", command=select).pack(side="left", padx=(7, 0))
        return variable

    def open(self, section):
        for child in self.form.winfo_children():
            child.destroy()
        self.title.configure(text=SECTIONS[section][0])
        self.description.configure(text=SECTIONS[section][1])
        if section == "Current":
            self.path("MAIN-BRAIN-Checkout", directory=True, variable=self.checkout)
            commands = [("Lokal prüfen", False), ("Mit GitHub abgleichen", True)]
            for label, remote in commands:
                ttk.Button(self.form, text=label, command=lambda verify=remote: self.start(
                    label="GitHub-Abgleich" if verify else "Lokaler Current",
                    function=current, arguments=(Path(self.checkout.get()), verify),
                )).pack(side="left", padx=(0, 8), pady=12)
            return
        if section == "Checkpoint":
            fields = [self.path("Checkpoint JSON"), self.path("Projektbindung JSON"),
                      self.path("Projekt-Checkout", directory=True)]
        elif section == "Laufbelege":
            fields = [self.path("Soll-Vertrag JSON"), self.path("Receipt JSON"),
                      self.path("Artefaktordner", directory=True)]
        else:
            fields = [self.path("Projekt-Datensatz JSON"), self.path("HTML-Ziel", save=True),
                      self.path("UI-Handoff optional")]
            fields[0].set(str(TOOLS_DIR / "workbench" / "template" / "view.example.json"))
        ttk.Button(self.form, text="HTML exportieren" if section == "Workbench" else "Prüfung starten",
                   command=lambda: self.submit(section, [field.get() for field in fields])).pack(
                       anchor="w", pady=(10, 0))

    def submit(self, section, values):
        if not all(values[:2]) or (section != "Workbench" and not values[2]):
            self.status.set("OFFEN · Bitte die erforderlichen Pfade auswählen.")
            return
        if section == "Checkpoint":
            args = ("checkpoint", *values[:2], "--git-repo", values[2], "--include-worktree")
        elif section == "Laufbelege":
            args = ("receipt", *values)
        else:
            self.start(section, export_workbench, values)
            return
        self.start(section, tool, args)

    def start(self, label, function, arguments):
        if getattr(self, "pending", False):
            self.status.set("Eine Prüfung läuft bereits.")
            return
        self.pending = True
        self.status.set(f"Läuft · {label}")
        future = self.executor.submit(function, *arguments)

        def collect():
            if not future.done():
                self.root.after(75, collect)
                return
            self.pending = False
            try:
                result = future.result()
                if isinstance(result, dict):
                    text = "\n\n".join(f"{key}\n{value}" for key, value in result.items())
                    state = "Abgeschlossen"
                else:
                    text = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
                    state = f"Exitcode {result.returncode}"
            except (OSError, ValueError, RuntimeError, TimeoutError) as error:
                state, text = "OFFEN", str(error)
            except Exception as error:
                state, text = "Fehler", str(error)
            self.output.configure(state="normal")
            self.output.delete("1.0", "end")
            self.output.insert("1.0", text or "Keine Ausgabe.")
            self.output.configure(state="disabled")
            try:
                self.log_path.parent.mkdir(parents=True, exist_ok=True)
                with self.log_path.open("a", encoding="utf-8") as stream:
                    stream.write(f"{datetime.now().isoformat(timespec='seconds')} {label}: {state}\n")
                self.status.set(f"{label} · {state} · Log: {self.log_path}")
            except OSError as error:
                self.status.set(f"{label} · {state} · Log nicht verfügbar: {error}")
        self.root.after(75, collect)

    def close(self):
        self.executor.shutdown(wait=False, cancel_futures=True)
        self.root.destroy()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Integrationsdateien und Git auslesen")
    options = parser.parse_args()
    if options.check:
        try:
            report = current(REPO_DIR)
        except (OSError, ValueError, RuntimeError) as error:
            print(error, file=sys.stderr)
            return 1
        print(json.dumps(report, ensure_ascii=True, indent=2))
        paths = [
            "checkpoint/scripts/checkpoint_review.py", "run/scripts/check_run_evidence.py",
            "workbench/scripts/render_ui.py", "workbench/template/view.example.json",
            *(f"workbench/assets/{asset}" for asset in (
                "ui-template.html", "visualform-menu.html", "charts.html",
                "visual-daemon.html", "companion.js",
            )),
        ]
        missing = [path for path in paths if not (TOOLS_DIR / path).is_file()]
        if missing:
            print("Missing integration: " + ", ".join(missing), file=sys.stderr)
            return 1
        return 0
    root = tk.Tk()
    Desktop(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
