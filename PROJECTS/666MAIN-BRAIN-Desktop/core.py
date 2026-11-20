"""Befunde aus bestehenden MAIN-BRAIN-Werkzeugen lesen."""
from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

APP_DIR = Path(__file__).resolve().parent
REPO_DIR = APP_DIR.parents[1]
TOOLS_DIR = REPO_DIR / "INTEGRATIONS" / "PSYLLO_CODING"
POINTER = "CURRENT_POINTER.md"
BRANCH = "666MAIN_BRAIN"
SHA = re.compile(r"[0-9a-f]{40,64}")


def run(arguments: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env["GIT_OPTIONAL_LOCKS"] = "0"
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["PYTHONIOENCODING"] = "utf-8"
    options = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
    return subprocess.run(
        arguments, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=timeout, env=env, cwd=APP_DIR, **options,
    )


def git(checkout: Path, *args: str) -> str:
    executable = shutil.which("git")
    if executable is None:
        raise RuntimeError("Git fehlt im PATH.")
    result = run([executable, "-C", str(checkout), *args])
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"Git meldet Exitcode {result.returncode}.")
    return result.stdout.strip()


def current(checkout: Path, compare_remote: bool = False) -> dict[str, str]:
    root = Path(git(checkout, "rev-parse", "--show-toplevel"))
    revision = git(root, "rev-parse", "HEAD")
    branch = git(root, "rev-parse", "--abbrev-ref", "HEAD")
    pointer = git(root, "show", f"{revision}:{POINTER}")
    rows = dict(line.split("=", 1) for line in pointer.splitlines()
                if re.match(r"^[A-Z][A-Z0-9_]+=", line))
    if rows.get("SYSTEM_ID") != "666MAIN-BRAIN-MYCEL-SYSTEM-001":
        raise ValueError("Der Pointer gehört nicht zu 666MAIN BRAIN.")
    result = {
        "Projekt": str(root),
        "Lokaler Branch": branch,
        "Lokaler HEAD": revision,
        "Pointer aus Git": git(root, "rev-parse", f"{revision}:{POINTER}"),
        "Arbeitsbaum": git(root, "status", "--porcelain=v1") or "Sauber",
        "Systemstatus": rows.get("STATUS", "OFFEN"),
        "Plugin laut Pointer": rows.get("PSYLLO_CODING_PLUGIN_RELEASE", "OFFEN"),
        "Fresh-Chat-Abnahme": rows.get("PSYLLO_CODING_FRESH_CHAT", "OFFEN"),
        "GitHub-Current": "OFFEN · Remote-Abgleich noch nicht ausgeführt",
    }
    if compare_remote:
        url = "https://github.com/xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM.git"
        ref = f"refs/heads/{BRANCH}"
        output = git(root, "ls-remote", "--exit-code", "--refs", url, ref)
        remote, separator, observed = output.partition("\t")
        if not separator or observed != ref or SHA.fullmatch(remote) is None:
            raise RuntimeError("GitHub lieferte keinen eindeutigen Branch-HEAD.")
        result["GitHub-Current"] = ("VERIFIZIERT" if remote == revision and branch == BRANCH else
                                    "ABWEICHUNG · Lokalen Stand und Branch prüfen")
        result["GitHub-HEAD"] = remote
    return result


def tool(component: str, *args: str) -> subprocess.CompletedProcess[str]:
    entrypoints = {
        "checkpoint": "checkpoint/scripts/checkpoint_review.py",
        "receipt": "run/scripts/check_run_evidence.py",
        "workbench": "workbench/scripts/render_ui.py",
    }
    entry = TOOLS_DIR / entrypoints[component]
    if not entry.is_file():
        raise FileNotFoundError(f"MAIN-BRAIN-Integration fehlt: {entry}")
    return run([sys.executable, "-B", str(entry), *args], timeout=60)


def export_workbench(source: str, destination: str, handoff: str = "") -> subprocess.CompletedProcess[str]:
    target = Path(destination).absolute()
    if target.suffix.lower() != ".html":
        raise ValueError("Bitte eine .html-Datei als Exportziel wählen.")
    if target.exists() or target.is_symlink():
        raise FileExistsError("Das HTML-Ziel existiert bereits. Bitte einen neuen Dateinamen wählen.")
    with TemporaryDirectory(dir=target.parent) as directory:
        staged = Path(directory) / target.name
        options = ("--checkpoint", handoff) if handoff else ()
        result = tool("workbench", source, str(staged), "--standalone", *options)
        if result.returncode:
            return result
        payload = staged.read_bytes()
        with target.open("xb") as output:
            try:
                output.write(payload)
                output.flush()
            except OSError:
                output.close()
                target.unlink()
                raise
    result.stdout = f"Workbench gespeichert:\n{target}"
    return result
