from __future__ import annotations
import json,sys,zipfile
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'app'))
from archive_intelligence import ArchiveCatalog,ArchiveImportError,load_export,inspect_export,completeness
from archive_research import iter_chunks,export_jsonl

def conversation(text='hello'):
    return {'id':'chat-1','title':'Music archive','update_time':1710000000,
      'mapping':{'a':{'parent':None,'children':['b','c'],'message':{'id':'m1','author':{'role':'user'},'content':{'content_type':'text','parts':[text]}}},
                 'b':{'parent':'a','children':[],'message':{'id':'m2','author':{'role':'assistant'},'content':{'content_type':'text','parts':['response']}}},
                 'c':{'parent':'a','children':[],'message':{'id':'m3','author':{'role':'assistant'},'content':{'content_type':'multimodal_text','parts':[{'content_type':'image_asset_pointer','asset_pointer':'asset://ptr'}]}}}}

def exported(path,entry='conversations.json',extra=None,contents=None):
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr(entry,json.dumps([conversation() if contents is None else contents]))
        for k,v in (extra or {}).items():z.writestr(k,v)

def test_preserves_branches_and_reports_missing_assets(tmp_path):
    path=tmp_path/'export.zip';exported(path)
    chats,report=load_export(path)
    assert report['status']=='PASS' and len(chats)==1
    assert len(chats[0].messages)==3
    assert [m.parent_id for m in chats[0].messages]==[None,'a','a']
    assert completeness(chats[0])['status']=='PARTIAL'
    assert completeness(chats[0])['asset_bytes_missing']==1

def test_catalog_dedup_update_and_search(tmp_path):
    path=tmp_path/'export.zip';exported(path)
    chats,report=load_export(path)
    with ArchiveCatalog(tmp_path/'index.sqlite3') as db:
        assert db.add(chats,report['sha256'],'export.zip')['new']==1
        assert db.add(chats,report['sha256'],'export.zip')['unchanged']==1
        assert db.status()=={'conversations':1,'messages':3,'revisions':1}
        assert len(db.search('hello'))==1
        chats[0].messages[0].text='updated'
        assert db.add(chats,report['sha256'],'export.zip')['updated']==1
        assert db.status()['revisions']==2
        assert db.search('hello')==[] and len(db.search('updated'))==1

def test_source_bytes_preserved(tmp_path):
    path=tmp_path/'e.zip';exported(path)
    before=path.read_bytes();load_export(path)
    assert path.read_bytes()==before

def test_zip_traversal_rejected(tmp_path):
    path=tmp_path/'bad.zip';exported(path,extra={'../secret':'fake'})
    with pytest.raises(ArchiveImportError):load_export(path)

def test_duplicate_entries_rejected(tmp_path):
    import warnings
    path=tmp_path/'duplicate.zip'
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',UserWarning)
        with zipfile.ZipFile(path,'w') as z:
            z.writestr('conversations.json','[]')
            z.writestr('conversations.json','[]')
    with pytest.raises(ArchiveImportError):load_export(path)

def test_html_only_fail_closed(tmp_path):
    path=tmp_path/'html.zip'
    with zipfile.ZipFile(path,'w') as z:z.writestr('chat.html','<html/>')
    assert inspect_export(path)['status']=='UNSUPPORTED_OR_AMBIGUOUS'
    with pytest.raises(ArchiveImportError):load_export(path)

def test_unknown_conversation_partial(tmp_path):
    path=tmp_path/'bad.zip';exported(path,contents={'title':'No ID','mapping':{}})
    chats,report=load_export(path)
    assert chats==[] and report['status']=='PARTIAL' and report['rejected']==1

def test_rag_offsets_and_no_overwrite(tmp_path):
    path=tmp_path/'export.zip';exported(path,contents=conversation('abc'*190))
    chats,_=load_export(path)
    chunks=list(iter_chunks(chats,max_chars=210))
    assert chunks
    for row in chunks:
        msg=next(m for m in chats[0].messages if m.identity==row['message_id'])
        assert msg.text[row['start_char']:row['end_char']]==row['text']
    dest=tmp_path/'rag.jsonl'
    assert export_jsonl(chats,dest,210)['status']=='READBACK_VERIFIED'
    with pytest.raises(FileExistsError):export_jsonl(chats,dest,210)

def test_like_escaping(tmp_path):
    path=tmp_path/'e.zip';exported(path,contents=conversation('a%b f_o'))
    chats,r=load_export(path)
    with ArchiveCatalog(tmp_path/'db.sqlite3') as db:
        db.add(chats,r['sha256'],'e.zip')
        assert len(db.search('a%b'))==1
        assert len(db.search('f_o'))==1
        assert len(db.search('not-found'))==0
