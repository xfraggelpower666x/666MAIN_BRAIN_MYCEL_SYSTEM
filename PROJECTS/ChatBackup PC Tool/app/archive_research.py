"""Opt-in RAG JSONL with verifiable source offsets. No LLM/API/network dependency."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from archive_intelligence import ArchiveConversation

def iter_chunks(chats:list[ArchiveConversation],max_chars:int=1800):
    if not 200<=max_chars<=20000:raise ValueError('max_chars outside 200..20000')
    for chat in chats:
        for message in chat.messages:
            text=message.text
            start=0;ordinal=0
            while start<len(text):
                end=min(len(text),start+max_chars)
                if end<len(text):
                    cut=text.rfind('\n',start+max_chars//2,end)
                    if cut>start:end=cut+1
                part=text[start:end]
                yield {'schema':'666.chatbackup.rag.v1','conversation_id':chat.identity,
                       'title':chat.title,'message_id':message.identity,'role':message.role,
                       'parent_id':message.parent_id,'chunk':ordinal,
                       'start_char':start,'end_char':end,'text':part,
                       'sha256':hashlib.sha256(part.encode('utf-8')).hexdigest(),
                       'source_file':chat.source_file,'visual_parity':'NOT_CLAIMED'}
                start=end;ordinal+=1

def export_jsonl(chats:list[ArchiveConversation],destination:str|Path,max_chars:int=1800):
    target=Path(destination)
    if target.exists():raise FileExistsError('Destination exists: '+str(target))
    target.parent.mkdir(parents=True,exist_ok=True)
    partial=target.with_name(target.name+'.partial')
    if partial.exists():raise FileExistsError('Unfinished export exists')
    count=0
    try:
        with partial.open('x',encoding='utf-8',newline='\n') as out:
            for row in iter_chunks(chats,max_chars):
                out.write(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n')
                count+=1
        digest=hashlib.sha256(partial.read_bytes()).hexdigest()
        partial.replace(target)
        if hashlib.sha256(target.read_bytes()).hexdigest()!=digest:
            raise IOError('RAG readback mismatch')
        return {'chunks':count,'sha256':digest,'path':str(target),'status':'READBACK_VERIFIED'}
    finally:
        if partial.exists():partial.unlink()
