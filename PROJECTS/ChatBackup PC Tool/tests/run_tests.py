from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from chatbackup_core import (  # noqa: E402
    APP_VERSION,
    build_javascript_export,
    build_json_export,
    build_jsonl_export,
    build_markdown,
    chat_asset_key,
    enrich_chat_image_urls_from_html,
    normalize_and_validate_share_url,
    parse_shared_conversation,
    write_verified,
)


def main() -> None:
    checks = 0

    assert APP_VERSION == "1.10.5"
    checks += 1

    assert normalize_and_validate_share_url("http://chatgpt.com/share/abc#x") == "https://chatgpt.com/share/abc"
    checks += 1

    data = {
        "conversation_id": "abc123",
        "title": "Test Chat",
        "mapping": {
            "m1": {"message": {"id": "m1", "author": {"role": "user"}, "recipient": "all", "status": "finished_successfully", "content": {"content_type": "text", "parts": ["Hallo"]}, "metadata": {}}},
            "m2": {"message": {"id": "m2", "author": {"role": "assistant"}, "recipient": "all", "status": "finished_successfully", "content": {"content_type": "text", "parts": ["Hallo zurück"]}, "metadata": {}}},
        },
        "linear_conversation": [{"id": "m1"}, {"id": "m2"}],
    }
    payload = {"props": {"pageProps": {"serverResponse": {"data": data}}}}
    html = '<html><script id="__NEXT_DATA__" type="application/json">' + json.dumps(payload) + "</script></html>"
    chat = parse_shared_conversation(html, "https://chatgpt.com/share/abc")
    markdown = build_markdown(chat)
    assert len(chat.messages) == 2
    assert "Hallo zurück" in markdown
    checks += 1

    js = build_javascript_export("Backtick ` und ${x}", "Titel")
    assert "CHAT_BACKUP_EXPORT" in js
    checks += 1

    machine = json.loads(
        build_json_export(
            content=markdown,
            title=chat.title,
            source_url=chat.source_url,
            source_mode="share-link",
            chat=chat,
        )
    )
    assert machine["schema"] == "666.chatbackup.machine.v1"
    assert machine["toolVersion"] == "1.10.5"
    assert len(machine["messages"]) == 2
    jsonl_rows = [
        json.loads(line)
        for line in build_jsonl_export(
            content=markdown,
            title=chat.title,
            source_url=chat.source_url,
            source_mode="share-link",
            chat=chat,
        ).splitlines()
    ]
    assert jsonl_rows[0]["recordType"] == "metadata"
    assert jsonl_rows[-1]["recordType"] == "renderedContent"
    checks += 1

    with tempfile.TemporaryDirectory() as folder:
        target = Path(folder) / "backup.md"
        write_verified(target, markdown)
        assert target.read_text(encoding="utf-8") == markdown
    checks += 1

    with tempfile.TemporaryDirectory() as folder:
        content = ("Benutzer\r\nZeile\nAssistant\rAntwort — äöü 🚀\n" * 50000)
        target = Path(folder) / "long_mixed_chat.md"
        write_verified(target, content)
        assert target.read_bytes() == content.encode("utf-8")
    checks += 1

    manifest = json.loads((ROOT / "bootstrap" / "dependencies.json").read_text(encoding="utf-8"))
    assert manifest["runtime"]["nodejs"]["required"] is False
    assert manifest["runtime"]["npm"]["required"] is False
    assert manifest["runtime"]["python"]["preferredInstallLine"] == "3.14"
    assert "Pillow>=11,<13" in manifest["runtime"]["pythonPackages"]["packages"]
    checks += 1

    bootstrap = (ROOT / "bootstrap" / "bootstrap.ps1").read_text(encoding="utf-8")
    for required_fragment in (
        "Get-AuthenticodeSignature",
        "Python Software Foundation",
        "Update-PythonIfRequired",
        "Include_tcltk=1",
        "NOT_REQUIRED",
    ):
        assert required_fragment in bootstrap
    checks += 1

    for launcher in (
        "AUTO_SETUP_AND_START.bat",
        "START_PYTHON.bat",
        "START_EXE.bat",
        "SYSTEM_CHECK_ONLY.bat",
        "BUILD_EXE.bat",
    ):
        assert "bootstrap\\bootstrap.ps1" in (ROOT / launcher).read_text(encoding="utf-8")
    checks += 1

    for name in ("header_banner.png", "app_logo.png", "app_icon_64.png", "chatbackup.ico"):
        assert (ROOT / "assets" / name).is_file()
    checks += 1

    gui = (ROOT / "app" / "chatbackup_gui.pyw").read_text(encoding="utf-8")
    assert "COPYRIGHT 2026 BY FRAGGLEPOWER666 - 666SOUNDsDESIGN" in gui
    assert "_start_chunked_insert" in gui
    assert "open_settings" in gui
    assert "Maschinen-JSON" in gui
    assert "Portable ZIP + Bilder" in gui
    assert "Chat-Bilder ansehen & auswählen" in gui
    assert "open_chat_image_browser" in gui
    assert "Mit Backup speichern" in gui
    assert "SKIPPED_BY_USER" in gui
    assert "fill=PINK" in gui
    checks += 1

    image_data = {
        "conversation_id": "image-select",
        "title": "Bildauswahl",
        "mapping": {
            "m1": {"message": {"id": "m1", "author": {"role": "user"}, "recipient": "all", "status": "finished_successfully", "content": {"content_type": "multimodal_text", "parts": [{"content_type": "image_asset_pointer", "asset_pointer": "https://files.oaiusercontent.com/a.png", "name": "A.png"}, {"content_type": "image_asset_pointer", "asset_pointer": "https://files.oaiusercontent.com/b.png", "name": "B.png"}]}, "metadata": {}}}
        },
        "linear_conversation": [{"id": "m1"}],
    }
    image_payload = {"props": {"pageProps": {"serverResponse": {"data": image_data}}}}
    image_html = '<html><script id="__NEXT_DATA__" type="application/json">' + json.dumps(image_payload) + "</script></html>"
    image_chat = parse_shared_conversation(image_html, "https://chatgpt.com/share/images")
    first_key = chat_asset_key(1, 1, image_chat.messages[0].assets[0])
    selected_machine = json.loads(build_json_export(content=build_markdown(image_chat), title=image_chat.title, source_url=image_chat.source_url, source_mode="share-link", chat=image_chat, selected_asset_keys={first_key}))
    assert selected_machine["assetSelection"]["selectedChatImageCount"] == 1
    assert selected_machine["assets"][0]["selectedForPortable"] is True
    assert selected_machine["assets"][1]["selectedForPortable"] is False
    checks += 1

    pointer_data = {
        "conversation_id": "enrich",
        "title": "Enrich",
        "mapping": {"m1": {"message": {"id": "m1", "author": {"role": "assistant"}, "recipient": "all", "status": "finished_successfully", "content": {"content_type": "multimodal_text", "parts": [{"content_type": "image_asset_pointer", "asset_pointer": "file-service://file-xyz789", "name": "X"}]}, "metadata": {}}}},
        "linear_conversation": [{"id": "m1"}],
    }
    pointer_payload = {"props": {"pageProps": {"serverResponse": {"data": pointer_data}}}}
    pointer_html = '<html><script id="__NEXT_DATA__" type="application/json">' + json.dumps(pointer_payload) + '</script><script>const u="https://files.oaiusercontent.com/files/file-xyz789/image.png";</script></html>'
    pointer_chat = parse_shared_conversation(pointer_html, "https://chatgpt.com/share/enrich")
    assert enrich_chat_image_urls_from_html(pointer_chat, pointer_html) == 1
    assert "file-xyz789" in pointer_chat.messages[0].assets[0].url
    checks += 1

    bootstrap_bytes = (ROOT / "bootstrap" / "bootstrap.ps1").read_bytes()
    assert bootstrap_bytes.startswith(b"\xef\xbb\xbf")
    bootstrap_body = bootstrap_bytes[3:]
    assert bootstrap_body and all(byte < 128 for byte in bootstrap_body)
    assert b"\r\n" in bootstrap_body
    assert b"NOT_REQUIRED" in bootstrap_body
    checks += 1

    from chatbackup_core import analyze_manual_transcript
    group = analyze_manual_transcript("Alice:\nA\n\nBob:\nB\n\nChatGPT:\nC\n\nAlice:\nD")
    assert group.is_group_chat is True
    assert {p.display_name for p in group.participants if p.kind == "human"} == {"Alice", "Bob"}
    group_machine = json.loads(build_json_export(content=build_markdown(group), title=group.title, source_mode="manual", chat=group))
    assert group_machine["conversation"]["isGroupChat"] is True
    assert group_machine["schemaVersion"] == "1.3.0"
    checks += 1

    print(f"ALL TESTS PASSED ({checks}/{checks})")


if __name__ == "__main__":
    main()
