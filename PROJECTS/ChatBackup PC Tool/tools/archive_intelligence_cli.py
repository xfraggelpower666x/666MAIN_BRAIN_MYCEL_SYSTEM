#!/usr/bin/env python3
"""666 ChatBackup R5 offline archive importer/search CLI."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'app'))
from archive_intelligence import ArchiveCatalog,ArchiveImportError,inspect_export,load_export,completeness
from archive_research import export_jsonl
from archive_extensions import import_directory, rebuild_fts, search_fts, conversation_view

def main(argv=None):
    p=argparse.ArgumentParser(description='ChatBackup Archive Intelligence - offline, no ChatGPT login/API')
    p.add_argument('--db',type=Path,default=Path.home()/'.666chatbackup'/'catalog.sqlite3')
    commands=p.add_subparsers(dest='command',required=True)
    for name in ('inspect','import'):
        a=commands.add_parser(name);a.add_argument('archive',type=Path)
    a=commands.add_parser('search');a.add_argument('term')
    commands.add_parser('status')
    a=commands.add_parser('rag');a.add_argument('archive',type=Path);a.add_argument('output',type=Path)
    a.add_argument('--chunk-size',type=int,default=1800)
    a=commands.add_parser('batch');a.add_argument('folder',type=Path)
    a.add_argument('--checkpoint',type=Path,default=None)
    a.add_argument('--recursive',action='store_true')
    a=commands.add_parser('search-fast');a.add_argument('term')
    a=commands.add_parser('view');a.add_argument('conversation_id')
    x=p.parse_args(argv)
    try:
        if x.command=='inspect':
            result=inspect_export(x.archive)
        elif x.command=='import':
            chats,report=load_export(x.archive)
            with ArchiveCatalog(x.db) as catalog:
                result={'source':report,'catalog':catalog.add(chats,report['sha256'],x.archive.name),
                        'completeness':[completeness(c) for c in chats],'indexed':catalog.status()}
        elif x.command=='search':
            with ArchiveCatalog(x.db) as catalog:result=catalog.search(x.term)
        elif x.command=='status':
            with ArchiveCatalog(x.db) as catalog:result=catalog.status()
        elif x.command=='batch':
            checkpoint=x.checkpoint or x.db.with_name(x.db.name+'.batch-checkpoint.json')
            result=import_directory(x.folder,x.db,checkpoint,recursive=x.recursive)
        elif x.command=='search-fast':
            with ArchiveCatalog(x.db) as catalog:result=search_fts(catalog,x.term)
        elif x.command=='view':
            with ArchiveCatalog(x.db) as catalog:result=conversation_view(catalog,x.conversation_id)
        elif x.command=='rag':
            chats,report=load_export(x.archive)
            if report['status']!='PASS':raise ArchiveImportError('Partial source cannot be claimed as complete RAG export')
            result=export_jsonl(chats,x.output,max_chars=x.chunk_size)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0
    except (ArchiveImportError,OSError,ValueError) as exc:
        print('ARCHIVE_BLOCKED: '+str(exc),file=sys.stderr)
        return 2

if __name__=='__main__':raise SystemExit(main())
