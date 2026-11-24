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


def file_record(path):
    with path.open("rb") as handle:
        digest = checksum(handle)
        size = handle.tell()
    return {"sha256": digest, "size_bytes": size}


def payload_fingerprint(manifest):
    payload = json.dumps(manifest, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def verify_publication(receipt_path):
    receipt_path = Path(receipt_path)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if not isinstance(receipt, dict) or receipt.get("publication_schema") != 1:
        raise ValueError("Expected a current publication manifest.")
    payload = {name: receipt[name] for name in ("product", "runtime", "files") if name in receipt}
    if len(payload) != 3 or payload_fingerprint(payload) != receipt.get("payload_sha256"):
        raise ValueError("Publication payload fingerprint mismatch.")
    records = receipt.get("artifacts")
    stem = receipt_path.name.removesuffix("-bundle-manifest.json")
    names = {"portable": f"{stem}-Portable.zip", "setup": f"{stem}-Setup.exe"}
    if not isinstance(records, dict) or not records or records.keys() - names.keys():
        raise ValueError("Invalid publication artifact list.")
    for mode, record in records.items():
        path = receipt_path.with_name(names[mode])
        if record != {"file": path.name, **file_record(path)}:
            raise ValueError(f"Publication readback mismatch: {path.name}")
    return receipt


def publish(starter, work, output, stem, manifest, portable, setup):
    payload_sha256 = payload_fingerprint(manifest)
    receipt_name = f"{stem}-bundle-manifest.json"
    receipt_path = output / receipt_name
    lock = output / f".{stem.casefold()}-publish.lock"
    try:
        lock.mkdir()
    except FileExistsError as error:
        raise ValueError(f"Publication locked for {stem}. Check the active build or recover the lock.") from error

    try:
        artifacts = {"portable": portable, "setup": setup}
        records = {}
        for mode, path in artifacts.items():
            if path.is_file():
                records[mode] = {"file": path.name, **file_record(path)}
                continue
            sibling = output / path.name
            if not sibling.exists() and not sibling.is_symlink():
                continue
            try:
                previous = json.loads(receipt_path.read_text(encoding="utf-8"))
                expected = {"file": path.name, **file_record(sibling)}
                same_payload = (previous["publication_schema"] == 1
                                and previous["payload_sha256"] == payload_sha256
                                and previous["artifacts"][mode] == expected)
            except (OSError, ValueError, KeyError, TypeError):
                same_payload = False
            if not same_payload:
                raise ValueError(
                    f"Existing {path.name} cannot be paired with this payload. "
                    "Use package both or a different output_name."
                )
            records[mode] = expected

        receipt = {**manifest, "publication_schema": 1, "payload_sha256": payload_sha256,
                   "artifacts": records}
        staged_receipt = work / receipt_name
        staged_receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for mode, path in artifacts.items():
            if path.is_file():
                path.replace(output / records[mode]["file"])
        for record in records.values():
            published = output / record["file"]
            if record != {"file": published.name, **file_record(published)}:
                raise ValueError(f"Publication readback mismatch: {published.name}")
        # Das externe Manifest ist der letzte Commit-Punkt des veröffentlichten Satzes.
        staged_receipt.replace(receipt_path)
        if verify_publication(receipt_path) != receipt:
            raise ValueError("Publication manifest readback failed.")
        for record in records.values():
            starter.log(f"[{starter.label('ok')}] {output / record['file']}")
    finally:
        lock.rmdir()


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
    launch_mode = config.get("launch_mode", "batch")
    if launch_mode not in ("batch", "direct"):
        raise ValueError("launch_mode must be batch or direct.")
    if launch_mode == "direct" and config.get("entry_args"):
        raise ValueError("Direct launch requires an executable that starts without entry_args.")
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
            # Restrict packaging inputs to the selected project root.
            requested_source = starter.root / relative(item["from"])
            if requested_source.is_symlink():
                raise ValueError(f"Symlink in package input: {requested_source}")
            source = requested_source.resolve()
            if not source.is_relative_to(starter.root.resolve()):
                raise ValueError(f"Package source escapes project root: {source}")
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
        if launch_mode == "direct":
            excluded_names = {"toolstarter.py", "packaging_tools.py"}
            if any(Path(name).suffix in (".bat", ".cmd") or Path(name).name in excluded_names for name in seen):
                raise ValueError("Direct launch bundles cannot contain batch launchers or ToolStarter build scripts.")
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
        if launch_mode == "batch":
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
            shortcut_entry = entry if launch_mode == "direct" else Path("STARTEN.bat")
            script.write_text(inno_script(metadata, shortcut_entry, dual_mode=config.get("dual_mode", False)), encoding="utf-8-sig")
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

        publish(starter, work, output, stem, manifest, portable, setup)
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

def inno_script(metadata, entry=Path("STARTEN.bat"), *, dual_mode=False):
    # Der Setup-Compiler erwartet auch bei der Quellprüfung Windows-Pfade.
    destination = "\\".join(entry.parts)
    parent = "\\".join(entry.parent.parts)
    working_directory = r"{app}" + ("\\" + parent if parent else "")
    portable_source = r"payload\*"
    script = rf'''[Setup]
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
Name: "{{group}}\{metadata['name']}"; Filename: "{{app}}\{destination}"; WorkingDir: "{working_directory}"
'''
    if not dual_mode:
        return script

    script = script.replace(
        r"{localappdata}\Programs", r"{autopf}"
    ).replace(
        "PrivilegesRequired=lowest\n",
        "PrivilegesRequired=admin\nDisableProgramGroupPage=yes\n"
        "DisableDirPage=no\nUsePreviousAppDir=no\n"
        "Uninstallable=not IsPortable\nCreateUninstallRegKey=not IsPortable\n",
    ).replace(
        'Name: "{group}', 'Name: "{autoprograms}'
    ).replace(
        'WorkingDir: "' + working_directory + '"',
        'WorkingDir: "' + working_directory + '"; Check: IsFullInstall',
    )
    return script + rf"""
[Code]
var
  InstallMode: TInputOptionWizardPage;

procedure InitializeWizard;
begin
  InstallMode := CreateInputOptionPage(wpWelcome,
    'Choose deployment mode', 'Full installation or portable',
    'Select how to deploy {metadata['name']}.', True, False);
  InstallMode.Add('Full installation');
  InstallMode.Add('Extract portable application');
  InstallMode.SelectedValueIndex := 0;
end;

function IsPortable: Boolean;
begin
  Result := False;
  if Assigned(InstallMode) then
    Result := InstallMode.SelectedValueIndex = 1;
end;

function IsFullInstall: Boolean;
begin
  Result := not IsPortable;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = InstallMode.ID then begin
    if IsPortable then
      WizardForm.DirEdit.Text := ExpandConstant('{{userdocs}}\{metadata['output_name']}-Portable')
    else
      WizardForm.DirEdit.Text := ExpandConstant('{{autopf}}\{metadata['output_name']}');
  end;
end;
"""
