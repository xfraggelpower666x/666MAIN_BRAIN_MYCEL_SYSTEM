"""Focused streaming, progress, cancellation and transaction rollback tests."""
from __future__ import annotations
import json
import sys
import zipfile
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'app'))
from archive_intelligence import ArchiveCatalog,ArchiveImportError
from archive_extensions import import_directory,conversation_view
from archive_streaming import iter_export_conversations,StreamingCancelled

def make_export(path, count=7, payload="synth signal"):
    conversations=[]
    for i in range(count):
        conversations.append({
            "id":f"chat-{i}", "title":f"Audio {i}",
            "mapping":{"a":{"parent":None,"children":[],
                        "message":{"id":f"msg-{i}","author":{"role":"user"},
                                   "content":{"content_type":"text","parts":[payload]}}}}
        })
    with zipfile.ZipFile(path,"w",compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("conversations.json",json.dumps(conversations,ensure_ascii=False))
    return conversations

def test_streaming_reads_without_whole_array(tmp_path):
    path=tmp_path/"large.zip"
    make_export(path,500,payload="Cyberpsy "+("abcde"*80))
    events=[]
    rows=list(iter_export_conversations(path,progress=events.append))
    assert len(rows)==500
    assert events and events[-1]['json_bytes']>0

def test_streaming_rejects_trailing_comma(tmp_path):
    path=tmp_path/"bad.zip"
    with zipfile.ZipFile(path,"w") as z:
        z.writestr("conversations.json",'[{"id":"first","mapping":{}},]')
    with pytest.raises(ArchiveImportError):list(iter_export_conversations(path))

def test_streaming_rejects_truncated_array(tmp_path):
    path=tmp_path/"bad.zip"
    with zipfile.ZipFile(path,"w") as z:
        z.writestr("conversations.json",'[{"id":"first","mapping":{}}')
    with pytest.raises(ArchiveImportError):list(iter_export_conversations(path))

def test_streaming_rollback_on_late_parse_failure(tmp_path):
    folder=tmp_path/"sources";folder.mkdir()
    path=folder/"broken.zip"
    a=make_export(path,1)[0]
    with zipfile.ZipFile(path,"w") as z:
        z.writestr("conversations.json",json.dumps([a,{"title":"missing id"}]))
    db=tmp_path/"db.sqlite";cp=tmp_path/"progress.json"
    result=import_directory(folder,db,cp)
    assert result["status"]=="PARTIAL" and result["imported"]==0
    with ArchiveCatalog(db) as c:
        assert c.status()["conversations"]==0
    assert not cp.exists()

def test_streaming_cancel_inside_zip_rolls_back(tmp_path):
    folder=tmp_path/"sources";folder.mkdir()
    make_export(folder/"many.zip",300,payload="x"*3000)
    db=tmp_path/"db.sqlite";cp=tmp_path/"progress.json"
    event_log=[]
    cancelled=[False]
    def progress(event):
        event_log.append(event)
        if event.get("stage")=="STREAMING":
            cancelled[0]=True
    result=import_directory(folder,db,cp,stop=lambda:cancelled[0],progress=progress)
    assert result["stopped"] and result["status"]=="PARTIAL"
    with ArchiveCatalog(db) as c:assert c.status()["conversations"]==0
    assert not cp.exists()
    assert event_log

def test_batch_resume_with_streamed_zip_and_progress(tmp_path):
    folder=tmp_path/"sources";folder.mkdir()
    make_export(folder/"a.zip",24)
    make_export(folder/"b.zip",25)
    db=tmp_path/"db.sqlite";cp=tmp_path/"cp.json";events=[]
    first=import_directory(folder,db,cp,progress=events.append)
    assert first["status"]=="PASS" and first["imported"]==2
    assert any(ev["stage"]=="STREAMING" for ev in events)
    assert events[-1]["stage"]=="FINISHED"
    with ArchiveCatalog(db) as catalog:
        assert catalog.status()["conversations"]==25 # same IDs across ZIPs, revisions dedup
        assert conversation_view(catalog,"chat-24") is not None
    second=import_directory(folder,db,cp)
    assert second["unchanged_files"]==2

def test_unicode_boundaries_and_nested_content(tmp_path):
    p=tmp_path/"unicode.zip"
    long="🎛️"*33000
    make_export(p,1,long)
    data=list(iter_export_conversations(p))
    assert data[0].messages[0].text==long
