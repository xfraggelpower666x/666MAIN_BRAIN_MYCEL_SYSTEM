"""Offline R5.4 regression: incremental FTS, filters, navigation and source integrity."""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
from archive_intelligence import ArchiveCatalog, ArchiveConversation, ArchiveMessage, ArchiveImportError
from archive_navigation import sync_fts, browse_conversations, search_filtered, audit_sources
from archive_extensions import search_fts


def chat(cid, title, role, text, stamp, source="export.zip"):
    return ArchiveConversation(cid, title, [ArchiveMessage(
        "message-" + cid, role, text, created_at=stamp)], source, stamp)


def test_incremental_cache_only_updates_changed_messages(tmp_path):
    with ArchiveCatalog(tmp_path / "catalog.sqlite") as db:
        db.add([chat("one","Cyber sound","user","Deep Dark Techno",100)],"sha","one.zip")
        first = sync_fts(db)
        if first["status"] == "FTS5_UNAVAILABLE":
            pytest.skip("SQLite FTS5 not installed")
        assert first["updated"] == 1 and first["count"] == 1
        assert sync_fts(db)["status"] == "UNCHANGED_CACHE_REUSED"
        db.add([chat("two","Forest","assistant","Psytrance",200)],"sha","two.zip")
        changed = sync_fts(db)
        assert changed["updated"] == 1 and changed["count"] == 2
        assert len(search_fts(db,"Psytrance")) == 1
        db.add([chat("one","Cyber sound","user","Industrial Pulse",100)],"sha","one.zip")
        revised = sync_fts(db)
        assert revised["updated"] == 1 and revised["count"] == 2
        assert search_fts(db,"Deep Dark Techno") == []
        assert len(search_fts(db,"Industrial Pulse")) == 1


def test_incremental_cache_deletes_removed_messages(tmp_path):
    with ArchiveCatalog(tmp_path / "cat.db") as db:
        db.add([chat("a","Track","user","Delete me",30)],"sha","a.zip")
        sync_fts(db)
        with db.db:
            db.db.execute("DELETE FROM conversations WHERE conversation_id=?",("a",))
        result=sync_fts(db)
        assert result["removed"] == 1 and result["count"] == 0
        assert search_fts(db,"Delete me") == []


def test_legacy_fts_migration_without_duplicate_results(tmp_path):
    from archive_extensions import rebuild_fts
    with ArchiveCatalog(tmp_path / "legacy.sqlite") as db:
        db.add([chat("a","Original","assistant","Sound power",100)],"sha","a.zip")
        legacy=rebuild_fts(db)
        if legacy["status"] == "FTS5_UNAVAILABLE":
            pytest.skip("SQLite FTS5 not installed")
        assert legacy["count"] == 1
        migrated=sync_fts(db)
        assert migrated["migrated"] and migrated["count"] == 1
        assert sync_fts(db)["status"] == "UNCHANGED_CACHE_REUSED"


def test_paged_navigation_and_exact_source_filter(tmp_path):
    with ArchiveCatalog(tmp_path / "cat.sqlite") as db:
        for i in range(7):
            db.add([chat(str(i),"Forest " + str(i),"user" if i % 2 else "assistant",
                         "Dark Techno",100 + i)],"sha", "a.zip" if i % 2 else "b.zip")
        page=browse_conversations(db,title="Forest",limit=3)
        nextpage=browse_conversations(db,title="Forest",limit=3,offset=3)
        assert len(page)==3 and len(nextpage)==3
        assert not {x["conversation_id"] for x in page} & {x["conversation_id"] for x in nextpage}
        assert len(browse_conversations(db,source="a.zip"))==3
        assert len(search_filtered(db,"Dark",role="user",source="a.zip"))==3
        assert len(search_filtered(db,"",start_time=103,end_time=105))==3
        assert search_filtered(db,"Not present")==[]


def test_invalid_paging_filters_fail_closed(tmp_path):
    with ArchiveCatalog(tmp_path / "cat.db") as db:
        with pytest.raises(ArchiveImportError):browse_conversations(db,offset=-1)
        with pytest.raises(ArchiveImportError):search_filtered(db,"",limit=9999)
        with pytest.raises(ArchiveImportError):search_filtered(db,"x",start_time=5,end_time=4)


def test_source_integrity_unchanged_changed_missing(tmp_path):
    src=tmp_path / "zip";src.mkdir()
    file=src / "backup.zip"
    file.write_bytes(b"sample-source")
    checksum=hashlib.sha256(file.read_bytes()).hexdigest()
    cp=tmp_path / "checkpoint.json"
    cp.write_text(json.dumps({"schema":"666.chatbackup.batch-checkpoint.v1",
                             "completed":{"backup.zip":checksum}}),encoding="utf-8")
    assert audit_sources(src,cp)["status"]=="VERIFIED"
    file.write_bytes(b"new-archive-content")
    report=audit_sources(src,cp)
    assert report["status"]=="PARTIAL" and report["sources"][0]["status"]=="CHANGED"
    file.unlink()
    assert audit_sources(src,cp)["sources"][0]["status"]=="MISSING"


def test_source_integrity_rejects_escape(tmp_path):
    src=tmp_path / "zip";src.mkdir()
    cp=tmp_path / "checkpoint.json"
    cp.write_text(json.dumps({"schema":"666.chatbackup.batch-checkpoint.v1",
                             "completed":{"../another.zip":"0"*64}}),encoding="utf-8")
    with pytest.raises(ArchiveImportError):audit_sources(src,cp)


def test_originals_stay_unchanged(tmp_path):
    src=tmp_path / "zip";src.mkdir()
    file=src/"a.zip";file.write_bytes(b"untouched")
    before=file.read_bytes()
    cp=tmp_path/"checkpoint.json"
    cp.write_text(json.dumps({"schema":"666.chatbackup.batch-checkpoint.v1",
                             "completed":{"a.zip":hashlib.sha256(before).hexdigest()}}))
    audit_sources(src,cp)
    assert file.read_bytes()==before
