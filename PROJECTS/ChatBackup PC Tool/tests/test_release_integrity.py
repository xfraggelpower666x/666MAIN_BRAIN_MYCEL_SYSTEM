from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PC_VERSION = "1.10.5"
MOBILE_VERSION = "1.0.9"
MOBILE_NAME = f"666_CHATBACKUP_SCRIPTABLE_IPHONE_v{MOBILE_VERSION}.zip"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def test_current_release_index_and_source_mapping() -> None:
    idx = (ROOT / "CURRENT_RELEASE_INDEX.md").read_text(encoding="utf-8")
    src = (ROOT / "SOURCE_MAPPING.md").read_text(encoding="utf-8")
    assert f"PC runtime: `{PC_VERSION}`" in idx
    assert f"Scriptable companion: `{MOBILE_VERSION}`" in idx
    assert f"mobile_scriptable/{MOBILE_NAME}" in idx
    assert f"mobile_scriptable/{MOBILE_NAME}" in src
    assert "mobile_scriptable/666_CHATBACKUP_SCRIPTABLE_IPHONE_v1.0.0.zip` — audited mobile distribution snapshot" not in src


def test_current_mobile_zip_hash_version_and_manifest() -> None:
    mobile = ROOT / "mobile_scriptable" / MOBILE_NAME
    hash_file = mobile.with_suffix(mobile.suffix + ".sha256")
    assert mobile.is_file() and hash_file.is_file()
    expected = hash_file.read_text(encoding="utf-8").strip().split()[0].lower()
    assert expected == _sha256(mobile)

    with zipfile.ZipFile(mobile) as zf:
        names = zf.namelist()
        version_name = next(n for n in names if n.endswith("/VERSION.json"))
        manifest_name = next(n for n in names if n.endswith("/MANIFEST.sha256"))
        version = json.loads(zf.read(version_name).decode("utf-8"))
        assert version["version"] == MOBILE_VERSION

        base = manifest_name.rsplit("/", 1)[0] + "/"
        manifest = zf.read(manifest_name).decode("utf-8")
        checked = 0
        for line in manifest.splitlines():
            line = line.strip()
            if not line:
                continue
            match = re.match(r"^([0-9a-fA-F]{64})\s+\*?(.+)$", line)
            assert match, line
            digest, rel = match.groups()
            rel_norm = rel.replace("\\", "/").removeprefix("./")
            data = zf.read(base + rel_norm)
            assert hashlib.sha256(data).hexdigest() == digest.lower(), rel
            checked += 1
        assert checked >= 5


def test_historical_companions_are_history_scoped() -> None:
    history = ROOT / "mobile_scriptable" / "history"
    assert (history / "666_CHATBACKUP_SCRIPTABLE_IPHONE_v1.0.0.zip").is_file()
    assert (history / "666_CHATBACKUP_SCRIPTABLE_IPHONE_v1.0.6.zip").is_file()
    current_root_names = {p.name for p in (ROOT / "mobile_scriptable").iterdir() if p.is_file()}
    assert "666_CHATBACKUP_SCRIPTABLE_IPHONE_v1.0.0.zip" not in current_root_names
    assert "666_CHATBACKUP_SCRIPTABLE_IPHONE_v1.0.6.zip" not in current_root_names



def test_current_mobile_host_acceptance_contract_is_present() -> None:
    mobile = ROOT / "mobile_scriptable" / MOBILE_NAME
    with zipfile.ZipFile(mobile) as zf:
        js_name = next(n for n in zf.namelist() if n.endswith(f"666_CHATBACKUP_SCRIPTABLE_IPHONE_v{MOBILE_VERSION}.js"))
        source = zf.read(js_name).decode("utf-8")
    assert "Run host acceptance" in source
    assert "666.chatbackup.host-acceptance.v1" in source
    assert "HOST_ACCEPTANCE_PASS" in source
    assert "JSON_MESSAGE_COUNT_READBACK" in source
    assert "STRUCTURE_MESSAGE_COUNT_READBACK" in source


def test_windows_host_acceptance_fixture_pipeline() -> None:
    probe = ROOT / "tests" / "host_acceptance_probe.py"
    proc = subprocess.run(
        [sys.executable, str(probe), "--fixture"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    # 3 intentionally means fixture/non-Windows evidence passed but cannot close the real Windows gate.
    assert proc.returncode == 3, proc.stdout + proc.stderr
    receipts = sorted((ROOT / "runtime_readback").glob("host_acceptance_*/windows_host_acceptance_receipt.json"))
    assert receipts
    report = json.loads(receipts[-1].read_text(encoding="utf-8"))
    assert report["status"] == "FIXTURE_ACCEPTANCE_PASS_HOST_GATE_NOT_CLOSED"
    assert report["failed"] == 0
    assert report["messageCount"] == 1
    assert all(item["status"] == "PASS" for item in report["checks"])



def test_windows_acceptance_batch_contracts() -> None:
    host = (ROOT / "VERIFY_WINDOWS_HOST_ACCEPTANCE.bat").read_text(encoding="utf-8", errors="replace")
    runtime = (ROOT / "VERIFY_WINDOWS_RUNTIME.bat").read_text(encoding="utf-8", errors="replace")
    release = (ROOT / "VERIFY_RELEASE_INTEGRITY.bat").read_text(encoding="utf-8", errors="replace")
    for source in (host, runtime, release):
        assert "v1.10.5" in source
        assert "if not defined CHATBACKUP_NO_PAUSE pause" in source
    bootstrap = (ROOT / "bootstrap/bootstrap.ps1").read_text(encoding="utf-8-sig")
    assert "-Mode VerifyHost" in host
    assert "-Mode VerifyRuntime" in runtime
    assert "-Mode VerifyRelease" in release
    assert "$python = $runtime.Python.Executable" in bootstrap
    assert all(f"& $python (Join-Path $Root \"tests\\{name}.py\")" in bootstrap for name in (
        "runtime_readback_probe", "release_integrity_probe", "host_acceptance_probe",
    ))
    runtime_probe = (ROOT / "tests/runtime_readback_probe.py").read_text(encoding="utf-8")
    assert 'runpy.run_path(str(APP / "chatbackup_gui.pyw"))' in runtime_probe
    assert "GUI_BROWSER_RECOVERY_DIALOG" in runtime_probe


def test_pc_integrity_rejects_tampered_release_file(tmp_path) -> None:
    import shutil

    for name in ("tests/release_integrity_probe.py", "CURRENT_RELEASE_INDEX.md", "MANIFEST.sha256"):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    target = tmp_path / "CURRENT_RELEASE_INDEX.md"
    target.write_bytes(target.read_bytes() + b"modified")
    proc = subprocess.run(
        [sys.executable, str(tmp_path / "tests/release_integrity_probe.py")],
        capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 2, proc.stdout + proc.stderr
    report = json.loads((tmp_path / "runtime_readback/release_integrity_readback.json").read_text(encoding="utf-8"))
    pc_manifest = next(row for row in report["checks"] if row["name"] == "PC_MANIFEST")
    assert pc_manifest["status"] == "FAIL"
    assert json.loads(pc_manifest["detail"])["mismatch"] == ["CURRENT_RELEASE_INDEX.md"]
