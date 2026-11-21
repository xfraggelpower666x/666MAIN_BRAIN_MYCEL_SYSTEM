from __future__ import annotations
import json
import sys
import zipfile
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"app"))
from archive_intelligence import ArchiveCatalog, ArchiveImportError
from archive_extensions import import_directory, rebuild_fts, search_fts, conversation_view

def make_archive(target:Path, cid:str="one", text:str="dark techno"):
    payload=[{"id":cid,"title":"Audio Projects","update_time":1710000011,
              "mapping":{"a":{"parent":None,"children":[],"message":{
                "id":"msg-"+cid,"author":{"role":"user"},
                "create_time":1710000000,
                "content":{"content_type":"text","parts":[text]}}}}}]
    with zipfile.ZipFile(target,"w",compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("conversations.json",json.dumps(payload))

def test_batch_import_resume_source_untouched(tmp_path):
    folder=tmp_path/"exports";folder.mkdir()
    one=folder/"first.zip";two=folder/"second.zip"
    make_archive(one,"one");make_archive(two,"two",text="psytrance")
    before=one.read_bytes(),two.read_bytes()
    db=tmp_path/"catalog.sqlite";cp=tmp_path/"progress.json"
    completed=[]
    def progress(event):
        if event.get("stage")=="IMPORTED":
            completed.append(event["filename"])
    first=import_directory(folder,db,cp,stop=lambda:bool(completed),progress=progress)
    assert first["imported"]==1 and first["stopped"] and first["status"]=="PARTIAL"
    with ArchiveCatalog(db) as cat:assert cat.status()["conversations"]==1
    second=import_directory(folder,db,cp)
    assert second["imported"]==1 and second["unchanged_files"]==1
    assert second["status"]=="PASS"
    third=import_directory(folder,db,cp)
    assert third["imported"]==0 and third["unchanged_files"]==2
    assert (one.read_bytes(),two.read_bytes())==before
    with ArchiveCatalog(db) as cat: assert cat.status()["conversations"]==2

def test_modified_export_invalidates_checkpoint(tmp_path):
    folder=tmp_path/"a";folder.mkdir();p=folder/"x.zip"
    make_archive(p,"one")
    db=tmp_path/"idx.sqlite";cp=tmp_path/"c.json"
    import_directory(folder,db,cp)
    make_archive(p,"one","changed signal")
    report=import_directory(folder,db,cp)
    assert report["imported"]==1
    with ArchiveCatalog(db) as catalog:
        assert len(catalog.search("changed signal"))==1

def test_failed_zip_does_not_get_checkpoint(tmp_path):
    folder=tmp_path/"a";folder.mkdir()
    (folder/"bad.zip").write_bytes(b"invalid")
    r=import_directory(folder,tmp_path/"db.sqlite",tmp_path/"cp.json")
    assert r["status"]=="PARTIAL" and len(r["failed"])==1
    assert r["imported"]==0
    assert not (tmp_path/"cp.json").exists()

def test_fts_and_conversation_view(tmp_path):
    folder=tmp_path/"a";folder.mkdir()
    make_archive(folder/"test.zip","one","Deep Dark Techno spirals")
    db=tmp_path/"d.sqlite"
    import_directory(folder,db,tmp_path/"ckpt.json")
    with ArchiveCatalog(db) as c:
        status=rebuild_fts(c)
        if status["status"]=="FTS5_UNAVAILABLE":
            pytest.skip("SQLite built without FTS5")
        assert status["count"]==1
        matches=search_fts(c,"Dark Techno")
        assert len(matches)==1 and matches[0]["conversation_id"]=="one"
        assert search_fts(c,"non-existent")==[]
        assert search_fts(c,'Dark" OR "anything')==[]
        info=conversation_view(c,"one")
        assert info["source_file"]=="test.zip"
        assert info["messages"][0]["text"]=="Deep Dark Techno spirals"
        assert info["visual_parity"]=="NOT_CLAIMED"
        assert conversation_view(c,"not-here") is None

def test_rejects_checkpoint_as_database(tmp_path):
    folder=tmp_path/"a";folder.mkdir()
    with pytest.raises(ArchiveImportError):
        import_directory(folder,tmp_path/"same",tmp_path/"same")

def test_multi_source_checkpoint_dedup(tmp_path):
    folder=tmp_path/"a";folder.mkdir()
    make_archive(folder/"a.zip","same","first")
    make_archive(folder/"b.zip","same","second")
    db=tmp_path/"db.sqlite";cp=tmp_path/"ck.json"
    result=import_directory(folder,db,cp)
    assert result["imported"]==2
    with ArchiveCatalog(db) as c:
        view=conversation_view(c,"same")
        assert view["messages"][0]["text"]=="second"
        assert c.status()["revisions"]==2
