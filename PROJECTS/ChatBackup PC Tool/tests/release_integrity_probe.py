from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath

ROOT = Path(__file__).resolve().parents[1]
PC_VERSION = "1.10.5"
MOBILE_VERSION = "1.0.9"
MOBILE_NAME = f"666_CHATBACKUP_SCRIPTABLE_IPHONE_v{MOBILE_VERSION}.zip"

checks: list[dict[str, str]] = []

def add(name: str, ok: bool, detail: object = "") -> None:
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "detail": str(detail)})

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def verify_pc_manifest(root: Path) -> tuple[int, dict[str, list[str]]]:
    entries: set[str] = set()
    problems: dict[str, list[str]] = {"invalid": [], "missing": [], "mismatch": []}
    for index, line in enumerate((root / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        match = re.fullmatch(r"([0-9a-fA-F]{64})\s+\*?(.+)", line)
        if not match:
            problems["invalid"].append(f"Zeile {index}")
            continue
        digest, relative = match.groups()
        rel = PurePosixPath(relative.replace(chr(92), "/").removeprefix("./"))
        name = rel.as_posix()
        key = name.casefold()
        if (rel.is_absolute() or PureWindowsPath(name).drive or ".." in rel.parts
                or key in entries or key in {".", "manifest.sha256"}):
            problems["invalid"].append(relative)
            continue
        entries.add(key)
        path = (root / rel).resolve()
        if not path.is_relative_to(root):
            problems["invalid"].append(relative)
        elif not path.is_file():
            problems["missing"].append(name)
        elif sha256(path) != digest.lower():
            problems["mismatch"].append(name)
    return len(entries), problems


try:
    count, issues = verify_pc_manifest(ROOT)
    failed_files = sum(len(items) for items in issues.values())
    add("PC_MANIFEST", count > 0 and not failed_files,
        json.dumps({"entries": count, **issues}, ensure_ascii=False))
except (OSError, ValueError, RuntimeError) as exc:
    add("PC_MANIFEST", False, repr(exc))


mobile = ROOT / "mobile_scriptable" / MOBILE_NAME
hash_file = mobile.with_suffix(mobile.suffix + ".sha256")
try:
    add("CURRENT_MOBILE_ZIP_PRESENT", mobile.is_file(), mobile)
    add("CURRENT_MOBILE_SHA_PRESENT", hash_file.is_file(), hash_file)
    if mobile.is_file() and hash_file.is_file():
        expected = hash_file.read_text(encoding="utf-8").strip().split()[0].lower()
        actual = sha256(mobile)
        add("CURRENT_MOBILE_SHA_MATCH", expected == actual, actual)
        with zipfile.ZipFile(mobile) as zf:
            names = zf.namelist()
            version_name = next(n for n in names if n.endswith("/VERSION.json"))
            manifest_name = next(n for n in names if n.endswith("/MANIFEST.sha256"))
            version = json.loads(zf.read(version_name).decode("utf-8"))
            add("CURRENT_MOBILE_VERSION", version.get("version") == MOBILE_VERSION, version.get("version"))
            base = manifest_name.rsplit("/", 1)[0] + "/"
            manifest = zf.read(manifest_name).decode("utf-8")
            manifest_ok = True
            count = 0
            for line in manifest.splitlines():
                line = line.strip()
                if not line:
                    continue
                m = re.match(r"^([0-9a-fA-F]{64})\s+\*?(.+)$", line)
                if not m:
                    manifest_ok = False
                    break
                digest, rel = m.groups()
                rel = rel.replace("\\", "/").removeprefix("./")
                try:
                    data = zf.read(base + rel)
                except KeyError:
                    manifest_ok = False
                    break
                if hashlib.sha256(data).hexdigest() != digest.lower():
                    manifest_ok = False
                    break
                count += 1
            add("CURRENT_MOBILE_MANIFEST", manifest_ok and count >= 5, f"entries={count}")
except Exception as exc:
    add("CURRENT_MOBILE_PACKAGE_READ", False, repr(exc))

try:
    with zipfile.ZipFile(mobile) as zf:
        js_name = next(n for n in zf.namelist() if n.endswith(f"666_CHATBACKUP_SCRIPTABLE_IPHONE_v{MOBILE_VERSION}.js"))
        mobile_source = zf.read(js_name).decode("utf-8")
        mobile_contract_ok = all(marker in mobile_source for marker in (
            "Run host acceptance",
            "666.chatbackup.host-acceptance.v1",
            "HOST_ACCEPTANCE_PASS",
            "JSON_MESSAGE_COUNT_READBACK",
            "STRUCTURE_MESSAGE_COUNT_READBACK",
        ))
        add("CURRENT_MOBILE_HOST_ACCEPTANCE_CONTRACT", mobile_contract_ok, js_name)
except Exception as exc:
    add("CURRENT_MOBILE_HOST_ACCEPTANCE_CONTRACT", False, repr(exc))

try:
    windows_probe = ROOT / "tests" / "host_acceptance_probe.py"
    windows_bat = ROOT / "VERIFY_WINDOWS_HOST_ACCEPTANCE.bat"
    probe_source = windows_probe.read_text(encoding="utf-8") if windows_probe.is_file() else ""
    bat_source = windows_bat.read_text(encoding="utf-8", errors="replace") if windows_bat.is_file() else ""
    bootstrap_source = (ROOT / "bootstrap" / "bootstrap.ps1").read_text(encoding="utf-8-sig")
    ok = (
        windows_probe.is_file()
        and windows_bat.is_file()
        and "666.chatbackup.windows-host-acceptance.v1" in probe_source
        and "WINDOWS_HOST_ACCEPTANCE_PASS" in probe_source
        and "-Mode VerifyHost" in bat_source
        and "host_acceptance_probe.py" in bootstrap_source
        and "--share-url=" in bootstrap_source
    )
    add("WINDOWS_HOST_ACCEPTANCE_CONTRACT", ok, windows_bat)
except Exception as exc:
    add("WINDOWS_HOST_ACCEPTANCE_CONTRACT", False, repr(exc))

try:
    current = (ROOT / "CURRENT_RELEASE_INDEX.md").read_text(encoding="utf-8")
    mapping = (ROOT / "SOURCE_MAPPING.md").read_text(encoding="utf-8")
    add("CURRENT_INDEX_PC_VERSION", f"PC runtime: `{PC_VERSION}`" in current, PC_VERSION)
    add("CURRENT_INDEX_MOBILE_VERSION", f"Scriptable companion: `{MOBILE_VERSION}`" in current, MOBILE_VERSION)
    add("SOURCE_MAPPING_CURRENT_MOBILE", f"mobile_scriptable/{MOBILE_NAME}" in mapping, MOBILE_NAME)
    stale = "mobile_scriptable/666_CHATBACKUP_SCRIPTABLE_IPHONE_v1.0.0.zip` — audited mobile distribution snapshot"
    add("SOURCE_MAPPING_NO_STALE_V1_0_0_CURRENT", stale not in mapping, "stale-current-reference")
except Exception as exc:
    add("CURRENT_DOCUMENT_READ", False, repr(exc))

history = ROOT / "mobile_scriptable" / "history"
add("HISTORY_V1_0_0_PRESENT", (history / "666_CHATBACKUP_SCRIPTABLE_IPHONE_v1.0.0.zip").is_file(), history)
add("HISTORY_V1_0_6_PRESENT", (history / "666_CHATBACKUP_SCRIPTABLE_IPHONE_v1.0.6.zip").is_file(), history)
add("HISTORY_V1_0_7_PRESENT", (history / "666_CHATBACKUP_SCRIPTABLE_IPHONE_v1.0.7.zip").is_file(), history)
add("HISTORY_V1_0_8_PRESENT", (history / "666_CHATBACKUP_SCRIPTABLE_IPHONE_v1.0.8.zip").is_file(), history)

failed = [c for c in checks if c["status"] != "PASS"]
report = {
    "status": "RELEASE_INTEGRITY_PASS" if not failed else "RELEASE_INTEGRITY_FAIL",
    "tool": "666 ChatBackup PC Tool",
    "pcVersion": PC_VERSION,
    "mobileVersion": MOBILE_VERSION,
    "executedAtUtc": datetime.now(timezone.utc).isoformat(),
    "checks": checks,
}
out_dir = ROOT / "runtime_readback"
out_dir.mkdir(exist_ok=True)
out = out_dir / "release_integrity_readback.json"
out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
print(f"REPORT={out}")
raise SystemExit(0 if not failed else 2)
