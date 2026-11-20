import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from chatbackup_core import (  # noqa: E402
    build_javascript_export,
    build_json_export,
    build_jsonl_export,
    build_markdown,
    build_parser_receipt,
    build_raw_source_bundle,
    chat_asset_key,
    enrich_chat_image_urls_from_html,
    extract_copy_fields,
    extract_legacy_next_data,
    normalize_and_validate_share_url,
    parse_shared_conversation,
    reparse_share_source,
    analyze_manual_transcript,
    write_verified,
    APP_VERSION,
)


def fixture_html() -> str:
    data = {
        "conversation_id": "abc123",
        "title": "Test Chat",
        "mapping": {
            "m1": {
                "message": {
                    "id": "m1",
                    "author": {"role": "user"},
                    "recipient": "all",
                    "status": "finished_successfully",
                    "content": {"content_type": "text", "parts": ["Hallo"]},
                    "metadata": {},
                }
            },
            "m2": {
                "message": {
                    "id": "m2",
                    "author": {"role": "assistant"},
                    "recipient": "all",
                    "status": "finished_successfully",
                    "content": {"content_type": "text", "parts": ["Hallo zurück"]},
                    "metadata": {},
                }
            },
        },
        "linear_conversation": [{"id": "m1"}, {"id": "m2"}],
    }
    payload = {"props": {"pageProps": {"serverResponse": {"data": data}}}}
    return '<html><script id="__NEXT_DATA__" type="application/json">' + json.dumps(payload) + "</script></html>"


def test_normalize_share_url():
    assert normalize_and_validate_share_url("http://chatgpt.com/share/abc#x") == "https://chatgpt.com/share/abc"


def test_parse_legacy_fixture():
    html = fixture_html()
    assert extract_legacy_next_data(html)
    chat = parse_shared_conversation(html, "https://chatgpt.com/share/abc")
    assert chat.title == "Test Chat"
    assert len(chat.messages) == 2
    markdown = build_markdown(chat)
    assert "Hallo zurück" in markdown
    assert "Export-Integrität" in markdown


def test_javascript_export_is_structurally_safe():
    js = build_javascript_export("Backtick ` und ${x}", "Titel")
    assert "const CHAT_BACKUP_EXPORT" in js
    assert '"content": "Backtick ` und ${x}"' in js


def test_verified_write(tmp_path):
    target = tmp_path / "backup.md"
    write_verified(target, "abc\n")
    assert target.read_text(encoding="utf-8") == "abc\n"


def test_verified_write_preserves_mixed_line_endings(tmp_path):
    content = "A\r\nB\rC\nD\r\n"
    target = tmp_path / "mixed.md"
    write_verified(target, content)
    assert target.read_bytes() == content.encode("utf-8")


def test_verified_write_long_chat_exact(tmp_path):
    block = "Benutzer\r\nZeile 1\nAssistant\rZeile 2 — äöü 🚀\n"
    content = block * 50000
    target = tmp_path / "long_chat.md"
    write_verified(target, content)
    assert target.stat().st_size == len(content.encode("utf-8"))
    assert target.read_bytes() == content.encode("utf-8")


def test_static_dom_fallback():
    html = '''<html><head><title>ChatGPT - DOM Test</title></head><body>
    <article data-message-author-role="user"><div>Zeile 1<br>Zeile 2</div></article>
    <article data-message-author-role="assistant"><div>Antwort</div></article>
    </body></html>'''
    chat = parse_shared_conversation(html, "https://chatgpt.com/share/dom")
    assert chat.parser == "static-dom-fallback"
    assert len(chat.messages) == 2
    assert "Zeile 2" in chat.messages[0].text


def test_ssr_dom_transcript_preserves_turns_and_images():
    html = """<html><head><title>ChatGPT - SSR &amp; Test</title></head><body>
    <p>Log in or sign up</p>
    <li data-message-role="user">Out of transcript</li>
    <ol data-conversation-transcript>
      <li id="m1" data-message-role="user"><div data-user-message-copy>Again</div>Copy</li>
      <li id="m2" data-message-role="assistant"><div data-assistant-markdown-root>
        <p>Antwort</p><img src="https://example.invalid/chat.png" alt="Diagramm"/>
      </div><button>Copy</button></li>
      <li id="m3" data-message-role="user"><div data-user-message-copy>Again</div></li>
      <li id="m4" data-message-role="assistant"><img src="https://example.invalid/image-only.png"></li>
    </ol></body></html>"""
    chat = parse_shared_conversation(html, "https://chatgpt.com/share/example")
    assert chat.title == "SSR & Test"
    assert chat.parser == "ssr-dom-transcript"
    assert [(m.message_id, m.role, m.text) for m in chat.messages] == [
        ("m1", "user", "Again"),
        ("m2", "assistant", "Antwort"),
        ("m3", "user", "Again"),
        ("m4", "assistant", ""),
    ]
    assert chat.messages[0].participant_resolution == "UNRESOLVED"
    assert chat.messages[1].assets[0].name == "Diagramm"
    assert chat.messages[3].assets[0].url == "https://example.invalid/image-only.png"
    assert chat.integrity_profile()["sourceStatus"] == "DOM_FALLBACK"


def test_dependency_manifest_and_bootstrap_contract():
    manifest_path = ROOT / "bootstrap" / "dependencies.json"
    bootstrap_path = ROOT / "bootstrap" / "bootstrap.ps1"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    bootstrap = bootstrap_path.read_text(encoding="utf-8")

    assert manifest["toolVersion"] == "1.10.5"
    assert manifest["runtime"]["python"]["minimumVersion"] == "3.10.0"
    assert manifest["runtime"]["python"]["preferredInstallLine"] == "3.14"
    assert manifest["runtime"]["nodejs"]["required"] is False
    assert manifest["runtime"]["npm"]["required"] is False
    assert manifest["runtime"]["pythonPackages"]["requiredForSource"] is True
    assert "Pillow>=11,<13" in manifest["runtime"]["pythonPackages"]["packages"]
    assert manifest["build"]["pyinstaller"]["versionSpec"] == ">=6.17,<7.0"

    assert "Get-AuthenticodeSignature" in bootstrap
    assert "Python Software Foundation" in bootstrap
    assert "Update-PythonIfRequired" in bootstrap
    assert "Include_tcltk=1" in bootstrap
    assert "NOT_REQUIRED" in bootstrap
    assert "Ensure-RuntimePackages" in bootstrap
    assert "Pillow" in bootstrap


def test_all_launchers_route_through_bootstrap():
    expected = {
        "AUTO_SETUP_AND_START.bat",
        "START_PYTHON.bat",
        "START_EXE.bat",
        "SYSTEM_CHECK_ONLY.bat",
        "BUILD_EXE.bat",
    }
    for name in expected:
        content = (ROOT / name).read_text(encoding="utf-8")
        assert "bootstrap\\bootstrap.ps1" in content


def test_version_is_updated():
    from chatbackup_core import APP_VERSION

    assert APP_VERSION == "1.10.5"


def test_v140_gui_assets_and_packaging_contract():
    for name in (
        "header_banner.png",
        "app_logo.png",
        "app_icon_64.png",
        "chatbackup.ico",
    ):
        assert (ROOT / "assets" / name).is_file()
    spec = (ROOT / "666_CHATBACKUP_PC_TOOL.spec").read_text(encoding="utf-8")
    for name in ("header_banner.png", "app_logo.png", "app_icon_64.png", "chatbackup.ico"):
        assert name in spec


def test_v140_gui_branding_and_progress_contract():
    gui = (ROOT / "app" / "chatbackup_gui.pyw").read_text(encoding="utf-8")
    assert "COPYRIGHT 2026 BY FRAGGLEPOWER666 - 666SOUNDsDESIGN" in gui
    assert "NeonButton" in gui
    assert "_start_chunked_insert" in gui
    assert "Einfügen läuft" in gui
    assert "open_settings" in gui
    assert "fill=PINK" in gui
    assert "Maschinen-JSON" in gui
    assert "Portable ZIP + Bilder" in gui
    assert "save_portable_zip" in gui
    assert "Chat-Bilder ansehen & auswählen" in gui
    assert "open_chat_image_browser" in gui
    assert "Nur direkt erreichbare" in gui
    assert "Mit Backup speichern" in gui
    assert "SKIPPED_BY_USER" in gui
    assert "PIL_AVAILABLE" in gui
    assert "1600" in gui and "930" in gui


def test_machine_json_and_jsonl_are_structured():
    html = fixture_html()
    chat = parse_shared_conversation(html, "https://chatgpt.com/share/abc")
    content = build_markdown(chat)
    raw = build_json_export(
        content=content,
        title=chat.title,
        source_url=chat.source_url,
        source_mode="share-link",
        chat=chat,
    )
    payload = json.loads(raw)
    assert payload["schema"] == "666.chatbackup.machine.v1"
    assert payload["toolVersion"] == "1.10.5"
    assert len(payload["messages"]) == 2
    assert payload["messages"][0]["role"] == "user"
    assert payload["renderedContentSha256"]

    jsonl = build_jsonl_export(
        content=content,
        title=chat.title,
        source_url=chat.source_url,
        source_mode="share-link",
        chat=chat,
    )
    rows = [json.loads(line) for line in jsonl.splitlines()]
    assert rows[0]["recordType"] == "metadata"
    assert any(row["recordType"] == "message" for row in rows)
    assert rows[-1]["recordType"] == "renderedContent"


def test_image_asset_pointer_is_preserved_machine_readable():
    data = {
        "conversation_id": "asset123",
        "title": "Bildtest",
        "mapping": {
            "m1": {
                "message": {
                    "id": "m1",
                    "author": {"role": "user"},
                    "recipient": "all",
                    "status": "finished_successfully",
                    "content": {
                        "content_type": "multimodal_text",
                        "parts": [
                            {"content_type": "text", "text": "Bild dabei"},
                            {"content_type": "image_asset_pointer", "asset_pointer": "file-service://asset-abc"},
                        ],
                    },
                    "metadata": {},
                }
            }
        },
        "linear_conversation": [{"id": "m1"}],
    }
    payload = {"props": {"pageProps": {"serverResponse": {"data": data}}}}
    html = '<html><script id="__NEXT_DATA__" type="application/json">' + json.dumps(payload) + "</script></html>"
    chat = parse_shared_conversation(html, "https://chatgpt.com/share/asset")
    assert len(chat.messages[0].assets) == 1
    assert chat.messages[0].assets[0].kind == "image"
    assert chat.messages[0].assets[0].asset_pointer == "file-service://asset-abc"
    machine = json.loads(
        build_json_export(
            content=build_markdown(chat),
            title=chat.title,
            source_url=chat.source_url,
            source_mode="share-link",
            chat=chat,
        )
    )
    assert machine["assets"][0]["assetPointer"] == "file-service://asset-abc"
    assert machine["assets"][0]["downloadable"] is False



def test_chat_image_selection_is_machine_readable():
    data = {
        "conversation_id": "asset-select",
        "title": "Bildauswahl",
        "mapping": {
            "m1": {
                "message": {
                    "id": "m1",
                    "author": {"role": "user"},
                    "recipient": "all",
                    "status": "finished_successfully",
                    "content": {
                        "content_type": "multimodal_text",
                        "parts": [
                            {"content_type": "text", "text": "Zwei Bilder"},
                            {"content_type": "image_asset_pointer", "asset_pointer": "https://files.oaiusercontent.com/file-a.png", "name": "A.png"},
                            {"content_type": "image_asset_pointer", "asset_pointer": "https://files.oaiusercontent.com/file-b.png", "name": "B.png"},
                        ],
                    },
                    "metadata": {},
                }
            }
        },
        "linear_conversation": [{"id": "m1"}],
    }
    payload = {"props": {"pageProps": {"serverResponse": {"data": data}}}}
    html = '<html><script id="__NEXT_DATA__" type="application/json">' + json.dumps(payload) + "</script></html>"
    chat = parse_shared_conversation(html, "https://chatgpt.com/share/select")
    first_key = chat_asset_key(1, 1, chat.messages[0].assets[0])
    machine = json.loads(
        build_json_export(
            content=build_markdown(chat),
            title=chat.title,
            source_url=chat.source_url,
            source_mode="share-link",
            chat=chat,
            selected_asset_keys={first_key},
        )
    )
    assert machine["schemaVersion"] == "1.3.0"
    assert machine["assetSelection"]["mode"] == "explicit"
    assert machine["assetSelection"]["chatImageCount"] == 2
    assert machine["assetSelection"]["selectedChatImageCount"] == 1
    assert machine["assets"][0]["selectedForPortable"] is True
    assert machine["assets"][1]["selectedForPortable"] is False
    assert machine["assets"][0]["assetKey"] == first_key


def test_pointer_only_image_can_be_enriched_from_share_html_url():
    data = {
        "conversation_id": "asset-enrich",
        "title": "Bild URL",
        "mapping": {
            "m1": {
                "message": {
                    "id": "m1",
                    "author": {"role": "assistant"},
                    "recipient": "all",
                    "status": "finished_successfully",
                    "content": {
                        "content_type": "multimodal_text",
                        "parts": [
                            {"content_type": "image_asset_pointer", "asset_pointer": "file-service://file-abc123", "name": "Chatbild"}
                        ],
                    },
                    "metadata": {},
                }
            }
        },
        "linear_conversation": [{"id": "m1"}],
    }
    payload = {"props": {"pageProps": {"serverResponse": {"data": data}}}}
    html = (
        '<html><script id="__NEXT_DATA__" type="application/json">'
        + json.dumps(payload)
        + '</script><script>const x="https://files.oaiusercontent.com/files/file-abc123/generated.png?sig=1";</script></html>'
    )
    chat = parse_shared_conversation(html, "https://chatgpt.com/share/enrich")
    assert not chat.messages[0].assets[0].url
    changed = enrich_chat_image_urls_from_html(chat, html)
    assert changed == 1
    assert "file-abc123" in chat.messages[0].assets[0].url


def test_windows_powershell51_bootstrap_is_ascii_only():
    data = (ROOT / "bootstrap" / "bootstrap.ps1").read_bytes()
    assert data.startswith(b"\xef\xbb\xbf")
    body = data[3:]
    assert body
    assert all(byte < 128 for byte in body)
    assert b"\r\n" in body
    assert b"NOT_REQUIRED" in body
    assert b"\xe2\x80\x94" not in body


def test_v150_preserves_lossless_message_fields():
    data = {
        "conversation_id": "lossless",
        "title": "Lossless",
        "mapping": {
            "m1": {
                "message": {
                    "id": "m1",
                    "author": {"role": "assistant"},
                    "recipient": "all",
                    "status": "finished_successfully",
                    "create_time": 1700000000,
                    "content": {
                        "content_type": "code",
                        "language": "javascript",
                        "text": "const mainPrompt = `Hello`;\nGenUI.copy(mainPrompt);",
                    },
                    "metadata": {"custom": {"keep": True}},
                }
            }
        },
        "linear_conversation": [{"id": "m1"}],
    }
    payload = {"props": {"pageProps": {"serverResponse": {"data": data}}}}
    html = '<html><script id="__NEXT_DATA__" type="application/json">' + json.dumps(payload) + "</script></html>"
    chat = parse_shared_conversation(html, "https://chatgpt.com/share/lossless")
    msg = chat.messages[0]
    assert msg.message_id == "m1"
    assert msg.content_type == "code"
    assert msg.raw_content["language"] == "javascript"
    assert msg.raw_metadata["custom"]["keep"] is True
    assert msg.copy_fields[0].identifier == "mainPrompt"
    assert msg.copy_fields[0].resolved is True
    machine = json.loads(build_json_export(content=build_markdown(chat), title=chat.title, source_url=chat.source_url, source_mode="share-link", chat=chat))
    assert machine["schemaVersion"] == "1.3.0"
    assert machine["messages"][0]["id"] == "m1"
    assert machine["messages"][0]["rawContent"]["language"] == "javascript"
    assert machine["messages"][0]["copyFields"][0]["text"] == "Hello"


def test_v150_copy_field_dynamic_expression_stays_unresolved():
    result = extract_copy_fields("const mainPrompt = `Hello ${name}`; GenUI.copy(mainPrompt);")
    assert len(result["fields"]) == 1
    assert result["fields"][0].resolved is False
    assert any("Dynamischer Template-Ausdruck" in warning for warning in result["warnings"])


def test_v150_raw_source_bundle_and_parser_receipt():
    html = fixture_html()
    chat = reparse_share_source(html, "https://chatgpt.com/share/abc")
    bundle = build_raw_source_bundle(chat)
    receipt = build_parser_receipt(chat)
    assert bundle["schema"] == "666.chatbackup.raw-source.v2"
    assert bundle["messages"][0]["rawContent"]["content_type"] == "text"
    assert receipt["schema"] == "666.chatbackup.parser-receipt.v1"
    assert receipt["sourceHtmlSha256"]
    assert receipt["sourceCaptureStatus"] == "RAW_PRESERVED_REPARSED"
    assert receipt["integrity"]["visualParity"] == "NOT_CLAIMED"


def test_v150_parser_provenance_and_integrity_profile():
    html = fixture_html()
    chat = parse_shared_conversation(html, "https://chatgpt.com/share/abc")
    assert chat.parser_attempts
    assert chat.parser_attempts[-1]["status"] == "PASS"
    profile = chat.integrity_profile()
    assert profile["sourceStatus"] == "SOURCE_OK"
    assert profile["visualParity"] == "NOT_CLAIMED"
    assert profile["uiBindings"] == "UI_BINDINGS_NOT_DETECTED"


def test_v150_gui_structure_inspector_and_raw_setting_contract():
    gui = (ROOT / "app" / "chatbackup_gui.pyw").read_text(encoding="utf-8")
    assert "Struktur-Inspector" in gui
    assert "open_structure_inspector" in gui
    assert "preserve_raw_share_source" in gui
    assert "conversation.raw.json" in gui
    assert "parser_receipt.json" in gui
    assert "share-source.html.gz" in gui


def test_v170_manual_private_help_and_analysis_contract():
    gui = (ROOT / "app" / "chatbackup_gui.pyw").read_text(encoding="utf-8")
    core = (ROOT / "app" / "chatbackup_core.py").read_text(encoding="utf-8")
    assert "Private / Manual" in gui
    assert "Privat / Manuell" in gui
    assert "WHEN CHATGPT SAYS THE CHAT IS FULL" in gui
    assert "WENN CHATGPT „CHAT VOLL“ MELDET" in gui
    assert "open_private_manual_import" in gui
    assert "_ensure_manual_analysis_for_export" in gui
    assert "analyze_manual_transcript" in core
    assert "manual-transcript" in core


def test_structured_group_chat_participants_are_preserved():
    data = {
        "conversation_id": "group-1",
        "title": "Group Test",
        "is_group_chat": True,
        "participants": [
            {"participant_id": "p1", "display_name": "Alice", "username": "alice"},
            {"participant_id": "p2", "display_name": "Bob", "username": "bob"},
        ],
        "mapping": {
            "m1": {"message": {"id": "m1", "author": {"role": "user", "participant_id": "p1"}, "recipient": "all", "status": "finished_successfully", "content": {"content_type": "text", "parts": ["Hi from Alice"]}, "metadata": {}}},
            "m2": {"message": {"id": "m2", "author": {"role": "user", "participant_id": "p2"}, "recipient": "all", "status": "finished_successfully", "content": {"content_type": "text", "parts": ["Hi from Bob"]}, "metadata": {}}},
            "m3": {"message": {"id": "m3", "author": {"role": "assistant"}, "recipient": "all", "status": "finished_successfully", "content": {"content_type": "text", "parts": ["Hello group"]}, "metadata": {}}},
        },
        "linear_conversation": [{"id": "m1"}, {"id": "m2"}, {"id": "m3"}],
    }
    payload = {"props": {"pageProps": {"serverResponse": {"data": data}}}}
    html = '<html><script id="__NEXT_DATA__" type="application/json">' + json.dumps(payload) + '</script></html>'
    chat = parse_shared_conversation(html, "https://chatgpt.com/share/group")
    assert chat.is_group_chat is True
    assert chat.messages[0].author == "Alice"
    assert chat.messages[1].author == "Bob"
    assert chat.messages[0].participant_id == "p1"
    machine = json.loads(build_json_export(content=build_markdown(chat), title=chat.title, source_url=chat.source_url, source_mode="share-link", chat=chat))
    assert machine["schemaVersion"] == "1.3.0"
    assert machine["conversation"]["isGroupChat"] is True
    assert machine["conversation"]["participantCount"] == 3
    assert machine["messages"][1]["participantDisplayName"] == "Bob"


def test_manual_group_chat_role_and_participant_recovery():
    pasted = "Alice:\nFirst\n\nBob:\nSecond\n\nChatGPT:\nAnswer\n\nAlice:\nThird"
    chat = analyze_manual_transcript(pasted, title="Manual Group")
    assert chat.is_group_chat is True
    assert [m.author for m in chat.messages] == ["Alice", "Bob", "ChatGPT", "Alice"]
    humans = [p.display_name for p in chat.participants if p.kind == "human"]
    assert set(humans) == {"Alice", "Bob"}
    assert all(m.participant_resolution != "UNRESOLVED" for m in chat.messages)

def test_manual_single_chat_does_not_become_group():
    pasted = "You said:\nHello\n\nChatGPT said:\nHi"
    chat = analyze_manual_transcript(pasted)
    assert chat.is_group_chat is False
    assert len([p for p in chat.participants if p.kind == "human"]) == 1



def test_v181_manual_markdown_headings_inside_response_do_not_become_participants():
    pasted = """You said:\nPlease explain this.\n\nChatGPT said:\n## Introduction\nText\n\n## Details\nMore text\n\n## Summary\nDone"""
    chat = analyze_manual_transcript(pasted)
    assert chat.is_group_chat is False
    assert len(chat.messages) == 2
    assert [m.author for m in chat.messages] == ["Benutzer", "ChatGPT"]
    assert "## Introduction" in chat.messages[1].text
    assert "## Details" in chat.messages[1].text


def test_v181_exported_group_markdown_headings_round_trip_with_separators():
    pasted = """# Group\n\n---\n\n## Alice\n\nFirst\n\n---\n\n## Bob\n\nSecond\n\n---\n\n## ChatGPT\n\nAnswer\n\n---\n\n## Alice\n\nThird"""
    chat = analyze_manual_transcript(pasted, title="Roundtrip")
    assert chat.is_group_chat is True
    assert [m.author for m in chat.messages] == ["Alice", "Bob", "ChatGPT", "Alice"]


def test_v181_structured_assistant_identity_is_preserved():
    data = {
        "conversation_id": "group-assistant",
        "is_group_chat": True,
        "participants": [
            {"participant_id": "p1", "display_name": "Alice", "role": "user"},
            {"participant_id": "bot-1", "display_name": "Research GPT", "role": "assistant", "kind": "assistant"},
        ],
        "mapping": {
            "m1": {"message": {"id": "m1", "author": {"role": "user", "participant_id": "p1"}, "recipient": "all", "status": "finished_successfully", "content": {"content_type": "text", "parts": ["Question"]}, "metadata": {}}},
            "m2": {"message": {"id": "m2", "author": {"role": "assistant", "participant_id": "bot-1"}, "recipient": "all", "status": "finished_successfully", "content": {"content_type": "text", "parts": ["Answer"]}, "metadata": {}}},
        },
        "linear_conversation": [{"id": "m1"}, {"id": "m2"}],
    }
    payload = {"props": {"pageProps": {"serverResponse": {"data": data}}}}
    html = '<html><script id="__NEXT_DATA__" type="application/json">' + json.dumps(payload) + '</script></html>'
    chat = parse_shared_conversation(html, "https://chatgpt.com/share/group-assistant")
    assert chat.messages[1].participant_id == "bot-1"
    assert chat.messages[1].participant_display_name == "Research GPT"
    assert any(p.display_name == "Research GPT" and p.kind == "assistant" for p in chat.participants)


def test_v181_package_version_contract_is_consistent():
    version = json.loads((ROOT / "VERSION.json").read_text(encoding="utf-8"))["version"]
    deps = json.loads((ROOT / "bootstrap" / "dependencies.json").read_text(encoding="utf-8-sig"))["toolVersion"]
    bootstrap = (ROOT / "bootstrap" / "bootstrap.ps1").read_text(encoding="utf-8-sig")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert version == APP_VERSION == "1.10.5"
    assert deps == APP_VERSION
    assert f'toolVersion = "{APP_VERSION}"' in bootstrap
    assert readme.startswith(f"# 666 ChatBackup PC Tool v{APP_VERSION}")
