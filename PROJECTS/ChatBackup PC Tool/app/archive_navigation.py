"""Archive Intelligence R5.4 - incremental search, source monitoring and paging.

Offline derivatives only. Original ZIPs are never altered or extracted.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from archive_intelligence import ArchiveCatalog, ArchiveImportError

MAX_PAGE = 250
MAX_SOURCE_AUDIT = 10000


def sync_fts(db: ArchiveCatalog) -> dict[str, Any]:
    """Synchronize only changed/removed conversation IDs into FTS5 atomically.

    A pre-R5.4 cache without an identity ledger is rebuilt once to avoid
    duplicate rows and stale results. Subsequent unchanged calls are cheap.
    """
    conn = db.db
    try:
        conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS message_fts USING fts5("
                     "conversation_id UNINDEXED,message_id UNINDEXED,title,role,"
                     "body,tokenize='unicode61')")
    except sqlite3.OperationalError as exc:
        if "fts5" in str(exc).lower():
            return {"status": "FTS5_UNAVAILABLE", "detail": str(exc)}
        raise
    conn.execute("CREATE TABLE IF NOT EXISTS archive_fts_revisions("
                 "conversation_id TEXT PRIMARY KEY, revision_hash TEXT NOT NULL)")
    total = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
    tracked = conn.execute("SELECT COUNT(*) FROM archive_fts_revisions").fetchone()[0]
    existing_fts = conn.execute("SELECT COUNT(*) FROM message_fts").fetchone()[0]
    # A legacy FTS cache has no revision ledger. Rebuild once, never blindly
    # trust it as current, even if the row count matches.
    migrate = tracked == 0 and existing_fts != 0
    changed = conn.execute("""
        SELECT c.conversation_id,c.revision_hash FROM conversations c
        LEFT JOIN archive_fts_revisions r ON r.conversation_id=c.conversation_id
        WHERE r.conversation_id IS NULL OR r.revision_hash!=c.revision_hash
        ORDER BY c.conversation_id
    """).fetchall()
    removed = conn.execute("""
        SELECT r.conversation_id FROM archive_fts_revisions r
        LEFT JOIN conversations c ON c.conversation_id=r.conversation_id
        WHERE c.conversation_id IS NULL
    """).fetchall()
    if not changed and not removed and not migrate:
        return {"status": "UNCHANGED_CACHE_REUSED", "updated": 0, "removed": 0,
                "count": existing_fts}
    with conn:
        if migrate:
            conn.execute("DELETE FROM message_fts")
            conn.execute("DELETE FROM archive_fts_revisions")
        for (cid,) in removed:
            conn.execute("DELETE FROM message_fts WHERE conversation_id=?", (cid,))
            conn.execute("DELETE FROM archive_fts_revisions WHERE conversation_id=?", (cid,))
        for cid, revision in changed:
            conn.execute("DELETE FROM message_fts WHERE conversation_id=?", (cid,))
            conn.execute("""
                INSERT INTO message_fts(conversation_id,message_id,title,role,body)
                SELECT m.conversation_id,m.message_id,c.title,m.role,m.text
                FROM messages m JOIN conversations c ON c.conversation_id=m.conversation_id
                WHERE m.conversation_id=?
            """, (cid,))
            conn.execute("""INSERT INTO archive_fts_revisions(conversation_id,revision_hash)
                VALUES(?,?) ON CONFLICT(conversation_id)
                DO UPDATE SET revision_hash=excluded.revision_hash""", (cid, revision))
    return {"status": "INCREMENTAL_INDEX_VERIFIED", "updated": len(changed),
            "removed": len(removed), "migrated": migrate,
            "conversations": total,
            "count": conn.execute("SELECT COUNT(*) FROM message_fts").fetchone()[0]}


def search_filtered(
    db: ArchiveCatalog,
    term: str = "",
    *,
    role: str = "",
    source: str = "",
    start_time: float | None = None,
    end_time: float | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Literal substring filter on indexed messages with stable pagination.

    This deliberately avoids exposing FTS query operators and supports exact
    role, source name, message timestamp range and title/body search.
    """
    if len(term) > 500 or len(role) > 80 or len(source) > 1000:
        raise ArchiveImportError("Search filter too long")
    if limit < 1 or limit > MAX_PAGE or offset < 0 or offset > 1_000_000:
        raise ArchiveImportError("Invalid page bounds")
    if start_time is not None and end_time is not None and start_time > end_time:
        raise ArchiveImportError("Invalid time window")
    filters = []
    args: list[Any] = []
    if term.strip():
        filters.append("(instr(lower(m.text),lower(?))>0 OR instr(lower(c.title),lower(?))>0)")
        args.extend([term.strip(), term.strip()])
    if role:
        filters.append("m.role=?")
        args.append(role)
    if source:
        filters.append("c.filename=?")
        args.append(source)
    if start_time is not None:
        filters.append("m.created_at>=?")
        args.append(start_time)
    if end_time is not None:
        filters.append("m.created_at<=?")
        args.append(end_time)
    where = " WHERE " + " AND ".join(filters) if filters else ""
    rows = db.db.execute("""
        SELECT c.conversation_id,c.title,c.filename,c.integrity,
               m.message_id,m.role,m.created_at,substr(m.text,1,500)
        FROM messages m JOIN conversations c ON c.conversation_id=m.conversation_id
    """ + where + """
        ORDER BY COALESCE(m.created_at,c.modified_at,0) DESC,
                 c.conversation_id,m.message_id LIMIT ? OFFSET ?
    """, (*args, limit, offset)).fetchall()
    return [dict(zip(("conversation_id","title","source","integrity","message_id",
                       "role","created_at","snippet"), row)) for row in rows]


def browse_conversations(
    db: ArchiveCatalog,
    *,
    title: str = "",
    source: str = "",
    integrity: str = "",
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    if any(len(x) > 1000 for x in (title, source, integrity)):
        raise ArchiveImportError("Navigation filter too long")
    if limit < 1 or limit > MAX_PAGE or offset < 0 or offset > 1_000_000:
        raise ArchiveImportError("Invalid navigation page")
    where, values = [], []
    if title:
        where.append("instr(lower(title),lower(?))>0")
        values.append(title)
    if source:
        where.append("filename=?")
        values.append(source)
    if integrity:
        where.append("integrity=?")
        values.append(integrity)
    sql = """SELECT conversation_id,title,filename,integrity,modified_at,
                    message_count,revision_hash FROM conversations"""
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY COALESCE(modified_at,0) DESC,conversation_id LIMIT ? OFFSET ?"
    rows = db.db.execute(sql, (*values, limit, offset)).fetchall()
    return [dict(zip(("conversation_id","title","source","integrity","modified_at",
                      "messages","revision"), row)) for row in rows]


def audit_sources(folder: str | Path, checkpoint: str | Path) -> dict[str, Any]:
    """Report missing/changed ZIP sources relative to a checkpoint, read-only."""
    base = Path(folder).resolve()
    if not base.is_dir():
        raise ArchiveImportError("Source directory not found")
    path = Path(checkpoint)
    if not path.is_file():
        raise ArchiveImportError("Checkpoint missing")
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("schema") != "666.chatbackup.batch-checkpoint.v1" or not isinstance(
        state.get("completed"), dict
    ):
        raise ArchiveImportError("Invalid checkpoint")
    entries = state["completed"]
    if len(entries) > MAX_SOURCE_AUDIT:
        raise ArchiveImportError("Source inventory too large")
    results = []
    for name, expected in sorted(entries.items()):
        if not isinstance(name, str) or not isinstance(expected, str):
            raise ArchiveImportError("Malformed source inventory")
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts or not name.lower().endswith(".zip"):
            raise ArchiveImportError("Unsafe source inventory path")
        target = (base / relative).resolve()
        if not target.is_relative_to(base):
            raise ArchiveImportError("Source path escapes base directory")
        if not target.is_file():
            status, found = "MISSING", None
        else:
            digest = hashlib.sha256()
            with target.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            found = digest.hexdigest()
            status = "VERIFIED" if found == expected else "CHANGED"
        results.append({"file": name, "status": status, "sha256": found})
    return {"schema": "666.chatbackup.source-audit.v1",
            "status": "VERIFIED" if all(r["status"] == "VERIFIED" for r in results)
                      else "PARTIAL", "checked": len(results),
            "sources": results, "originals_modified": False}
