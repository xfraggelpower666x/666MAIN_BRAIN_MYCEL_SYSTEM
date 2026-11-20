"""Optional R5.1 additions: resumable batch, indexed search and local conversation viewer.

No codepath automatically invokes these features. The original source ZIP is never
modified or extracted. SQLite and checkpoint JSON are rebuildable derivatives.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from pathlib import Path
from typing import Callable

from archive_intelligence import ArchiveCatalog, ArchiveImportError, load_export, completeness

CHECKPOINT_SCHEMA = "666.chatbackup.batch-checkpoint.v1"
MAX_BATCH_FILES = 10000


def _file_digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _read_checkpoint(path: Path) -> dict:
    if not path.exists():
        return {"schema": CHECKPOINT_SCHEMA, "completed": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if (
        not isinstance(data, dict)
        or data.get("schema") != CHECKPOINT_SCHEMA
        or not isinstance(data.get("completed"), dict)
    ):
        raise ArchiveImportError("Invalid batch checkpoint")
    return data


def _write_checkpoint(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".temporary")
    if temp.exists():
        raise ArchiveImportError("Existing interrupted checkpoint write")
    try:
        with temp.open("x", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, sort_keys=True, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def import_directory(
    folder: str | Path,
    database: str | Path,
    checkpoint: str | Path,
    *,
    recursive: bool = False,
    stop: Callable[[], bool] | None = None,
) -> dict:
    """Resume only whole committed ZIPs, ordered by stable relative path.

    Changed ZIP bytes invalidate their completed marker. A failed file is not
    marked completed. Interrupt after a file boundary with stop().
    """
    directory = Path(folder).resolve()
    if not directory.is_dir():
        raise ArchiveImportError("Batch directory does not exist")
    files = sorted(directory.rglob("*.zip") if recursive else directory.glob("*.zip"))
    files = [f for f in files if f.is_file()]
    if len(files) > MAX_BATCH_FILES:
        raise ArchiveImportError("Too many ZIP files")
    marker_path = Path(checkpoint).resolve()
    db_path = Path(database).resolve()
    if marker_path == db_path:
        raise ArchiveImportError("Checkpoint and database must be separate")
    state = _read_checkpoint(marker_path)
    summary = {"schema": "666.chatbackup.batch-result.v1", "total": len(files),
               "imported": 0, "unchanged_files": 0, "failed": [], "stopped": False,
               "checkpoint": str(marker_path), "database": str(db_path)}
    with ArchiveCatalog(db_path) as catalog:
        for item in files:
            if stop is not None and stop():
                summary["stopped"] = True
                break
            relative = item.relative_to(directory).as_posix()
            try:
                digest = _file_digest(item)
                if state["completed"].get(relative) == digest:
                    summary["unchanged_files"] += 1
                    continue
                chats, report = load_export(item)
                if report["status"] != "PASS":
                    raise ArchiveImportError("Source incomplete: " + report["status"])
                catalog.add(chats, digest, relative)
                # Mark complete only after all database transactions committed.
                state["completed"][relative] = digest
                _write_checkpoint(marker_path, state)
                summary["imported"] += 1
            except (OSError, ValueError, sqlite3.DatabaseError) as exc:
                summary["failed"].append({"file": relative, "error": str(exc)[:300]})
    summary["status"] = "PARTIAL" if summary["failed"] or summary["stopped"] else "PASS"
    return summary


def rebuild_fts(db: ArchiveCatalog) -> dict:
    """Optional FTS5 full-text cache. No destructive migration of source tables."""
    try:
        with db.db:
            db.db.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS message_fts USING fts5("
                "conversation_id UNINDEXED, message_id UNINDEXED, title, role, body, tokenize='unicode61')"
            )
            db.db.execute("DELETE FROM message_fts")
            db.db.execute("""INSERT INTO message_fts(conversation_id,message_id,title,role,body)
              SELECT m.conversation_id,m.message_id,c.title,m.role,m.text
              FROM messages m JOIN conversations c ON c.conversation_id=m.conversation_id""")
        return {"status": "VERIFIED_INDEX_BUILT", "count": db.db.execute(
            "SELECT count(*) FROM message_fts").fetchone()[0]}
    except sqlite3.OperationalError as exc:
        if "fts5" in str(exc).lower():
            return {"status": "FTS5_UNAVAILABLE", "detail": str(exc)}
        raise


def search_fts(db: ArchiveCatalog, term: str, limit: int = 100) -> list[dict]:
    """Literal phrase search, not user-supplied FTS operators."""
    term = term.strip()
    if not term:
        return []
    if len(term) > 500:
        raise ArchiveImportError("Search term too long")
    available = db.db.execute(
        "SELECT 1 FROM sqlite_master WHERE name='message_fts'").fetchone()
    if not available:
        rebuild = rebuild_fts(db)
        if rebuild["status"] == "FTS5_UNAVAILABLE":
            return db.search(term, limit)
    # Treat quotes and operators as literal characters.
    phrase = '"' + term.replace('"', '""') + '"'
    rows = db.db.execute("""SELECT conversation_id,title,message_id,role,
                snippet(message_fts,4,'[',']','…',24)
              FROM message_fts WHERE message_fts MATCH ?
              ORDER BY rank LIMIT ?""",
              (phrase, max(1, min(500, limit)))).fetchall()
    return [dict(zip(("conversation_id","title","message_id","role","snippet"),r))
            for r in rows]


def conversation_view(db: ArchiveCatalog, conversation_id: str) -> dict | None:
    """Read back one indexed conversation without touching archive ZIP."""
    row = db.db.execute("""SELECT conversation_id,title,revision_hash,source_hash,
                filename,modified_at,message_count,integrity
              FROM conversations WHERE conversation_id=?""", (conversation_id,)).fetchone()
    if row is None:
        return None
    detail = dict(zip(("id","title","revision","source_sha256","source_file",
                       "modified_at","message_count","integrity"), row))
    messages = db.db.execute("""SELECT message_id,role,text,parent_id,created_at
              FROM messages WHERE conversation_id=? ORDER BY
              CASE WHEN created_at IS NULL THEN 1 ELSE 0 END,created_at,message_id""",
              (conversation_id,)).fetchall()
    detail["messages"] = [
        dict(zip(("id","role","text","parent","created_at"),m)) for m in messages
    ]
    detail["visual_parity"] = "NOT_CLAIMED"
    return detail
