"""666SOUNDsDESIGn – Windows-Projektstarter, © 2026 FRAGGLEPOWER666."""
from __future__ import annotations

import argparse
from datetime import datetime
import contextlib
import json
import locale
import os
from pathlib import Path
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading

from packaging_tools import package

TITLE = "666 TOOLSTARTER"
VERSION = "1.0.1"
COPYRIGHT = "© 2026 666SOUNDsDESIGn - FRAGGLEPOWER666"
BASE = Path(__file__).resolve().parent
WINDOWS = os.name == "nt"
ELECTRON_OVERRIDES = {
    "electron_run_as_node", "electron_override_dist_path",
    "electron_skip_binary_download", "electron_install_platform",
    "electron_install_arch", "npm_config_platform", "npm_config_arch",
    "npm_config_target_platform", "npm_config_target_arch",
    "npm_config_electron_skip_binary_download",
}
RESULT = {
    "function": ("Check, repair, launch and package project tools", "Projektwerkzeuge prüfen, reparieren, starten und paketieren"),
    "diagnose": ("Diagnose", "Diagnose"),
    "package": ("Package", "Paket bauen"),
    "logs": ("Open logs", "Logs öffnen"),
    "empty": ("No tools configured in this profile.", "In diesem Profil sind keine Werkzeuge konfiguriert."),
    "checked": ("All required checks passed.", "Alle Pflichtprüfungen bestanden."),
    "blocked": ("Required tools are unavailable.", "Pflichtwerkzeuge fehlen oder sind defekt."),
    "fix": ("Attempting repair", "Reparaturversuch"),
    "ok": ("Ready", "Bereit"),
    "missing": ("Missing or failed", "Fehlt oder fehlerhaft"),
    "optional": ("Optional", "Optional"),
    "check": ("Check", "Prüfen"),
    "repair": ("Install / repair", "Installieren / reparieren"),
    "run": ("Repair & run", "Selbstheilung & Start"),
    "busy": ("Working…", "Vorgang läuft…"),
    "profile": ("Profile", "Profil"),
    "action": ("Project action", "Projektaktion"),
    "browse": ("Browse…", "Auswählen…"),
    "exit": ("Exit code", "Exitcode"),
    "lock": ("Another operation is using this project.", "Ein anderer Vorgang nutzt dieses Projekt."),
    "complete": ("Operation complete.", "Vorgang abgeschlossen."),
}


class SetupError(Exception):
    pass


def display(code: str, lang: str) -> str:
    return RESULT[code][lang == "de"]


def introduction(lang):
    return f"{TITLE} v{VERSION} | {display('function', lang)} | {COPYRIGHT}"


def log_dir():
    base = os.environ.get("LOCALAPPDATA") if WINDOWS else None
    return (Path(base) if base else Path.home() / ".local/state") / "666SOUNDsDESIGn" / "ToolStarter" / "logs"


def redact(message):
    message = re.sub(r"(https?://)[^/\s@]+@", r"\1[REDACTED]@", message, flags=re.I)
    message = re.sub(
        r"(\b(?:authorization|token|password|secret|api[_-]?key|_authToken)\b[\s:=]+)(?:Bearer\s+)?[^\s&,\"';]+",
        r"\1[REDACTED]", message, flags=re.I,
    )
    return re.sub(r"\b(?:gh[pousr]_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{16,})",
                  "[REDACTED]", message)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def paths(*items: str) -> str:
    return os.pathsep.join(dict.fromkeys(p for item in items for p in item.split(os.pathsep) if p))


def registry_path() -> str:
    if not WINDOWS:
        return ""
    import winreg

    values = []
    for hive, subkey in (
        (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
        (winreg.HKEY_CURRENT_USER, r"Environment"),
    ):
        with contextlib.suppress(OSError), winreg.OpenKey(hive, subkey) as key:
            values.append(os.path.expandvars(winreg.QueryValueEx(key, "Path")[0]))
    return paths(*values)


@contextlib.contextmanager
def project_lock(root: Path):
    # Betriebssystem-Lock wird auch nach einem Prozessabbruch freigegeben.
    with (root / ".toolstarter.lock").open("a+b") as handle:
        if WINDOWS:
            import msvcrt
            handle.seek(0)
            lock = lambda: msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            lock = lambda: fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            lock()
        except OSError as exc:
            raise SetupError("PROJECT_LOCK") from exc
        yield


class Starter:
    def __init__(self, profile: Path, lang: str, log):
        self.config = load_json(profile)
        self.lang = lang
        self.log = log
        self.root = (profile.parent / self.config.get("project_root", ".")).resolve()
        self.env = os.environ.copy()
        if self.config.get("clean_electron_env", any(
            tool.get("kind") == "electron" for tool in self.config.get("tools", [])
        )):
            self.env = {k: v for k, v in self.env.items() if k.lower() not in ELECTRON_OVERRIDES}
        self.initial_path = self.env.get("PATH", "")
        self.tool_paths: dict[str, Path] = {}
        self.refresh_path()

    def label(self, key):
        return display(key, self.lang)

    def refresh_path(self):
        local = self.env.get("LOCALAPPDATA")
        program_files = self.env.get("ProgramFiles")
        system = self.env.get("SystemRoot")
        candidates = [str(p.parent) for p in self.tool_paths.values()]
        candidates.extend(str((self.root / p).resolve()) for p in self.config.get("path_dirs", []))
        if WINDOWS and local:
            candidates.extend(str(Path(local) / p) for p in (
                r"Microsoft\WinGet\Links", r"Microsoft\WindowsApps", r"Programs\nodejs",
            ))
        if WINDOWS and program_files:
            candidates.extend(str(Path(program_files) / p) for p in ("nodejs", r"PowerShell\7", "Git/cmd"))
        if WINDOWS and system:
            candidates.append(str(Path(system) / r"System32\WindowsPowerShell\v1.0"))
        self.env["PATH"] = paths(*candidates, self.initial_path, registry_path())

    def resolve(self, name: str) -> Path:
        if name.startswith("@"):
            return self.tool_paths[name[1:]]
        path = Path(name)
        if path.is_absolute() or len(path.parts) > 1 or name.startswith(("./", ".\\")):
            path = self.root / path
        else:
            found = shutil.which(name, path=self.env["PATH"])
            if not found:
                raise SetupError(f"{name} (PATH)")
            path = Path(found)
        if not path.is_file():
            raise SetupError(str(path))
        return path.absolute()

    def command(self, argv: list[str]) -> list[str]:
        if not argv or not all(isinstance(arg, str) for arg in argv):
            raise SetupError("Expected a nonempty array of command arguments.")
        if argv[0] == "npm" and WINDOWS:
            node = self.resolve("node.exe")
            # npm.cmd ist ein Wrapper. Der direkte CLI-Aufruf braucht kein cmd.exe.
            candidates = [node.parent / "node_modules/npm/bin/npm-cli.js"]
            wrapper = shutil.which("npm.cmd", path=self.env["PATH"])
            if wrapper:
                candidates.append(Path(wrapper).parent / "node_modules/npm/bin/npm-cli.js")
            cli = next((candidate for candidate in candidates if candidate.is_file()), None)
            if cli is None:
                raise SetupError("npm-cli.js (Node.js / npm)")
            return [str(node), str(cli), *argv[1:]]
        if argv[0] == "@python":
            return [sys.executable, *argv[1:]]
        executable = self.resolve(argv[0])
        if WINDOWS and executable.suffix.lower() in (".cmd", ".bat", ".ps1"):
            raise SetupError(f"{executable.name}: use a native executable, node, or powershell -File.")
        return [str(executable), *argv[1:]]

    def execute(self, argv, *, quiet=False, timeout=None):
        cmd = self.command(argv)
        options = dict(cwd=self.root, env=self.env, stderr=subprocess.STDOUT,
                       encoding=locale.getpreferredencoding(False), errors="replace",
                       creationflags=subprocess.CREATE_NO_WINDOW if WINDOWS else 0)
        if quiet:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, timeout=timeout or 30, **options)
            return result.returncode, result.stdout
        self.log(f"> {Path(cmd[0]).name} ({argv[0]})")
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, **options) as process:
            for line in process.stdout:
                self.log(line.rstrip())
            code = process.wait()
        self.log(f"{self.label('exit')}: {code}")
        return code, ""

    def probe(self, command, match=None):
        try:
            code, output = self.execute(command, quiet=True)
        except (OSError, KeyError, SetupError, subprocess.TimeoutExpired) as exc:
            return False, str(exc)
        if code == 0 and (not match or re.search(match, output, re.MULTILINE)):
            return True, output.strip().splitlines()[0] if output.strip() else ""
        return False, f"{self.label('exit')}: {code} | {output.strip()[-640:]}"

    def locked_version(self, package_name):
        lock = load_json(self.root / "package-lock.json")
        return lock["packages"][f"node_modules/{package_name}"]["version"]

    def require_electron_version(self, name):
        version = self.locked_version(name)
        if not re.match(r"^[0-9]+\.", version) or int(version.split(".", 1)[0]) <= 3:
            raise SetupError(f"{name} {version}: Electron 3.x and earlier are blocked. "
                             "Use a supported project version in package.json and package-lock.json.")
        return version

    def exact_version(self, package_name):
        version = self.locked_version(package_name)
        installed = load_json(self.root / "node_modules" / package_name / "package.json")
        if installed["version"] != version:
            raise SetupError(f"{package_name}: {installed['version']} != {version}")
        return version

    def npm_probe(self, tool):
        packages = set(tool.get("locked_packages", []))
        if tool.get("all_locked_dev"):
            packages.update(load_json(self.root / "package.json").get("devDependencies", {}))
        for package_name in sorted(packages):
            self.exact_version(package_name)
        for filename in tool.get("files", []):
            self.resolve(filename)
        return self.probe(["npm", "ls", "--all", "--include=dev"])

    def electron_probe(self, tool):
        package = tool.get("package", "electron")
        version = self.exact_version(package)
        hook = tool.get("check")
        if hook:
            ok, detail = self.probe(hook)
            if not ok:
                return ok, detail
        package_dir = self.root / "node_modules" / package
        marker = package_dir / "path.txt"
        if marker.is_file():
            binary = marker.read_text(encoding="utf-8").strip()
        else:
            binary = "electron.exe" if WINDOWS else "electron"
        if binary not in ("electron.exe", "electron"):
            raise SetupError(f"Unsupported Electron executable in {marker.name}: {binary}")
        exe = package_dir / "dist" / binary
        return self.probe([str(exe), "--version"], rf"^v?{re.escape(version)}\s*$")

    def executable_probe(self, tool):
        for name in tool["names"]:
            ok, detail = self.probe([name, *tool.get("args", ["--version"])], tool.get("match"))
            if ok:
                self.tool_paths[tool["id"]] = self.resolve(name)
                self.refresh_path()
                return ok, f"{self.tool_paths[tool['id']]} | {detail}"
        return False, detail

    def audio_probe(self, tool):
        # Lokale Paare werden gemeinsam geprüft. PATH dient als weitere Quelle.
        directories = [(self.root / p).resolve() for p in self.config.get("path_dirs", [])]
        suffix = ".exe" if WINDOWS else ""
        directories.extend(Path(entry) for entry in self.env["PATH"].split(os.pathsep) if entry)
        candidates = [
            (directory.absolute() / f"ffmpeg{suffix}", directory.absolute() / f"ffprobe{suffix}")
            for directory in dict.fromkeys(directories) if directory.is_absolute()
        ]
        # Separate Installationsorte bleiben als letzte Aufloesungsoption erlaubt.
        candidates.append(("ffmpeg", "ffprobe"))
        detail = "ffmpeg / ffprobe"
        for ffmpeg, ffprobe in candidates:
            ok, detail = self.probe([str(ffmpeg), "-version"], r"^ffmpeg version ")
            if not ok:
                continue
            ok, detail = self.probe([str(ffprobe), "-version"], r"^ffprobe version ")
            if not ok:
                continue
            ok, detail = self.audio_sample(str(ffmpeg), str(ffprobe))
            if ok:
                ffmpeg_path, ffprobe_path = self.resolve(str(ffmpeg)), self.resolve(str(ffprobe))
                self.tool_paths.update(ffmpeg=ffmpeg_path, ffprobe=ffprobe_path)
                self.env["FFMPEG_PATH"] = str(ffmpeg_path)
                self.env["FFPROBE_PATH"] = str(ffprobe_path)
                self.refresh_path()
                return True, f"{ffmpeg_path} | {ffprobe_path}"
        return False, detail

    def audio_sample(self, ffmpeg, ffprobe):
        with tempfile.TemporaryDirectory(prefix="666-audio-") as temp:
            sample = str(Path(temp) / "probe.wav")
            ok, detail = self.probe([
                str(ffmpeg), "-hide_banner", "-loglevel", "error", "-f", "lavfi",
                "-i", "anullsrc=r=44100:cl=mono", "-t", "0.10", "-c:a", "pcm_s16le", sample,
            ])
            if ok:
                ok, detail = self.probe([
                    str(ffprobe), "-v", "error", "-select_streams", "a:0",
                    "-show_entries", "stream=codec_name,sample_rate",
                    "-of", "default=noprint_wrappers=1", sample,
                ], r"\Acodec_name=pcm_s16le\s+sample_rate=44100\s*\Z")
        return ok, detail

    def verify(self, tool):
        try:
            return {
                "exe": self.executable_probe, "audio": self.audio_probe,
                "npm": self.npm_probe, "electron": self.electron_probe,
            }[tool["kind"]](tool)
        except (OSError, KeyError, ValueError, SetupError) as exc:
            return False, str(exc)

    def repair(self, tool):
        if "repair" in tool:
            command = tool["repair"]
        elif "winget" in tool:
            if not WINDOWS:
                raise SetupError("WinGet requires Windows.")
            package = tool["winget"]
            installed, _ = self.probe(["winget.exe", "list", "--id", package, "--exact",
                                       "--source", "winget", "--disable-interactivity"],
                                      rf"(?<![\w.]){re.escape(package)}(?![\w.])")
            # Ein registriertes, aber im Test defektes Paket einmal neu installieren.
            command = ["winget.exe", "install", "--id", package, "--exact", "--source", "winget",
                       "--accept-package-agreements", "--accept-source-agreements",
                       "--silent", "--disable-interactivity"]
            if installed:
                command.append("--force")
        elif tool["kind"] == "npm":
            command = ["npm", "ci", "--include=dev", "--foreground-scripts",
                       "--ignore-scripts=false", "--no-audit", "--no-fund"]
        elif tool["kind"] == "electron":
            package_dir = self.root / "node_modules" / tool.get("package", "electron")
            installers = (package_dir / "install.js", package_dir / "bin/install.js")
            installer = next((path for path in installers if path.is_file()), None)
            if not installer:
                npm_bin = load_json(package_dir / "package.json").get("bin", {})
                if not isinstance(npm_bin, dict) or "install-electron" not in npm_bin:
                    raise SetupError("Electron install.js / install-electron")
                installer = package_dir / npm_bin["install-electron"]
            return self.reinstall_electron(tool, package_dir, installer)
        else:
            raise SetupError("No repair command configured.")
        code, _ = self.execute(command)
        self.refresh_path()
        return code

    def reinstall_electron(self, tool, package_dir, installer):
        # Alte Installer überspringen eine Runtime, deren interne Versionsdatei noch stimmt.
        # Vorhandene Dateien bleiben bis zur erfolgreichen Gegenprobe gesichert.
        backup = Path(tempfile.mkdtemp(prefix=".toolstarter-electron-", dir=package_dir))
        old = []
        installed = False
        staging_complete = False
        try:
            for name in ("dist", "path.txt"):
                current = package_dir / name
                if current.exists() or current.is_symlink():
                    current.rename(backup / name)
                    old.append(name)
            staging_complete = True
            code, _ = self.execute(["node", str(installer)])
            installed = code == 0 and self.verify(tool)[0]
            return 0 if installed else (code or 1)
        finally:
            if not installed:
                if staging_complete:
                    for name in ("dist", "path.txt"):
                        current = package_dir / name
                        if current.is_dir() and not current.is_symlink():
                            shutil.rmtree(current)
                        elif current.exists() or current.is_symlink():
                            current.unlink()
                for name in old:
                    (backup / name).rename(package_dir / name)
            shutil.rmtree(backup)

    def preflight(self):
        if not self.root.is_dir():
            raise SetupError(str(self.root))
        for file in self.config.get("required_files", []):
            if not (self.root / file).is_file():
                raise SetupError(f"{self.label('missing')}: {self.root / file}")

    def check_all(self, repair=False, repair_optional=False):
        failed = set()
        required_ok = True
        for tool in self.config.get("tools", []):
            name = tool["id"]
            required = tool.get("required", True)
            missing_deps = failed.intersection(tool.get("after", []))
            if missing_deps:
                ok, detail = False, ", ".join(sorted(missing_deps))
            else:
                ok, detail = self.verify(tool)
            if not ok and repair and (required or repair_optional) and not missing_deps:
                self.log(f"[{self.label('fix')}] {name} | {detail}")
                try:
                    code = self.repair(tool)
                except (OSError, KeyError, ValueError, SetupError) as exc:
                    self.log(str(exc))
                    code = 1
                checked, detail = self.verify(tool)
                ok = code == 0 and checked
                if code:
                    detail = f"{self.label('exit')}: {code} | {detail}"
            if not ok:
                failed.add(name)
                required_ok &= not required
            status = "ok" if ok else ("missing" if required else "optional")
            self.log(f"[{self.label(status)}] {name} | {detail}")
        return required_ok

    def start(self, mode, action=None):
        if mode == "diagnose":
            self.log(f"Python {sys.version.split()[0]} | {sys.executable}")
            self.log(f"Platform: {sys.platform} | Project: {self.root}")
            configured = self.config.get("tools", [])
            if any("winget" in item for item in configured):
                name = "winget.exe"
                self.log(f"{name}: {shutil.which(name, path=self.env['PATH']) or self.label('missing')}")
            if "package" in self.config:
                self.log(f"ISCC: {self.config['package'].get('iscc') or shutil.which('ISCC.exe', path=self.env['PATH']) or self.label('missing')}")
        self.preflight()
        for tool in self.config.get("tools", []):
            if tool.get("kind") == "electron":
                self.require_electron_version(tool.get("package", "electron"))
        actions = self.config.get("actions", {})
        if mode == "run" and action not in actions:
            raise SetupError(f"{self.label('action')}: {action!r} | {', '.join(actions)}")
        guard = project_lock(self.root) if mode in ("repair", "run", "package") else contextlib.nullcontext()
        with guard:
            if mode == "package":
                if not WINDOWS:
                    raise SetupError("Windows is required to run the bundled Windows probes and build Setup.")
                if "package" not in self.config:
                    raise SetupError("This profile has no package configuration.")
                return package(self, action)
            heal = mode == "repair" or (mode == "run" and self.config.get("self_heal_on_run", True))
            if not self.check_all(heal, repair_optional=mode == "repair"):
                self.log(self.label("blocked"))
                return 1
            self.log(self.label("checked" if self.config.get("tools") else "empty"))
            if mode != "run":
                return 0
            selected = actions[action]
            for command in [*self.config.get("before_actions", []), *selected["commands"]]:
                code, _ = self.execute(command)
                if code:
                    return code
            for file in selected.get("artifacts", []):
                output = self.root / file
                if not output.is_file() or output.stat().st_size == 0:
                    raise SetupError(f"{self.label('missing')}: {output}")
                self.log(f"[{self.label('ok')}] {output}")
            self.log(self.label("complete"))
            return 0


def run_profile(profile, lang, mode, action=None, log=print):
    try:
        directory = log_dir()
        directory.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S-%f")
        logfile = directory / f"{stamp}-{os.getpid()}-{mode}.log"
        with logfile.open("x", encoding="utf-8", buffering=1) as handle:
            def report(message):
                clean = redact(str(message))
                handle.write(f"{datetime.now().astimezone().isoformat(timespec='seconds')} {clean}\n")
                log(clean)

            report(introduction(lang))
            report(f"Log: {logfile}")
            report(f"{mode} | {profile}")
            try:
                code = Starter(profile, lang, report).start(mode, action)
            except (OSError, KeyError, TypeError, ValueError, SetupError, AttributeError) as exc:
                report(display("lock", lang) if str(exc) == "PROJECT_LOCK" else f"ERROR: {exc}")
                code = 1
            report(f"{display('exit', lang)}: {code}")
            return code
    except OSError as exc:
        log(f"ERROR: {redact(str(exc))}")
        return 1


def gui(profile, lang):
    import tkinter as tk
    from tkinter import filedialog, ttk

    root = tk.Tk()
    root.title(f"{TITLE} v{VERSION} · {COPYRIGHT}")
    root.geometry("880x560")
    root.minsize(580, 420)
    frame = ttk.Frame(root, padding=16)
    frame.pack(fill="both", expand=True)
    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(5, weight=1)
    selected = tk.StringVar(value=str(profile))
    language = tk.StringVar(value=lang)
    action = tk.StringVar()
    status = tk.StringVar()
    subtitle = ttk.Label(frame, wraplength=510)
    subtitle.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))
    profile_label = ttk.Label(frame)
    profile_label.grid(row=1, column=0, sticky="w")
    path_entry = ttk.Entry(frame, textvariable=selected, state="readonly")
    path_entry.grid(row=1, column=1, sticky="ew", padx=8)
    action_label = ttk.Label(frame)
    action_label.grid(row=2, column=0, sticky="w", pady=8)
    action_box = ttk.Combobox(frame, textvariable=action, state="readonly")
    action_box.grid(row=2, column=1, sticky="ew", padx=8)
    languages = ttk.Combobox(frame, textvariable=language, values=("en", "de"),
                             state="readonly", width=6)
    languages.grid(row=2, column=2, sticky="e")
    buttons = ttk.Frame(frame)
    buttons.grid(row=3, column=0, columnspan=3, sticky="w", pady=(4, 12))
    ttk.Label(frame, textvariable=status).grid(row=4, column=0, columnspan=3, sticky="w")
    output_frame = ttk.Frame(frame)
    output_frame.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=(6, 0))
    output = tk.Text(output_frame, wrap="word", bg="#111827", fg="#f1f5f9",
                     padx=10, pady=8, state="disabled")
    scroll = ttk.Scrollbar(output_frame, command=output.yview)
    output.configure(yscrollcommand=scroll.set)
    scroll.pack(side="right", fill="y")
    output.pack(side="left", fill="both", expand=True)
    output.tag_configure("ok", foreground="#6ee7b7")
    output.tag_configure("warn", foreground="#fcd34d")
    messages = queue.Queue()
    busy = False
    can_package = False

    def line(message):
        tag = ""
        if message.startswith(("[Ready]", "[Bereit]")):
            tag = "ok"
        elif message.startswith(("ERROR:", "[Missing", "[Fehlt", "[Optional", "[Reparatur", "[Attempt")):
            tag = "warn"
        output.configure(state="normal")
        output.insert("end", message + "\n", tag)
        output.see("end")
        output.configure(state="disabled")

    def choose():
        filename = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if filename:
            selected.set(filename)
            update_actions()

    def update_actions():
        nonlocal can_package
        can_package = False
        try:
            config = load_json(Path(selected.get()))
            names = list(config.get("actions", {}))
            can_package = "package" in config
        except (OSError, ValueError, AttributeError) as exc:
            line(f"ERROR: {exc}")
            names = []
        action_box.configure(values=names)
        action.set(names[0] if names else "")
        controls()

    def controls():
        for button in (check_btn, repair_btn, browse_btn, diagnose_btn):
            button.configure(state="disabled" if busy else "normal")
        package_btn.configure(state="disabled" if busy or not can_package else "normal")
        run_btn.configure(state="disabled" if busy or not action.get() else "normal")
        action_box.configure(state="disabled" if busy else "readonly")
        languages.configure(state="disabled" if busy else "readonly")

    def translate(_event=None):
        subtitle.configure(text=display("function", language.get()))
        for widget, text in ((profile_label, "profile"), (action_label, "action"),
                             (check_btn, "check"), (repair_btn, "repair"),
                             (run_btn, "run"), (browse_btn, "browse"), (diagnose_btn, "diagnose"),
                             (package_btn, "package"), (logs_btn, "logs")):
            widget.configure(text=display(text, language.get()))

    def launch(mode):
        nonlocal busy
        busy = True
        controls()
        lang_now, path_now, action_now = language.get(), Path(selected.get()), action.get()
        if mode == "package":
            action_now = "both"
        status.set(display("busy", lang_now))
        output.configure(state="normal")
        output.delete("1.0", "end")
        output.configure(state="disabled")

        def work():
            code = 1
            try:
                code = run_profile(path_now, lang_now, mode, action_now,
                                   lambda message: messages.put(("line", message)))
            finally:
                messages.put(("done", code))

        threading.Thread(target=work, daemon=True).start()

    def poll():
        nonlocal busy
        for _ in range(100):
            try:
                kind, value = messages.get_nowait()
            except queue.Empty:
                break
            if kind == "line":
                line(value)
            else:
                busy = False
                status.set(f"{display('exit', language.get())}: {value}")
                controls()
        root.after(80, poll)

    def close():
        if not busy:
            root.destroy()
        else:
            root.bell()

    check_btn = ttk.Button(buttons, command=lambda: launch("check"))
    repair_btn = ttk.Button(buttons, command=lambda: launch("repair"))
    run_btn = ttk.Button(buttons, command=lambda: launch("run"))
    diagnose_btn = ttk.Button(buttons, command=lambda: launch("diagnose"))
    package_btn = ttk.Button(buttons, command=lambda: launch("package"))

    def open_logs():
        directory = log_dir()
        directory.mkdir(parents=True, exist_ok=True)
        try:
            if WINDOWS:
                os.startfile(directory)
            else:
                line(str(directory))
        except OSError as exc:
            line(f"ERROR: {exc}")

    logs_btn = ttk.Button(buttons, command=open_logs)
    for index, button in enumerate((check_btn, repair_btn, run_btn, diagnose_btn, package_btn, logs_btn)):
        button.grid(row=index // 3, column=index % 3, sticky="ew", padx=(0, 8), pady=(0, 4))
    browse_btn = ttk.Button(frame, command=choose)
    browse_btn.grid(row=1, column=2, sticky="e")
    languages.bind("<<ComboboxSelected>>", translate)
    root.protocol("WM_DELETE_WINDOW", close)
    translate()
    update_actions()
    poll()
    root.mainloop()
    return 0


def main():
    parser = argparse.ArgumentParser(description="666SOUNDsDESIGn Windows ToolStarter")
    parser.add_argument("mode", choices=["gui", "check", "repair", "run", "diagnose", "package"], nargs="?", default="gui")
    parser.add_argument("action", nargs="?", help="Project action ID or package mode (portable, setup, both)")
    parser.add_argument("--version", action="version", version=introduction("en"))
    parser.add_argument("--profile", type=Path, default=BASE / "tools.json")
    parser.add_argument("--lang", choices=["en", "de"], default="en")
    args = parser.parse_args()
    if args.mode == "package" and args.action not in ("portable", "setup", "both"):
        parser.error("package requires portable, setup or both.")
    if args.mode != "package" and (args.mode == "run") != bool(args.action):
        parser.error("An action ID is required for run and only allowed with run.")
    if args.mode != "gui":
        return run_profile(args.profile.resolve(), args.lang, args.mode, args.action)
    try:
        return gui(args.profile.resolve(), args.lang)
    except ImportError as exc:
        print(f"GUI unavailable ({exc}). Use check, repair or run.", file=sys.stderr)
        return 1
    except Exception as exc:
        if type(exc).__name__ != "TclError":
            raise
        print(f"GUI unavailable ({exc}). Use check, repair or run.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
