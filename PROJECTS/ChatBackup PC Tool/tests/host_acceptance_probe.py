"""Host acceptance for a public ChatGPT share, with a strictly offline fixture mode.

Fixture evidence never closes the Windows host gate. No credentials are accessed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from chatbackup_backend import ChatBackend  # noqa: E402
from chatbackup_core import (  # noqa: E402
    build_json_export, build_jsonl_export, build_markdown,
    build_parser_receipt, build_structure_inspector_json,
    normalize_and_validate_share_url, write_verified,
)

SCHEMA = "666.chatbackup.windows-host-acceptance.v1"


def fixture_page() -> str:
    data = {
        "conversation_id": "fixture-local", "title": "Offline acceptance fixture",
        "mapping": {"m1": {"message": {
            "id": "m1", "author": {"role": "user"}, "recipient": "all",
            "status": "finished_successfully",
            "content": {"content_type": "text", "parts": ["Fixture — äöü 🚀\r\nline two"]},
            "metadata": {},
        }}},
        "linear_conversation": [{"id": "m1"}],
    }
    payload = {"props": {"pageProps": {"serverResponse": {"data": data}}}}
    return '<html><script id="__NEXT_DATA__" type="application/json">' + json.dumps(payload) + '</script></html>'


def execute(*, fixture: bool, share_url: str) -> tuple[dict, int]:
    is_windows = platform.system().lower() == "windows"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out = ROOT / "runtime_readback" / f"host_acceptance_{stamp}"
    out.mkdir(parents=True, exist_ok=False)
    checks: list[dict] = []
    report = {
        "schema": SCHEMA, "status": "HOST_ACCEPTANCE_PENDING",
        "mode": "fixture" if fixture else "live-public-share",
        "isWindowsHost": is_windows, "platform": platform.platform(),
        "executedAtUtc": datetime.now(timezone.utc).isoformat(),
        "checks": checks, "messageCount": 0, "failed": 0,
    }

    def check(name: str, cond: bool, detail: str = "") -> None:
        checks.append({"name": name, "status": "PASS" if cond else "FAIL", "detail": detail})

    try:
        url = "https://chatgpt.com/share/fixture" if fixture else normalize_and_validate_share_url(share_url)
        check("PUBLIC_SHARE_URL_VALID", True)
        backend = ChatBackend()
        chat = backend.parse_html(fixture_page(), url) if fixture else backend.load(url)
        report["messageCount"] = len(chat.messages)
        check("SHARE_PARSED", bool(chat.messages), f"parser={chat.parser}")
        markdown = build_markdown(chat)
        machine = build_json_export(content=markdown, title=chat.title,
                                    source_url=url, source_mode="share-link", chat=chat)
        jsonl = build_jsonl_export(content=markdown, title=chat.title,
                                  source_url=url, source_mode="share-link", chat=chat)
        structure = build_structure_inspector_json(chat)
        parser_receipt = json.dumps(build_parser_receipt(chat), ensure_ascii=False, indent=2) + "\n"
        exports = {
            "chat.md": markdown,
            "chat.json": machine,
            "chat.jsonl": jsonl,
            "structure.json": structure,
            "parser_receipt.json": parser_receipt,
        }
        with tempfile.TemporaryDirectory(prefix="chatbackup_host_accept_") as tmp:
            for name, content in exports.items():
                path = write_verified(Path(tmp) / name, content)
                check("BYTE_READBACK_" + name.upper().replace(".", "_"),
                      path.read_bytes() == content.encode("utf-8"),
                      hashlib.sha256(path.read_bytes()).hexdigest())
            doc = json.loads((Path(tmp) / "chat.json").read_text(encoding="utf-8"))
            jsonl_rows = [json.loads(s) for s in (Path(tmp) / "chat.jsonl").read_text(encoding="utf-8").splitlines()]
            structure_doc = json.loads((Path(tmp) / "structure.json").read_text(encoding="utf-8"))
            parsed_receipt = json.loads((Path(tmp) / "parser_receipt.json").read_text(encoding="utf-8"))
        count = len(chat.messages)
        check("JSON_MESSAGE_COUNT_READBACK", len(doc.get("messages", [])) == count)
        check("JSONL_MESSAGE_COUNT_READBACK", sum(r.get("recordType") == "message" for r in jsonl_rows) == count)
        check("STRUCTURE_MESSAGE_COUNT_READBACK", structure_doc.get("summary", {}).get("messageCount") == count and len(structure_doc.get("messages", [])) == count)
        check("PARSER_RECEIPT_SCHEMA", parsed_receipt.get("schema") == "666.chatbackup.parser-receipt.v1")
        check("MARKDOWN_CONTENT_NONEMPTY", bool(markdown.strip()))
    except Exception as exc:
        # A failed live import never writes the remote HTML or chat content into the receipt.
        check("ACCEPTANCE_PIPELINE", False, type(exc).__name__ + ": " + str(exc)[:250])
    report["failed"] = sum(c["status"] != "PASS" for c in checks)
    if report["failed"]:
        report["status"] = "WINDOWS_HOST_ACCEPTANCE_FAIL"
        exit_code = 2
    elif fixture:
        report["status"] = "FIXTURE_ACCEPTANCE_PASS_HOST_GATE_NOT_CLOSED"
        exit_code = 3
    elif not is_windows:
        report["status"] = "NON_WINDOWS_ACCEPTANCE_PASS_HOST_GATE_NOT_CLOSED"
        exit_code = 3
    else:
        report["status"] = "WINDOWS_HOST_ACCEPTANCE_PASS"
        exit_code = 0
    receipt = out / "windows_host_acceptance_receipt.json"
    receipt.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "checks": len(checks),
                      "failed": report["failed"], "messageCount": report["messageCount"],
                      "receipt": str(receipt)}, ensure_ascii=False))
    return report, exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description="666 ChatBackup Windows Host Acceptance")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fixture", action="store_true", help="offline fixture; never closes the host gate")
    group.add_argument("--share-url", help="public ChatGPT share URL (real host only)")
    args = parser.parse_args()
    _, rc = execute(fixture=args.fixture, share_url=args.share_url or "")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
