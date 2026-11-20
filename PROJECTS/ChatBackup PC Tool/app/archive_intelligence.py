"""Optional, offline ChatGPT account export adapter and local derived catalog for ChatBackup R5.
Existing share, manual, browser and Scriptable paths are not modified.
"""
from __future__ import annotations
import hashlib
import json
import re
import sqlite3
import zipfile
from dataclasses import dataclass, field
from datetime import datetime,timezone
from pathlib import Path, PurePosixPath
from typing import Any

MAX_MEMBER_BYTES=160*1024*1024
MAX_EXPANDED_BYTES=512*1024*1024
MAX_MEMBERS=50000
MAX_RATIO=200
MAX_CONVERSATIONS=150000
MAX_MAPPING_NODES=250000

class ArchiveImportError(ValueError):
    """Fail-closed and user-displayable import error."""

@dataclass
class ArchiveMessage:
    identity:str
    role:str
    text:str
    parent_id:str|None=None
    created_at:float|None=None
    attachments:list[dict[str,Any]]=field(default_factory=list)
    metadata:dict[str,Any]=field(default_factory=dict)

@dataclass
class ArchiveConversation:
    identity:str
    title:str
    messages:list[ArchiveMessage]
    source_file:str
    updated_at:float|None=None
    mapping_nodes:int=0
    warnings:list[str]=field(default_factory=list)

def sha256(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def file_sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        while chunk:=f.read(1024*1024):
            h.update(chunk)
    return h.hexdigest()

def timestamp(value:Any)->float|None:
    if isinstance(value,(int,float)) and not isinstance(value,bool):
        value=float(value)
        if value==value and abs(value)<1e15:return value
    return None

def _parts(content:Any)->tuple[str,list[dict[str,Any]]]:
    if not isinstance(content,dict):return '',[]
    source=content.get('parts',[])
    if not isinstance(source,list):return '',[]
    texts,assets=[],[]
    for part in source:
        if isinstance(part,str):texts.append(part)
        elif isinstance(part,dict):
            if isinstance(part.get('text'),str):texts.append(part['text'])
            kind=str(part.get('content_type') or part.get('type') or '')
            if kind in {'image_asset_pointer','file','audio','video'}:
                assets.append({'kind':kind,'pointer':str(part.get('asset_pointer') or part.get('url') or '')[:2000],
                               'name':str(part.get('name') or part.get('filename') or '')[:260],
                               'available_bytes':False})
    return '\n'.join(texts),assets

def parse_conversation(data:dict[str,Any],source_file:str='conversations.json')->ArchiveConversation:
    if not isinstance(data,dict):raise ArchiveImportError('Conversation is not an object')
    cid=str(data.get('id') or data.get('conversation_id') or '').strip()
    mapping=data.get('mapping')
    if not cid or len(cid)>500 or not isinstance(mapping,dict):
        raise ArchiveImportError('Missing identity or mapping')
    if len(mapping)>MAX_MAPPING_NODES:raise ArchiveImportError('Mapping too large')
    messages=[];warnings=[]
    for node_id,node in mapping.items():
        if not isinstance(node,dict):
            warnings.append('MALFORMED_NODE_SKIPPED');continue
        msg=node.get('message')
        if not isinstance(msg,dict):continue
        author=msg.get('author')
        role=str(author.get('role') or 'unknown')[:80] if isinstance(author,dict) else 'unknown'
        content=msg.get('content')
        text,assets=_parts(content)
        if not text and not assets:continue
        children=node.get('children')
        messages.append(ArchiveMessage(
            identity=str(msg.get('id') or node_id)[:500],role=role,text=text,
            parent_id=str(node['parent'])[:500] if node.get('parent') is not None else None,
            created_at=timestamp(msg.get('create_time')),attachments=assets,
            metadata={'content_type':str(content.get('content_type') or '')[:100] if isinstance(content,dict) else '',
                      'mapping_node_id':str(node_id)[:500],
                      'children_count':len(children) if isinstance(children,list) else 0}))
    if not messages:warnings.append('NO_RENDERABLE_MESSAGES')
    return ArchiveConversation(cid,str(data.get('title') or 'Untitled conversation')[:1000],
                               messages,source_file,timestamp(data.get('update_time')),len(mapping),list(dict.fromkeys(warnings)))

def _validate_zip(zf:zipfile.ZipFile)->list[zipfile.ZipInfo]:
    infos=zf.infolist()
    if len(infos)>MAX_MEMBERS:raise ArchiveImportError('Too many ZIP entries')
    seen=set();size=0
    for info in infos:
        name=info.filename
        p=PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts or '\\' in name or '\x00' in name or re.match(r'^[A-Za-z]:',name):
            raise ArchiveImportError('Unsafe archive member')
        if (info.external_attr>>16)&0o170000==0o120000:raise ArchiveImportError('ZIP symlinks forbidden')
        if info.flag_bits&1:raise ArchiveImportError('Encrypted ZIP forbidden')
        if info.file_size<0 or info.file_size>MAX_MEMBER_BYTES:raise ArchiveImportError('ZIP member oversized')
        if info.compress_size==0 and info.file_size:raise ArchiveImportError('Invalid compressed size')
        if info.compress_size and info.file_size>1024*1024 and info.file_size>info.compress_size*MAX_RATIO:
            raise ArchiveImportError('Possible decompression bomb')
        key=name.casefold()
        if key in seen:raise ArchiveImportError('Duplicate ZIP path')
        seen.add(key);size+=info.file_size
        if size>MAX_EXPANDED_BYTES:raise ArchiveImportError('Archive expanded size limit exceeded')
    return infos

def inspect_export(source:str|Path)->dict[str,Any]:
    path=Path(source)
    if not path.is_file() or not zipfile.is_zipfile(path):raise ArchiveImportError('Not a ZIP file')
    with zipfile.ZipFile(path) as zf:
        infos=_validate_zip(zf)
        found=[x.filename for x in infos if PurePosixPath(x.filename).name=='conversations.json']
        return {'schema':'666.chatbackup.export-inspection.v1','file':path.name,'sha256':file_sha256(path),
                'members':len(infos),'expanded_bytes':sum(x.file_size for x in infos),
                'candidates':found,'status':'SUPPORTED_JSON' if len(found)==1 else 'UNSUPPORTED_OR_AMBIGUOUS'}

def load_export(source:str|Path)->tuple[list[ArchiveConversation],dict[str,Any]]:
    report=inspect_export(source)
    if report['status']!='SUPPORTED_JSON':
        raise ArchiveImportError('Exactly one conversations.json required; HTML-only export not parsed')
    with zipfile.ZipFile(source) as zf:
        with zf.open(report['candidates'][0]) as handle:
            raw=handle.read(MAX_MEMBER_BYTES+1)
        if len(raw)>MAX_MEMBER_BYTES:raise ArchiveImportError('JSON limit exceeded')
        try:value=json.loads(raw.decode('utf-8-sig'))
        except (UnicodeError,json.JSONDecodeError,RecursionError) as exc:
            raise ArchiveImportError('Invalid conversations.json') from exc
    if not isinstance(value,list) or len(value)>MAX_CONVERSATIONS:
        raise ArchiveImportError('Expected bounded conversations array')
    conversations=[];rejected=[];seen=set()
    for i,data in enumerate(value):
        try:
            chat=parse_conversation(data,report['candidates'][0])
            if chat.identity in seen:raise ArchiveImportError('Duplicate conversation ID')
            seen.add(chat.identity);conversations.append(chat)
        except ArchiveImportError as exc:
            rejected.append({'index':i,'error':str(exc)})
    report.update({'seen':len(value),'accepted':len(conversations),'rejected':len(rejected),
                   'errors':rejected[:200],'status':'PARTIAL' if rejected else 'PASS'})
    return conversations,report

def completeness(chat:ArchiveConversation)->dict[str,Any]:
    assets=[a for m in chat.messages for a in m.attachments]
    missing=sum(not a['available_bytes'] for a in assets)
    warnings=list(chat.warnings)
    if missing:warnings.append('ASSET_BYTES_UNAVAILABLE')
    return {'conversation_id':chat.identity,'mapping_nodes':chat.mapping_nodes,
            'messages':len(chat.messages),'asset_references':len(assets),
            'asset_bytes_missing':missing,'visual_parity':'NOT_CLAIMED',
            'status':'PARTIAL' if warnings else 'STRUCTURED_SOURCE_UI_UNVERIFIED',
            'warnings':warnings}

def revision_hash(chat:ArchiveConversation)->str:
    data={'id':chat.identity,'title':chat.title,
          'messages':[{'id':m.identity,'role':m.role,'text':m.text,'parent':m.parent_id,
                       'attachments':m.attachments,'metadata':m.metadata} for m in chat.messages]}
    return sha256(json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8'))

class ArchiveCatalog:
    """Local SQLite cache; original ZIP remains canonical and never gets modified."""
    def __init__(self,path:str|Path):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
        self.db=sqlite3.connect(str(self.path))
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.execute('PRAGMA busy_timeout=10000')
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS conversations(
            conversation_id TEXT PRIMARY KEY,title TEXT NOT NULL,revision_hash TEXT NOT NULL,
            source_hash TEXT NOT NULL,filename TEXT NOT NULL,modified_at REAL,
            message_count INTEGER NOT NULL,integrity TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS messages(
            conversation_id TEXT NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
            message_id TEXT NOT NULL,role TEXT NOT NULL,text TEXT NOT NULL,
            parent_id TEXT,created_at REAL,PRIMARY KEY(conversation_id,message_id));
        CREATE TABLE IF NOT EXISTS revisions(
            conversation_id TEXT NOT NULL,revision_hash TEXT NOT NULL,
            observed_at TEXT NOT NULL,source_hash TEXT NOT NULL,
            PRIMARY KEY(conversation_id,revision_hash));""")
        self.db.commit()
    def __enter__(self):return self
    def __exit__(self,*args):self.db.close()
    def add(self,chats:list[ArchiveConversation],source_hash:str,source_name:str)->dict[str,int]:
        result={'new':0,'updated':0,'unchanged':0}
        for chat in chats:
            rev=revision_hash(chat)
            existing=self.db.execute('SELECT revision_hash FROM conversations WHERE conversation_id=?',(chat.identity,)).fetchone()
            if existing and existing[0]==rev:
                result['unchanged']+=1;continue
            with self.db:
                self.db.execute('DELETE FROM conversations WHERE conversation_id=?',(chat.identity,))
                self.db.execute('INSERT INTO conversations VALUES(?,?,?,?,?,?,?,?)',
                    (chat.identity,chat.title,rev,source_hash,source_name,chat.updated_at,len(chat.messages),completeness(chat)['status']))
                for message in chat.messages:
                    self.db.execute('INSERT OR IGNORE INTO messages VALUES(?,?,?,?,?,?)',
                        (chat.identity,message.identity,message.role,message.text,message.parent_id,message.created_at))
                self.db.execute('INSERT OR IGNORE INTO revisions VALUES(?,?,?,?)',
                    (chat.identity,rev,datetime.now(timezone.utc).isoformat(),source_hash))
            result['new' if not existing else 'updated']+=1
        return result
    def status(self):
        return {name:self.db.execute('SELECT COUNT(*) FROM '+table).fetchone()[0]
                for name,table in [('conversations','conversations'),('messages','messages'),('revisions','revisions')]}
    def search(self,term:str,limit:int=100)->list[dict[str,str]]:
        if not term.strip():return []
        term='%'+term.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')+'%'
        rows=self.db.execute("""SELECT m.conversation_id,c.title,m.message_id,m.role,substr(m.text,1,500)
            FROM messages m JOIN conversations c ON c.conversation_id=m.conversation_id
            WHERE m.text LIKE ? ESCAPE '\\' OR c.title LIKE ? ESCAPE '\\'
            ORDER BY c.modified_at DESC,m.message_id LIMIT ?""",(term,term,max(1,min(500,limit)))).fetchall()
        return [dict(zip(('conversation_id','title','message_id','role','snippet'),row)) for row in rows]
