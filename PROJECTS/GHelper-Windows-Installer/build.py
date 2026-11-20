"""Kompiliert ein G-Helper-Quellarchiv und erstellt ein Windows-x64-Offline-Setup."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import zipfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
PACKAGES = ("runtime", "asus", "pawnio")
CONFIG = ROOT / "build-config.json"
INPUTS = ROOT / "eingaben"
STAGED_INSTALLERS = {
    "runtime": "RuntimeSetup.exe",
    "asus": "AsusSetup.exe",
    "pawnio": "PawnIO_setup.exe",
}
NO_UPDATE = 0x8A15002B


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def download_input(package: dict, destination: Path, expected: str) -> None:
    url = package.get("download_url")
    if not url:
        raise RuntimeError(f"Bitte {destination.name} in eingaben ablegen. Bezugsquellen stehen in eingaben/README.md.")
    if urlsplit(url).scheme != "https":
        raise RuntimeError(f"Der Download für {destination.name} benötigt HTTPS.")
    print(f"Lade geprüfte Bezugsquelle: {destination.name}", flush=True)
    destination.parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="download-", dir=destination.parent) as temporary:
        staged_file = Path(temporary) / destination.name
        with urlopen(Request(url, headers={"User-Agent": "GHelper-Windows-Installer"}), timeout=90) as response:
            if urlsplit(response.geturl()).scheme != "https":
                raise RuntimeError(f"Unsichere Weiterleitung für {destination.name}.")
            with staged_file.open("wb") as target:
                shutil.copyfileobj(response, target)
        if digest(staged_file) != expected:
            raise RuntimeError(f"SHA-256 der Bezugsquelle stimmt nicht: {destination.name}")
        staged_file.replace(destination)


def verify_inputs(*, download_missing: bool = False) -> tuple[dict, str, str, int]:
    config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    for name in ("source", *PACKAGES):
        package = config[name]
        filename = package["file"]
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_ .()-]*", filename):
            raise RuntimeError(f"Ungültiger Dateiname für {name}.")
        checksum = package["sha256"].lower()
        download_checksum = package.get("download_sha256", checksum).lower() if name == "source" else checksum
        if any(not re.fullmatch(r"[0-9a-f]{64}", value) for value in (checksum, download_checksum)):
            raise RuntimeError(f"Ungültiger SHA-256-Wert für {name}.")
        local_file = INPUTS / filename
        if not local_file.is_file() and download_missing:
            download_input(package, local_file, download_checksum)
        if digest(local_file) not in (checksum, download_checksum):
            raise RuntimeError(f"SHA-256 stimmt nicht: {filename}")
        if name in PACKAGES and pe_machine(local_file) not in (0x8664, 0x14C):
            raise RuntimeError(f"Unerwartete Architektur: {filename}")
        if name in PACKAGES and not re.fullmatch(r"\d+\.\d+\.\d+(?:\.\d+)?", package["version"]):
            raise RuntimeError(f"Ungültige Paketversion für {name}.")
        print(f"SHA-256 bestätigt: {filename}", flush=True)

    with zipfile.ZipFile(INPUTS / config["source"]["file"]) as source:
        entries = source.namelist()
        candidates = [entry for entry in entries if PurePosixPath(entry).parts[-2:] == ("app", "GHelper.csproj")]
        if len(candidates) != 1:
            raise RuntimeError("Das ZIP muss genau eine app/GHelper.csproj enthalten.")
        member = candidates[0]
        project = ET.fromstring(source.read(member))
        app_version = project.findtext(".//AssemblyVersion", "").strip()
        framework = project.findtext(".//TargetFramework", "").strip()
    if not re.fullmatch(r"\d+(?:\.\d+){1,3}", app_version):
        raise RuntimeError("Keine eindeutige numerische AssemblyVersion im Projekt.")
    framework_match = re.fullmatch(r"net(\d+)\.(\d+)-windows(?:[0-9.]+)?", framework)
    runtime_version = tuple(map(int, config["runtime"]["version"].split(".")))
    if (not framework_match or len(runtime_version) != 3
            or runtime_version[:2] != tuple(map(int, framework_match.groups()))):
        raise RuntimeError(f"Desktop Runtime {config['runtime']['version']} passt nicht zu {framework}.")
    hardware_ids = config["asus"]["hardware_ids"]
    if not hardware_ids or any(not re.fullmatch(r"ACPI\\[A-Z0-9_]+", item) for item in hardware_ids):
        raise RuntimeError("ASUS-Hardware-IDs aus dem INF fehlen oder sind ungültig.")
    return config, member, app_version, int(framework_match[1])


def pe_machine(path: Path) -> int:
    with path.open("rb") as stream:
        header = stream.read(64)
        if len(header) != 64 or header[:2] != b"MZ":
            raise RuntimeError(f"Keine gültige Windows-EXE: {path}")
        stream.seek(struct.unpack_from("<I", header, 60)[0])
        signature = stream.read(6)
        if len(signature) != 6 or signature[:4] != b"PE\0\0":
            raise RuntimeError(f"Fehlender PE-Header: {path}")
        return struct.unpack_from("<H", signature, 4)[0]


def run(args: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> None:
    print(f"\n> {subprocess.list2cmdline(args)}", flush=True)
    subprocess.run(args, cwd=cwd, env=env, check=True)


def provision(winget: str, sdk_major: int) -> None:
    for package, architecture in ((f"Microsoft.DotNet.SDK.{sdk_major}", ["--architecture", "x64"]), ("NSIS.NSIS", [])):
        args = [
            winget, "install", "--exact", "--id", package, "--source", "winget",
            *architecture, "--silent", "--accept-package-agreements",
            "--accept-source-agreements", "--disable-interactivity",
        ]
        print(f"\n> {subprocess.list2cmdline(args)}", flush=True)
        result = subprocess.run(args, cwd=ROOT, check=False)
        if (result.returncode & 0xFFFFFFFF) not in (0, NO_UPDATE):
            raise RuntimeError(f"WinGet meldet für {package}: 0x{result.returncode & 0xFFFFFFFF:08X}")


def find_dotnet() -> Path:
    candidates = [Path(os.environ["ProgramFiles"]) / "dotnet" / "dotnet.exe"]
    from_path = shutil.which("dotnet.exe")
    if from_path:
        candidates.append(Path(from_path))
    for path in candidates:
        if path.is_file() and pe_machine(path) == 0x8664:
            return path
    raise RuntimeError("Das x64-.NET-SDK wurde nach der Werkzeugprüfung nicht gefunden.")


def find_makensis() -> Path:
    import winreg

    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for view in (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY):
            try:
                with winreg.OpenKey(hive, r"SOFTWARE\NSIS", 0, winreg.KEY_READ | view) as key:
                    directory = winreg.QueryValueEx(key, "")[0]
            except OSError:
                continue
            compiler = Path(directory) / "makensis.exe"
            if compiler.is_file():
                return compiler

    for location in ("ProgramFiles(x86)", "ProgramFiles"):
        directory = os.environ.get(location)
        if directory:
            compiler = Path(directory) / "NSIS" / "makensis.exe"
            if compiler.is_file():
                return compiler
    from_path = shutil.which("makensis.exe")
    if from_path:
        return Path(from_path)
    raise RuntimeError("NSIS (makensis.exe) wurde nach der Werkzeugprüfung nicht gefunden.")


def build_payload_manifest(payload: Path, manifest: Path) -> None:
    # Die Deinstallation löscht nur die Dateien und Unterordner aus diesem Build.
    files = sorted(path.relative_to(payload) for path in payload.rglob("*") if path.is_file())
    directories = sorted({path.parent for path in files})
    copy_lines = []
    for directory in directories:
        target = "" if directory == Path(".") else "\\" + "\\".join(directory.parts)
        copy_lines.append(f'  SetOutPath "$INSTDIR{target}"')
        for path in files:
            if path.parent == directory:
                # MakeNSIS zerlegt File-Pfade anhand des Separators seines Buildhosts.
                source = os.path.join("payload", *path.parts)
                copy_lines.append(f'  File "{source}"')
    delete_lines = [
        '  Delete /REBOOTOK "$INSTDIR\\' + "\\".join(path.parts) + '"' for path in files
    ]
    delete_lines.extend(
        '  RMDir /REBOOTOK "$INSTDIR\\' + "\\".join(directory.parts) + '"'
        for directory in sorted(directories, key=lambda path: (-len(path.parts), path))
        if directory != Path(".")
    )
    lines = [
        "!macro CopyGHelperPayload", *copy_lines, "!macroend",
        "!macro RemoveGHelperPayload", *delete_lines, "!macroend", "",
    ]
    manifest.write_text("\n".join(lines), encoding="utf-8-sig")


def select_sdk(dotnet: Path, project: Path, env: dict[str, str], sdk_major: int) -> str:
    sdks = subprocess.check_output(
        [str(dotnet), "--list-sdks"], cwd=project, env=env, text=True,
    )
    candidates = re.findall(rf"^({sdk_major}\.\d+\.\d+)\s+\[", sdks, re.MULTILINE)
    if not candidates:
        raise RuntimeError(f"Keine stabile .NET SDK-Version {sdk_major}.x gefunden.")
    version = max(candidates, key=lambda value: tuple(map(int, value.split("."))))
    # Die Originaldatei im Quell-ZIP bleibt unverändert. Nur der temporäre Build verwendet diese Auswahl.
    (project / "global.json").write_text(
        json.dumps({"sdk": {"version": version, "rollForward": "disable"}}) + "\n",
        encoding="utf-8",
    )
    return version


def compile_setup(dotnet: Path, makensis: Path, work: Path, inputs: tuple[dict, str, str, int]) -> Path:
    config, project_member, app_version, sdk_major = inputs
    source_stage = work / "source"
    with zipfile.ZipFile(INPUTS / config["source"]["file"]) as source:
        for member in source.namelist():
            path = PurePosixPath(member)
            if path.is_absolute() or ".." in path.parts or "\\" in member or ":" in member:
                raise RuntimeError(f"Unsicherer ZIP-Pfad: {member}")
        source.extractall(source_stage)

    project = (source_stage / project_member).parent
    source_root = project.parent
    env = os.environ | {
        # Nutzt die vorhandenen CI-Guards des Projekts und schließt keine laufende G-Helper-Instanz.
        "GITHUB_ACTIONS": "true",
        "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
        "DOTNET_GENERATE_ASPNET_CERTIFICATE": "false",
    }
    print(f".NET SDK für diesen Build: {select_sdk(dotnet, project, env, sdk_major)}", flush=True)

    payload = work / "payload"
    run([
        str(dotnet), "publish", "GHelper.csproj", "-c", "Release", "-r", "win-x64",
        "--self-contained", "false", "-p:PublishSingleFile=true",
        "-p:EnableWindowsTargeting=true", "-o", str(payload),
    ], cwd=project, env=env)
    if pe_machine(payload / "GHelper.exe") != 0x8664:
        raise RuntimeError("GHelper.exe ist keine Windows-x64-Anwendung.")
    if (payload / "hostfxr.dll").exists():
        raise RuntimeError("Unerwartete private Runtime im G-Helper-Payload.")

    for symbols in payload.rglob("*.pdb"):
        symbols.unlink()
    shutil.copyfile(source_root / "LICENSE", payload / "LICENSE-GHelper.txt")
    keybindings = ROOT / "TASTENKUERZEL.md"
    if app_version == "0.294":
        shutil.copyfile(keybindings, payload / keybindings.name)
    shutil.copyfile(project / "favicon.ico", work / "GHelper.ico")
    for name, staged_file in STAGED_INSTALLERS.items():
        installer = work / staged_file
        package = config[name]
        shutil.copyfile(INPUTS / package["file"], installer)
        if digest(installer) != package["sha256"].lower():
            raise RuntimeError(f"SHA-256 stimmt beim Kopieren nicht: {staged_file}")
    (work / "prerequisites.json").write_text(
        json.dumps({name: config[name] for name in PACKAGES}), encoding="ascii",
    )
    for name in ("GHelper.nsi", "install-prerequisites.ps1"):
        shutil.copyfile(ROOT / name, work / name)
    file_version = ".".join((app_version.split(".") + ["0"] * 4)[:4])
    (work / "version.nsh").write_text(
        f'!define APP_VER "{app_version}"\n!define FILE_VER "{file_version}"\n', encoding="ascii",
    )
    build_payload_manifest(payload, work / "payload.nsh")
    (work / "output").mkdir()
    prefix = "/" if sys.platform == "win32" else "-"
    version = subprocess.check_output(
        [str(makensis), prefix + "VERSION"], cwd=work, text=True,
    ).strip()
    match = re.search(r"(\d+)\.(\d+)", version)
    if not match or tuple(map(int, match.groups())) < (3, 13):
        raise RuntimeError(f"NSIS 3.13 oder neuer benötigt. Gefunden: {version}")
    print(f"NSIS für diesen Build: {version}", flush=True)
    run([str(makensis), prefix + "WX", "GHelper.nsi"], cwd=work)
    setup = work / "output" / f"GHelper-{app_version}-Offline-Setup-x64.exe"
    if pe_machine(setup) not in (0x8664, 0x14C):
        raise RuntimeError("Setup-EXE hat ein unerwartetes PE-Format.")
    return setup


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--winget", default=shutil.which("winget.exe"))
    parser.add_argument(
        "--ohne-werkzeugupdate", action="store_true",
        help="Bereits installierte Werkzeugversionen verwenden.",
    )
    parser.add_argument(
        "--eingaben-pruefen", action="store_true",
        help="Eingaben, Prüfsummen und Projektversion lesen.",
    )
    parser.add_argument(
        "--eingaben-laden", action="store_true",
        help="Fehlende Eingabedateien von den hinterlegten Bezugsquellen laden und prüfen.",
    )
    args = parser.parse_args()

    try:
        if args.eingaben_pruefen:
            verify_inputs()
            return 0
        inputs = verify_inputs(download_missing=True)
        if args.eingaben_laden:
            return 0
        if sys.platform != "win32" or struct.calcsize("P") != 8:
            raise RuntimeError("Der Doppelklick-Build benötigt Windows x64.")
        if not args.ohne_werkzeugupdate:
            if not args.winget:
                raise RuntimeError("WinGet fehlt. Bitte GHELPER_BUILD.bat ausführen.")
            provision(args.winget, inputs[3])
        dotnet, makensis = find_dotnet(), find_makensis()
        with tempfile.TemporaryDirectory(prefix="ghelper-build-") as folder:
            setup = compile_setup(dotnet, makensis, Path(folder), inputs)
            checksum = digest(setup)
            output = ROOT / "output"
            output.mkdir(exist_ok=True)
            with tempfile.TemporaryDirectory(prefix="staging-", dir=output) as staging:
                staged_setup = Path(staging) / setup.name
                staged_hash = staged_setup.with_suffix(".exe.sha256")
                shutil.copyfile(setup, staged_setup)
                staged_hash.write_text(f"{checksum}  {setup.name}\n", encoding="ascii")
                staged_setup.replace(output / staged_setup.name)
                staged_hash.replace(output / staged_hash.name)
        print(f"\nSetup erstellt: {output / setup.name}", flush=True)
        print(f"SHA-256: {checksum}", flush=True)
        return 0
    except (OSError, RuntimeError, subprocess.CalledProcessError, zipfile.BadZipFile, ET.ParseError, KeyError, ValueError) as error:
        print(f"\nBuild fehlgeschlagen: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
