import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from chatbackup_backend import BackendConfig, ChatBackend


def fixture_html() -> str:
    data = {
        "conversation_id": "backend123",
        "title": "Backend Test",
        "mapping": {
            "m1": {
                "message": {
                    "id": "m1",
                    "author": {"role": "assistant"},
                    "recipient": "all",
                    "status": "finished_successfully",
                    "content": {
                        "content_type": "code",
                        "language": "javascript",
                        "text": "const styleText = `Cyber Neon`;\nGenUI.copy(styleText);",
                    },
                    "metadata": {"origin": "fixture"},
                }
            }
        },
        "linear_conversation": [{"id": "m1"}],
    }
    payload = {"props": {"pageProps": {"serverResponse": {"data": data}}}}
    return '<html><script id="__NEXT_DATA__" type="application/json">' + json.dumps(payload) + "</script></html>"


def test_backend_identity_and_parse_html_preserves_source():
    backend = ChatBackend(BackendConfig(preserve_raw_source=True))
    chat = backend.parse_html(fixture_html(), "https://chatgpt.com/share/backend123")
    assert backend.identity()["backendId"] == "666.chatbackup.backend.v1"
    assert chat.source_capture_status == "RAW_PRESERVED"
    assert chat.source_html
    assert chat.source_html_sha256
    assert chat.messages[0].raw_metadata["origin"] == "fixture"
    assert chat.messages[0].copy_fields[0].text == "Cyber Neon"


def test_backend_raw_limit_is_honest_not_truncated():
    backend = ChatBackend(BackendConfig(preserve_raw_source=True, max_raw_html_chars=10))
    chat = backend.parse_html(fixture_html(), "https://chatgpt.com/share/backend123")
    assert chat.source_html == ""
    assert chat.source_capture_status == "RAW_TOO_LARGE_NOT_STORED"
    assert chat.source_html_sha256


def test_backend_reparse_is_replayable():
    backend = ChatBackend()
    html = fixture_html()
    chat = backend.reparse(html, "https://chatgpt.com/share/backend123")
    assert chat.source_capture_status == "RAW_PRESERVED_REPARSED"
    assert chat.messages[0].message_id == "m1"
    assert chat.parser == "legacy-next-data"


def test_structure_inspector_payload_is_systematic_and_loss_aware():
    backend = ChatBackend()
    chat = backend.parse_html(fixture_html(), "https://chatgpt.com/share/backend123")
    payload = backend.structure_inspector_payload(chat)
    assert payload["schema"] == "666.chatbackup.structure-inspector.v1"
    assert payload["schemaVersion"] == "1.1.0"
    assert payload["summary"]["messageCount"] == 1
    assert payload["summary"]["copyFieldsResolved"] == 1
    message = payload["messages"][0]
    assert message["id"] == "m1"
    assert message["rawMetadata"]["origin"] == "fixture"
    assert message["copyFields"][0]["text"] == "Cyber Neon"
    assert "renderedText" in message
    assert "assets" in message


def test_manual_transcript_analysis_recovers_roles_and_copy_fields():
    backend = ChatBackend()
    pasted = """You said:\nHello\n\nChatGPT said:\nconst styleText = `Cyber Neon`;\nGenUI.copy(styleText);\n"""
    chat = backend.analyze_manual_text(pasted, title="Manual Test")
    assert chat.parser == "manual-transcript"
    assert len(chat.messages) == 2
    assert chat.messages[0].role == "user"
    assert chat.messages[1].role == "assistant"
    assert chat.messages[1].copy_fields[0].text == "Cyber Neon"
    assert chat.integrity_profile()["sourceStatus"] == "MANUAL_STRUCTURED"


def test_manual_transcript_analysis_fallback_does_not_invent_turns():
    backend = ChatBackend()
    chat = backend.analyze_manual_text("plain copied text without role headers")
    assert len(chat.messages) == 1
    assert chat.messages[0].role == "manual"
    assert chat.messages[0].raw_content["sourceText"].startswith("plain copied")
    assert chat.integrity_profile()["sourceStatus"] == "MANUAL_PRESERVED"


def auth_wall_html() -> str:
    return '<html><body><h1>Log in or sign up</h1><button>Continue with Google</button><script>window.__reactRouterContext.streamController.enqueue("[{}]")</script></body></html>'


def test_auth_wall_is_explicit_not_parser_format_error():
    from chatbackup_core import AuthWallDetected, detect_auth_wall
    backend = ChatBackend()
    evidence = detect_auth_wall(auth_wall_html())
    assert evidence["detected"] is True
    try:
        backend.parse_html(auth_wall_html(), "https://chatgpt.com/share/authwall")
    except AuthWallDetected as exc:
        assert exc.code == "AUTH_WALL_DETECTED"
        assert exc.evidence["detected"] is True
        assert exc.source_url.endswith("/share/authwall")
    else:
        raise AssertionError("Auth wall was not raised explicitly")


def test_browser_recovery_uses_fail_closed_manual_analyzer():
    backend = ChatBackend()
    pasted = "You said:\nHello\n\nChatGPT said:\nHi there\n"
    chat = backend.recover_browser_transcript(
        pasted,
        source_url="https://chatgpt.com/share/authwall",
        title="Recovered",
    )
    assert chat.parser == "browser-assisted-transcript"
    assert chat.source_capture_status == "BROWSER_CLIPBOARD_RECOVERY"
    assert chat.source_url.endswith("/share/authwall")
    assert len(chat.messages) == 2
    assert chat.parser_attempts[0]["status"] == "AUTH_WALL_DETECTED"
