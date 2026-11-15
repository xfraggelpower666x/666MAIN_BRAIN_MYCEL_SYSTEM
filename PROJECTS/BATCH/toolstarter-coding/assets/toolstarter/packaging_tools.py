"""Gemeinsame, verifizierbare Nutzlast für Portable und Setup."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile
import zipfile


def relative(value):
    parts = value.split("/")
    if any(part in ("", ".", "..") or not re.fullmatch(r"[A-Za-z0-9 _.()+-]+", part)
           or part.endswith((" ", ".")) for part in parts):
        raise ValueError(f"Invalid package path: {value!r}")
    return Path(*PurePosixPath(value).parts)


def checksum(handle):
    digest = hashlib.sha256()
    for data in iter(lambda: handle.read(1024 * 1024), b""):
        digest.update(data)
    return digest.hexdigest()


def stage_file(source, stage, destination, seen):
    name = destination.as_posix().casefold()
    if name in seen or (stage / destination).exists():
        raise ValueError(f"Duplicate package path: {destination}")
    if source.is_symlink() or not source.is_file():
        raise ValueError(f"Expected regular source file: {source}")
    seen.add(name)
    (stage / destination).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, stage / destination)


def package(starter, mode):
    config = starter.config["package"]
    metadata = config["metadata"]
    app_id = metadata["app_id"]
    stem = metadata["output_name"]
    version = metadata["version"]
    for value in (app_id, stem, version):
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,90}", value):
            raise ValueError(f"Invalid packaging identifier: {value!r}")
    for key in ("name", "publisher"):
        if not re.fullmatch(r"[\w .()+-]{1,100}", metadata[key]):
            raise ValueError(f"Invalid packaging {key}: {metadata[key]!r}")
    electron_version = None
    if config.get("electron_package"):
        electron_version = starter.require_electron_version(config["electron_package"])
    output = starter.root / relative(config.get("output_dir", "dist/toolstarter"))
    output.mkdir(parents=True, exist_ok=True)
    # Der temporäre Ordner liegt auf demselben Laufwerk wie die Ausgabe.
    with tempfile.TemporaryDirectory(prefix=".package-", dir=output) as temp:
        work = Path(temp)
        stage = work / "payload"
        stage.mkdir()
        seen = set()
        for item in config["include"]:
            requested_source = starter.root / item["from"]
            if requested_source.is_symlink():
                raise ValueError(f"Symlink in package input: {requested_source}")
            source = requested_source.resolve()
            if stage.is_relative_to(source):
                raise ValueError(f"Package output is inside the input directory: {source}")
            destination = relative(item["to"]) if item["to"] != "." else Path(".")
            if destination == Path(".") and not source.is_dir():
                raise ValueError("Only a source directory can be copied to the bundle root.")
            if source.is_dir():
                for entry in sorted(source.rglob("*")):
                    if entry.is_symlink():
                        raise ValueError(f"Symlink in package input: {entry}")
                    if entry.is_file():
                        converted = relative((destination / entry.relative_to(source)).as_posix())
                        stage_file(entry, stage, converted, seen)
            else:
                stage_file(source, stage, destination, seen)
        entry = relative(config["entry"])
        if entry.suffix.lower() != ".exe" or not (stage / entry).is_file():
            raise ValueError(f"Packaged entry executable is missing: {entry}")
        path_dirs = [relative(value) for value in config.get("path_dirs", [])]
        for directory in path_dirs:
            if not (stage / directory).is_dir():
                raise ValueError(f"Packaged PATH directory is missing: {directory}")

        runtime = config["runtime"]
        expected = set(config.get("required_runtime_ids", []))
        covered = {item["id"] for item in runtime}
        if not expected or covered != expected or len(covered) != len(runtime):
            raise ValueError("Declare every required runtime ID exactly once and provide its files and probes.")
        if electron_version:
            electron = next((item for item in runtime if item["id"] == "electron"), None)
            if not electron or not any("{electron_version}" in p.get("match", "") for p in electron["probes"]):
                raise ValueError("Electron requires a bundled smoke probe containing {electron_version}.")
        for item in runtime:
            if not item["files"] or not item["licenses"] or not item["probes"]:
                raise ValueError(f"{item['id']}: files, licenses and probes are required.")
            for file in item["files"] + item["licenses"]:
                path = stage / relative(file)
                if not path.is_file() or path.stat().st_size == 0:
                    raise ValueError(f"{item['id']}: missing or empty bundled file: {file}")

        environment = {}
        for name, value in config.get("runtime_environment", {}).items():
            target = relative(value)
            if not re.fullmatch(r"[A-Z][A-Z0-9_]*", name) or not (stage / target).is_file():
                raise ValueError(f"Invalid bundled environment mapping: {name}={value}")
            environment[name] = target

        previous_root, previous_env = starter.root, starter.env
        starter.root, starter.env = stage, starter.env.copy()
        # Explizite Probe-Pfade und nur gebündelte Ordner im PATH.
        starter.env["PATH"] = os.pathsep.join(str(stage / p) for p in path_dirs)
        starter.env.update({name: str(stage / path) for name, path in environment.items()})
        try:
            for item in runtime:
                for probe in item["probes"]:
                    binary = stage / relative(probe["exe"])
                    if not binary.is_file() or binary.suffix.lower() != ".exe":
                        raise ValueError(f"{item['id']}: missing bundled probe executable: {binary}")
                    match = probe.get("match")
                    if match and electron_version:
                        match = match.replace("{electron_version}", re.escape(electron_version))
                    success, detail = starter.probe([str(binary), *probe.get("args", [])], match)
                    if not success:
                        raise ValueError(f"{item['id']}: {binary.name} | {detail}")
                    starter.log(f"[{starter.label('ok')}] {item['id']} | {binary.name} | {detail}")
            if "ffmpeg" in expected:
                pair = [str(stage / environment[name]) for name in ("FFMPEG_PATH", "FFPROBE_PATH")]
                success, detail = starter.audio_sample(*pair)
                if not success:
                    raise ValueError(f"Bundled FFmpeg function test: {detail}")
                starter.log(f"[{starter.label('ok')}] FFmpeg → WAV → FFprobe | {detail}")
        finally:
            starter.root, starter.env = previous_root, previous_env

        reserved = ("STARTEN.bat", "bundle-manifest.json", "BUNDLE_DIAGNOSE.ps1")
        if any(name.casefold() in seen for name in reserved):
            raise ValueError("STARTEN.bat, bundle-manifest.json and BUNDLE_DIAGNOSE.ps1 are reserved.")
        (stage / "BUNDLE_DIAGNOSE.ps1").write_text(BUNDLE_DIAGNOSTICS, encoding="ascii")
        lines = ["@echo off", "setlocal EnableExtensions DisableDelayedExpansion",
                 'pushd "%~dp0" || exit /b 1',
                 'if /i "%~1"=="--diagnose" goto diagnose']
        if path_dirs:
            prefixes = ";".join("%~dp0" + str(directory) for directory in path_dirs)
            lines.append(f'set "PATH={prefixes};%PATH%"')
        for name, target in environment.items():
            lines.append(f'set "{name}=%~dp0{target}"')
        # Alle Projekte erhalten denselben Aufrufvertrag: Startargumente plus an den Starter übergebene Argumente.
        args = config.get("entry_args", [])
        if any(not re.fullmatch(r"[A-Za-z0-9 _./:=+-]+", arg) for arg in args):
            raise ValueError("Package entry_args must contain plain Windows arguments.")
        arguments = " ".join(f'"{arg}"' for arg in args)
        lines.extend([f'"%~dp0{entry}" {arguments} %*', 'set "RC=%errorlevel%"',
                      "goto finish", ":diagnose",
                      r'"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -NonInteractive -File "%~dp0BUNDLE_DIAGNOSE.ps1"',
                      'set "RC=%errorlevel%"', ":finish", "popd", "exit /b %RC%"])
        (stage / "STARTEN.bat").write_bytes(("\r\n".join(lines) + "\r\n").encode("ascii"))
        manifest = {"product": metadata, "runtime": sorted(expected), "files": {}}
        for file in sorted(stage.rglob("*")):
            if file.is_file():
                with file.open("rb") as handle:
                    manifest["files"][file.relative_to(stage).as_posix()] = checksum(handle)
        manifest_path = stage / "bundle-manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        portable = work / f"{stem}-Portable.zip"
        setup = work / f"{stem}-Setup.exe"
        if mode in ("portable", "both"):
            with zipfile.ZipFile(portable, "w", zipfile.ZIP_DEFLATED, compresslevel=5) as archive:
                for name in [*manifest["files"], manifest_path.name]:
                    archive.write(stage / name, name)
            with zipfile.ZipFile(portable) as archive:
                if json.loads(archive.read(manifest_path.name)) != manifest:
                    raise ValueError("ZIP manifest readback failed.")
                for name, digest in manifest["files"].items():
                    with archive.open(name) as handle:
                        if checksum(handle) != digest:
                            raise ValueError(f"ZIP readback mismatch: {name}")
        if mode in ("setup", "both"):
            # Die Setup-Engine erhält exakt denselben vollständigen Nutzlastordner.
            script = work / "installer.iss"
            script.write_text(inno_script(metadata), encoding="utf-8-sig")
            compiler = config.get("iscc")
            if not compiler:
                locations = [Path(os.environ[name]) / f"Inno Setup {major}/ISCC.exe"
                             for name in ("ProgramFiles(x86)", "ProgramFiles")
                             if os.environ.get(name) for major in (7, 6)]
                compiler = next((str(path) for path in locations if path.is_file()), "ISCC.exe")
            code, _ = starter.execute([compiler, f"-O{work}", f"-F{setup.stem}", str(script)])
            if code:
                return code
            if not setup.is_file() or setup.stat().st_size == 0:
                raise ValueError("ISCC did not produce Setup.exe.")
            with setup.open("rb") as handle:
                if handle.read(2) != b"MZ":
                    raise ValueError("Setup.exe is not a Windows executable.")

        for artifact in (portable, setup):
            if artifact.is_file():
                target = output / artifact.name
                artifact.replace(target)
                starter.log(f"[{starter.label('ok')}] {target}")
        manifest_path.replace(output / f"{stem}-bundle-manifest.json")
    return 0



BUNDLE_DIAGNOSTICS = r"""
$ErrorActionPreference = 'Stop'
$logDir = Join-Path $env:LOCALAPPDATA '666SOUNDsDESIGn\ToolStarter\logs'
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss-ffff'
$log = Join-Path $logDir ("bundle-diagnose-$stamp-$PID.log")
function Write-Result($message) {
    Write-Output $message
    Add-Content -LiteralPath $log -Value $message -Encoding UTF8
}
Write-Result '666 TOOLSTARTER v1.0.1 | Bundle diagnosis | (c) 2026 666SOUNDsDESIGn - FRAGGLEPOWER666'
Write-Result "Log: $log"
try {
    $manifest = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'bundle-manifest.json') -Raw -Encoding UTF8 |
        ConvertFrom-Json
    $failed = 0
    foreach ($file in $manifest.files.PSObject.Properties) {
        if ($file.Name -notmatch '^[A-Za-z0-9 ._()+/-]+$' -or $file.Name.StartsWith('/') -or
            ($file.Name.Split('/') -contains '..')) { throw "Invalid manifest path: $($file.Name)" }
        $path = Join-Path $PSScriptRoot $file.Name
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            Write-Result "MISSING $($file.Name)"
            $failed++
            continue
        }
        if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -ne $file.Value) {
            Write-Result "MISMATCH $($file.Name)"
            $failed++
        }
    }
    Write-Result "$($manifest.product.name) $($manifest.product.version) | Differences: $failed"
    if ($failed -gt 0) { exit 1 }
    exit 0
}
catch {
    Write-Result "ERROR: $_"
    exit 1
}
"""

def inno_script(metadata):
    portable_source = r"payload\*"
    return rf'''[Setup]
AppId={metadata['app_id']}
AppName={metadata['name']}
AppVersion={metadata['version']}
AppPublisher={metadata['publisher']}
DefaultDirName={{localappdata}}\Programs\{metadata['output_name']}
DefaultGroupName={metadata['name']}
PrivilegesRequired=lowest
Compression=lzma2
SolidCompression=yes
[Files]
Source: "{portable_source}"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{{group}}\{metadata['name']}"; Filename: "{{app}}\STARTEN.bat"; WorkingDir: "{{app}}"
'''
