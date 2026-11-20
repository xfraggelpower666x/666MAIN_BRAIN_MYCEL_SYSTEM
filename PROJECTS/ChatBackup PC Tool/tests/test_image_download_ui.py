from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUI = ROOT / "app" / "chatbackup_gui.pyw"


def source() -> str:
    return GUI.read_text(encoding="utf-8")


def test_direct_image_download_controls_present():
    text = source()
    assert '"Download": "Download"' in text
    assert '"Ausgewählte herunterladen": "Download Selected"' in text
    assert '"Alle erreichbaren herunterladen": "Download All Reachable"' in text
    assert 'def _download_chat_image_single' in text
    assert 'def _download_chat_image_batch' in text


def test_direct_download_uses_verified_binary_write():
    text = source()
    assert 'self._write_binary_verified(target, data)' in text
    assert 'self._fetch_chat_image_bytes(entry)' in text


def test_portable_zip_still_writes_real_asset_files():
    text = source()
    assert 'target.write_bytes(data)' in text
    assert 'packagePath": f"assets/{target.name}"' in text
    assert 'base64' not in text.lower() or 'not as Base64' in text
