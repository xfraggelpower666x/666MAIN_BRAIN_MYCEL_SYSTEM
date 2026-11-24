"""ACE external-chat intake candidate R01: inert, in-memory, read-only.

NOT an installed plugin executor. Requires an explicitly approved host to call.
No persistence, dispatch, cost authorization, external I/O, or native promotion.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Callable

MAX_BYTES = 8 * 1024 * 1024
MAX_MESSAGES = 10000
MAX_TEXT = 100000
PROJECT = "LYVRA_CODING_PROFI"
RELEASE = "0.87.7"
CONTRACT = "ace.host.intake.v1"

class ImportRejected(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise ImportRejected("DUPLICATE_JSON_KEY")
        out[key] = value
    return out


def _string(value: Any, field: str, maximum: int) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise ImportRejected("INVALID_" + field.upper())
    return value


def _valid_messages(root: Any) -> list[dict]:
    if not isinstance(root, dict) or set(root) != {"schema", "messages", "metadata"}:
        raise ImportRejected("INVALID_ROOT_SHAPE")
    if root["schema"] != "ace.export.v1":
        raise ImportRejected("UNSUPPORTED_SCHEMA")
    if not isinstance(root["metadata"], dict):
        raise ImportRejected("INVALID_METADATA")
    messages = root["messages"]
    if not isinstance(messages, list) or len(messages) > MAX_MESSAGES:
        raise ImportRejected("INVALID_MESSAGE_COUNT")
    seen: set[str] = set()
    result: list[dict] = []
    for m in messages:
        if not isinstance(m, dict) or set(m) != {"id", "role", "content"}:
            raise ImportRejected("INVALID_MESSAGE_SHAPE")
        ident = _string(m["id"], "id", 128)
        if not re.fullmatch(r"[A-Za-z0-9_.:-]+", ident) or ident in seen:
            raise ImportRejected("INVALID_OR_DUPLICATE_ID")
        seen.add(ident)
        role = m["role"]
        if type(role) is not str or role not in ("user", "assistant", "system", "tool"):
            raise ImportRejected("INVALID_ROLE")
        content = _string(m["content"], "content", MAX_TEXT)
        result.append({"id": ident, "role": role, "content": content})
    return result


def prepare_import(raw: bytes, *, expected_project: str = PROJECT) -> dict:
    """Return an inert receipt. No actions and no file writes."""
    if expected_project != PROJECT:
        raise ImportRejected("PROJECT_SCOPE_MISMATCH")
    if type(raw) is not bytes or not raw or len(raw) > MAX_BYTES:
        raise ImportRejected("INVALID_INPUT_BYTES_OR_SIZE")
    try:
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(ImportRejected("NONFINITE_NUMBER")))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ImportRejected("MALFORMED_UTF8_JSON") from exc
    messages = _valid_messages(data)
    return {
        "schema": CONTRACT, "status": "CANDIDATE_ONLY", "plugin_version_target": RELEASE,
        "project": PROJECT, "input_sha256": hashlib.sha256(raw).hexdigest(),
        "message_count": len(messages), "authority": "NONE",
        "trust": "UNTRUSTED_INPUT", "native_project_binding": None,
        "writes_performed": False, "dispatch_performed": False,
        "chargeable_actions_allowed": False, "fresh_chat_verified": False,
        "output_persisted": False, "source_roles_are_data": True,
    }


def execute_with_host(raw: bytes, *, host: Any = None, expected_project: str = PROJECT) -> dict:
    """No arbitrary executor injection. Approved hosts may consume receipt separately.

    For actual execution a distinct owner-approved interface must be implemented,
    with capability attestation, scoped authorization and host-side receipts.
    """
    if host is not None:
        raise ImportRejected("HOST_EXECUTOR_NOT_BOUND")
    return prepare_import(raw, expected_project=expected_project)
