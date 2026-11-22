"""Single-request Python bridge: SQLite authority, incremental JSON indexes and safe import."""
from __future__ import annotations
import sys,os,json,sqlite3,hashlib,re,zipfile,io,datetime,collections,pathlib,mimetypes,shutil,tempfile,stat
from pathlib import Path
MAX_FILE=25*1024*1024
MAX_ZIP_TOTAL=150*1024*1024
MAX_ZIP_ENTRIES=2000
MAX_IMPORT_RECORD_BYTES=200*1024*1024
MAX_INPUT_FILES=200
MAX_ARCHIVE_IDS=10000
ALLOWED_TEXT={'.txt','.md','.markdown','.json','.jsonl','.csv','.log','.py','.js','.ts','.jsx','.tsx','.html','.css','.xml','.yml','.yaml','.toml','.ini','.cfg','.bat','.cmd','.ps1','.sh','.sql','.java','.c','.cpp','.h','.php','.rtf'}
KNOWN_BINARY={'.pdf','.docx','.pages'}
PROJECT_PATTERNS=[('LYVRA',r'\blyvra\b|\bl\.y\.v\.r\.a\b'),('666CLIC',r'\b666clic\b|\bclicpro\b'),('666TDH',r'\b666tdh\b|trackdesignhub'),('666PFS',r'\b666pfs\b'),('666CLS',r'\b666cls\b'),('666MAIN_BRAIN',r'\b666main.brain\b|\bpsyllo\b'),('666SOUNDsDESIGn',r'666soundsdesign|webradio|radiobot'),('FULL_LYRICS_TOOL',r'full.lyrics.tool|lyrics.library')]
SECTION_RE=re.compile(r'(?im)^\s*(?:#{1,4}\s*)?(?:title|song title|track title|lyrics|song lyrics|style prompt|style|extended|framework|prompt)\s*[:：\-–]\s*')
TITLE_RE=re.compile(r'(?im)^\s*(?:#{1,3}\s*)?(?:title|song title|track title)\s*[:：\-–]\s*(.+)$')
CODE_RE=re.compile(r'(?m)^\s*(?:```(?:python|javascript|js|typescript|html|css|json|bash|sql)|(?:def |class |function |const |import |from |SELECT |CREATE TABLE ))')
DATE=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def h(s):return hashlib.sha256(s.encode('utf-8')).hexdigest()
def safe_name(s):return re.sub('[^a-zA-Z0-9_.-]+','_',s)[:90].strip('._') or 'untitled'
def dbconnect(base):
 base.mkdir(parents=True,exist_ok=True)
 c=sqlite3.connect(str(base/'catalog.sqlite'),timeout=30)
 c.row_factory=sqlite3.Row
 c.execute('PRAGMA journal_mode=WAL')
 c.executescript('''CREATE TABLE IF NOT EXISTS records(id TEXT PRIMARY KEY, project TEXT NOT NULL, category TEXT NOT NULL,title TEXT NOT NULL, content TEXT NOT NULL, source_name TEXT, source_hash TEXT, confidence REAL, topics TEXT, created_at TEXT, archived INTEGER NOT NULL DEFAULT 0);CREATE INDEX IF NOT EXISTS ix_records_project ON records(project,category,archived);CREATE INDEX IF NOT EXISTS ix_records_source ON records(source_hash);CREATE TABLE IF NOT EXISTS imports(id INTEGER PRIMARY KEY AUTOINCREMENT, source_name TEXT,source_hash TEXT, status TEXT, inserted INTEGER,skipped INTEGER,notes TEXT,created_at TEXT);CREATE TABLE IF NOT EXISTS projects(name TEXT PRIMARY KEY,created_at TEXT);''')
 try:c.execute('CREATE VIRTUAL TABLE IF NOT EXISTS records_fts USING fts5(id UNINDEXED,title,content,project,category)')
 except sqlite3.OperationalError:pass
 c.commit();return c
def categorize(text,title=''):
 t=(title+'\n'+text[:9000]).lower(); line_count=len(text.splitlines());
 if ('```' in text and CODE_RE.search(text)) or (len(CODE_RE.findall(text))>=3):return 'code',.9
 if re.search(r'\bframework\b|architecture|systemstart|livecircle|re-hydration|rehydration|system_id',t):return 'framework',.83
 if re.search(r'(?im)^\s*(?:#{1,3}\s*)?(?:style\s*prompt|style)\s*[:：\-]|\bstyle\s*prompt\b|\b(?:bpm|psytrance|techno)\b.{0,110}\b(?:bass|drums|mastering|sound)\b',t):return 'style_prompt',.81
 if re.search(r'\b(prompt|instruction|system prompt|user prompt)\b',t) and line_count<90:return 'prompt',.72
 if re.search(r'(?im)^\s*\[?(?:verse|chorus|bridge|outro|intro|hook|drop|pre-chorus)(?:\s*\d+)?\]?\s*[:\-]?\s*$',text) or re.search(r'(?im)^\s*(?:lyrics|song lyrics)\s*[:\-]',text):return 'lyrics',.82
 return 'diverse',.45
def project_for(text,source=''):
 scores=[];scope=(source+'\n'+text[:12000]).lower()
 for p,pattern in PROJECT_PATTERNS:
  n=len(re.findall(pattern,scope,re.I));n+=3 if re.search(pattern,source,re.I) else 0
  if n:scores.append((n,p))
 scores.sort(reverse=True)
 return (scores[0][1] if scores else 'UNASSIGNED'),[p for _,p in scores[:5]]
def topics_for(text):
 mapping={'music':r'lyrics|suno|music|track|psytrance|techno','software':r'github|python|electron|javascript|code|commit','radio':r'web.?radio|shoutcast|stream|dj','prompts':r'prompt|framework|instruction','archive':r'backup|archive|recovery|json|index','discord':r'discord|bot|webhook'}
 return [name for name,r in mapping.items() if re.search(r,text[:15000],re.I)]
def split_text(text,source):
 # Structural boundaries only; long unrelated sections are never cut at arbitrary character sizes.
 # For chat backups, messages are handled individually by read_sources.
 title_matches=list(TITLE_RE.finditer(text))
 if len(title_matches)>=2:
  chunks=[]
  if text[:title_matches[0].start()].strip():chunks.append(('Preamble',text[:title_matches[0].start()]))
  for i,m in enumerate(title_matches):
   end=title_matches[i+1].start() if i+1<len(title_matches) else len(text)
   segment=text[m.start():end].strip()
   if segment:chunks.append((m.group(1).strip()[:120],segment))
  return chunks
 # Markdown fenced song blocks / record separators
 blocks=re.split(r'(?m)^\s*(?:---\s*SONG\s*---|===\s*(?:SONG|LYRICS)\s*===)\s*$',text)
 if len(blocks)>1:return [(f'{Path(source).stem} #{i+1}',t.strip()) for i,t in enumerate(blocks) if t.strip()]
 return [(Path(source).stem or 'Untitled',text.strip())]
def json_nodes(v,root='backup'):
 # ChatGPT exports: mapping->message->content.parts OR conversations messages
 if isinstance(v,dict):
  if isinstance(v.get('mapping'),dict):
   for node in v['mapping'].values():
    msg=node.get('message') if isinstance(node,dict) else None
    if not isinstance(msg,dict):continue
    cont=msg.get('content') or {};parts=cont.get('parts') or []
    parts=[p for p in parts if isinstance(p,str)]
    if parts:
     role=(msg.get('author') or {}).get('role','message')
     yield (f'{root} · {role}', '\n\n'.join(parts))
   return
  if isinstance(v.get('messages'),list):
   for i,msg in enumerate(v['messages']):
    if isinstance(msg,dict):
     val=msg.get('content',msg.get('text',''))
     if isinstance(val,str) and val.strip():yield(f'{root} #{i+1}',val)
   return
  for key,val in v.items():
   if key in ('title','content','lyrics','style_prompt','prompt','text') and isinstance(val,str) and len(val.strip())>30:yield(f'{root} · {key}',val)
   elif isinstance(val,(dict,list)):yield from json_nodes(val,root)
 elif isinstance(v,list):
  for i,val in enumerate(v):yield from json_nodes(val,root+f' #{i+1}')
def extract_bytes(name,raw):
 suffix=Path(name).suffix.lower()
 if len(raw)>MAX_FILE:raise ValueError('Datei überschreitet 25 MiB')
 if suffix in ALLOWED_TEXT:
  text=raw.decode('utf-8-sig',errors='replace')
  if suffix in ('.json','.jsonl'):
   try:
    if suffix=='.jsonl':obj=[json.loads(line) for line in text.splitlines() if line.strip()]
    else:obj=json.loads(text)
    extracted=list(json_nodes(obj,Path(name).stem))
    if extracted:return extracted
   except (json.JSONDecodeError,ValueError):pass
  return [(Path(name).stem,text)]
 if suffix=='.pdf':
  try:from pypdf import PdfReader
  except ImportError:raise ValueError('PDF: optionale Abhängigkeit pypdf fehlt')
  reader=PdfReader(io.BytesIO(raw));return [(Path(name).stem,'\n\n'.join(p.extract_text() or '' for p in reader.pages))]
 if suffix=='.docx':
  try:from docx import Document
  except ImportError:raise ValueError('DOCX: optionale Abhängigkeit python-docx fehlt')
  d=Document(io.BytesIO(raw));return [(Path(name).stem,'\n'.join(p.text for p in d.paragraphs))]
 raise ValueError('Dateiformat nicht textuell extrahierbar (als Metadaten katalogisiert)')
def read_source(path):
 if not path.is_file():raise ValueError('Keine reguläre Datei')
 if path.stat().st_size>MAX_ZIP_TOTAL:raise ValueError('Quelldatei größer als 150 MiB')
 if path.suffix.lower()!='.zip':
  b=path.read_bytes()
  try:return extract_bytes(path.name,b),[]
  except ValueError as exc:return [],[str(exc)]
 items=[];warnings=[];total=0
 with zipfile.ZipFile(path) as z:
  files=[m for m in z.infolist() if not m.is_dir()]
  if len(files)>MAX_ZIP_ENTRIES:raise ValueError('Mehr als 2.000 ZIP-Einträge')
  for m in files:
   name=m.filename.replace('\\','/')
   if name.startswith('/') or re.match(r'^[a-zA-Z]:',name) or '..' in Path(name).parts or stat.S_IFMT(m.external_attr >> 16)==stat.S_IFLNK:
    warnings.append('Unsicherer ZIP-Pfad/Link verworfen');continue
   if m.file_size>MAX_FILE or (m.compress_size>0 and m.file_size/m.compress_size>250):warnings.append('ZIP-Limit: '+name[:100]);continue
   total+=m.file_size
   if total>MAX_ZIP_TOTAL:raise ValueError('ZIP entpackt mehr als 150 MiB')
   try:
    with z.open(m) as src:
     raw=src.read(MAX_FILE+1)
    if len(raw)>MAX_FILE:raise ValueError('Entpackung überschreitet 25 MiB')
    contents=extract_bytes(name,raw)
    items.extend((name,title,body) for title,body in contents)
   except (ValueError,RuntimeError) as exc:warnings.append(name[:100]+': '+str(exc)[:140])
 return items,warnings
def insert(conn,project,category,title,content,source,source_hash,score,topics):
 rid=h(project+'\x00'+category+'\x00'+content)
 if conn.execute('SELECT 1 FROM records WHERE id=?',(rid,)).fetchone():return False,rid
 conn.execute('INSERT OR IGNORE INTO projects VALUES(?,?)',(project,DATE()))
 conn.execute('INSERT INTO records VALUES(?,?,?,?,?,?,?,?,?,?,0)',(rid,project,category,title[:240],content,source,source_hash,score,json.dumps(topics),DATE()))
 try:conn.execute('INSERT INTO records_fts VALUES(?,?,?,?,?)',(rid,title,content,project,category))
 except sqlite3.OperationalError:pass
 return True,rid
def materialize_records(conn,base,ids):
 # Incremental one-record-per-JSON output. Reimports don't rewrite old payloads.
 for rid in ids:
  row=conn.execute('SELECT * FROM records WHERE id=?',(rid,)).fetchone()
  if row:
   p=base/'records'/safe_name(row['project'])/(rid+'.json')
   atomic_json(p,{'schema':'666-catalog-record/1',**dict(row)})
def snapshot(conn,base):
 # Export derived, machine-readable views; SQLite is canonical for query.
 out=base/'index';out.mkdir(exist_ok=True)
 c=conn.execute('SELECT project,category,count(*) n FROM records WHERE archived=0 GROUP BY project,category').fetchall()
 counts={}
 for r in c:counts.setdefault(r['project'],{})[r['category']]=r['n']
 for proj,cats in counts.items():
  d=out/safe_name(proj);d.mkdir(exist_ok=True)
  rows=conn.execute('SELECT id,category,title,source_name,confidence,topics,created_at FROM records WHERE project=? AND archived=0 ORDER BY created_at DESC',(proj,)).fetchall()
  payload={'schema':'666-catalog-index/1','project':proj,'counts':cats,'record_count':len(rows),'records':[dict(r) for r in rows]}
  atomic_json(d/'index.json',payload)
  topic_counts=collections.Counter(t for r in rows for t in json.loads(r['topics'] or '[]'))
  atomic_json(d/'project_report.json',{'schema':'666-project-analysis/1','project':proj,'entry_count':len(rows),'categories':cats,'top_topics':dict(topic_counts.most_common(12)),'source_count':len({r['source_name'] for r in rows}),'potential_comparison':{'target':'native project current (independently verify)','status':'READBACK_REQUIRED','review_checks':['Source revision and exact provenance','Feature parity and contradictions','Code fragments against native contracts','Security and dependency impact'],'automation_policy':'NO_AUTO_PROMOTION'}})
 atomic_json(out/'index.json',{'schema':'666-catalog-root/1','generated_at':DATE(),'projects':counts,'total':sum(sum(x.values()) for x in counts.values())})
def atomic_json(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(path)
def stats(c):
 projects=[dict(r) for r in c.execute('SELECT project,category,count(*) count FROM records WHERE archived=0 GROUP BY project,category ORDER BY count DESC')]
 return {'total':c.execute('SELECT count(*) FROM records WHERE archived=0').fetchone()[0], 'archived':c.execute('SELECT count(*) FROM records WHERE archived=1').fetchone()[0], 'projects':projects,'import_total':c.execute('SELECT count(*) FROM imports').fetchone()[0], 'imports':[dict(r) for r in c.execute('SELECT * FROM imports ORDER BY id DESC LIMIT 12')]}
def importer(c,base,data):
 files=data.get('paths',[])
 if not isinstance(files,list) or len(files)>MAX_INPUT_FILES:raise ValueError('Maximal 200 Dateien pro Import')
 result={'inserted':0,'skipped':0,'sources':[],'warnings':[]}
 for filename in files:
  path=Path(filename)
  source_hash=''
  try:
   if not path.is_file():raise ValueError('Keine reguläre Quelldatei')
   if path.stat().st_size>MAX_ZIP_TOTAL:raise ValueError('Quelldatei größer als 150 MiB')
   digest=hashlib.sha256()
   with path.open('rb') as stream:
    for chunk in iter(lambda:stream.read(1024*1024),b''):digest.update(chunk)
   source_hash=digest.hexdigest()
   blocks,warnings=read_source(path);
   if sum(len(body.encode('utf-8')) for item in blocks for body in [item[-1]])>MAX_IMPORT_RECORD_BYTES:raise ValueError('Extrahierte Inhalte überschreiten 200 MiB')
   result['warnings'].extend(warnings[:100]);new=0;skip=0;new_ids=[]result['warnings'].extend(warnings[:100]);new=0;skip=0;new_ids=[]
   with c:
    for item in blocks:
     if len(item)==3:src,title,body=item;src=f'{path.name}/{src}'
     else:title,body=item;src=path.name
     for label,seg in split_text(body,src):
      if len(seg.strip())<10:continue
      proj,_=project_for(seg,src);cat,confidence=categorize(seg,label)
      added,rid=insert(c,proj,cat,label if title==Path(src).stem else f'{title} · {label}',seg,src,source_hash,confidence,topics_for(seg));new+=int(added);skip+=int(not added)
      if added:new_ids.append(rid)
    c.execute('INSERT INTO imports(source_name,source_hash,status,inserted,skipped,notes,created_at) VALUES(?,?,?,?,?,?,?)',(path.name,source_hash,'done' if blocks else 'unextracted',new,skip,'; '.join(warnings)[:1000],DATE()))
   materialize_records(c,base,new_ids)
   result['inserted']+=new;result['skipped']+=skip;result['sources'].append({'name':path.name,'inserted':new,'skipped':skip,'status':'done' if blocks else 'unextracted'})
  except Exception as exc:
   with c:c.execute('INSERT INTO imports(source_name,source_hash,status,inserted,skipped,notes,created_at) VALUES(?,?,?,?,?,?,?)',(path.name,source_hash,'error',0,0,str(exc)[:1000],DATE()))
   result['sources'].append({'name':path.name,'status':'error','detail':str(exc)})
 snapshot(c,base)
 return result
def export_records(c,base,data):
 ids=data.get('ids',[]);project=data.get('project');fmt=data.get('format','json')
 if fmt not in ('json','md','txt','zip'):raise ValueError('Ungültiges Exportformat')
 if ids:
  if len(ids)>10000:raise ValueError('Zu viele IDs')
  rows=c.execute('SELECT * FROM records WHERE id IN ('+','.join('?'*len(ids))+')',ids).fetchall()
 elif project:rows=c.execute('SELECT * FROM records WHERE project=? AND archived=0',(project,)).fetchall()
 else:rows=c.execute('SELECT * FROM records WHERE archived=0').fetchall()
 out=base/'exports';out.mkdir(exist_ok=True)
 stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f');stem='export_'+stamp
 entries=[dict(r) for r in rows]
 if fmt=='json':p=out/(stem+'.json');atomic_json(p,{'schema':'666-catalog-export/1','records':entries})
 elif fmt in ('md','txt'):
  p=out/(stem+'.'+fmt);p.write_text('\n\n---\n\n'.join(f'# {r["title"]}\nProject: {r["project"]} | {r["category"]}\n\n{r["content"]}' for r in entries),encoding='utf-8')
 else:
  p=out/(stem+'.zip')
  with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
   for r in entries:z.writestr(f'{safe_name(r["project"])}/{r["id"]}.json',json.dumps(r,ensure_ascii=False,indent=2))
   z.writestr('index.json',json.dumps({'schema':'666-catalog-archive/1','records':[{'id':r['id'],'project':r['project'],'category':r['category']} for r in entries]},ensure_ascii=False,indent=2))
 return {'path':str(p),'count':len(entries)}
def archive(c,base,data):
 # Controlled archive of explicitly selected records, not silent removal.
 ids=data.get('ids',[])
 if not isinstance(ids,list) or not ids or len(ids)>MAX_ARCHIVE_IDS or any(not isinstance(x,str) for x in ids):raise ValueError('Keine gültige Datensatzauswahl')
 ids=list(dict.fromkeys(ids))
 matched={r[0] for r in c.execute('SELECT id FROM records WHERE id IN ('+','.join('?'*len(ids))+')',ids)}
 if matched!=set(ids):raise ValueError('Archiv enthält unbekannte IDs; keine Änderungen durchgeführt')
 result=export_records(c,base,{'ids':ids,'format':'zip'})
 dest=base/'old_archive';dest.mkdir(exist_ok=True)
 p=Path(result['path']); target=dest/p.name;shutil.move(str(p),str(target))
 with zipfile.ZipFile(target) as z:
  if z.testzip() is not None:raise ValueError('ZIP-Archivprüfung fehlgeschlagen')
 with c:c.executemany('UPDATE records SET archived=1 WHERE id=?',[(x,) for x in ids])
 snapshot(c,base)
 return {'path':str(target),'archived':result['count']}
def migrate(c,base,data):
 db=Path(data.get('path',''))
 if not db.is_file():raise ValueError('Legacy-Datenbank nicht gefunden')
 # Read-only URI is intentional. Legacy DB itself never gets written.
 old=sqlite3.connect('file:'+db.resolve().as_posix()+'?mode=ro',uri=True)
 try:
  rows=old.execute('SELECT title,content,source_file FROM lyrics').fetchall()
  new=0;skip=0;new_ids=[]
  with c:
   for title,body,source in rows:
    if not body or not body.strip():continue
    ok,rid=insert(c,'FULL_LYRICS_TOOL','lyrics',title,body,source or 'legacy-r02',h(body),1.0,['music']);new+=int(ok);skip+=int(not ok)
    if ok:new_ids.append(rid)
  materialize_records(c,base,new_ids);snapshot(c,base);return {'legacy_count':len(rows),'inserted':new,'duplicates':skip}
 finally:old.close()
def run(arg):
 action=arg['action'];data=arg.get('data',{});base=Path(arg['data_dir']);c=dbconnect(base)
 try:
  if action=='status':return stats(c)
  if action=='deps':
   import importlib.util
   return {x:importlib.util.find_spec(x) is not None for x in ('pypdf','docx')}
  if action=='import':return importer(c,base,data)
  if action=='list':
   project=data.get('project','');category=data.get('category','');term=data.get('search','');archived=int(bool(data.get('archived')))
   where=['archived=?'];args=[archived]
   if project:where.append('project=?');args.append(project)
   if category:where.append('category=?');args.append(category)
   if term:where.append('(title LIKE ? OR content LIKE ?)');args.extend(['%'+term[:120]+'%']*2)
   page=max(0,int(data.get('page',0)));args.extend([100,page*100])
   rows=c.execute('SELECT id,title,project,category,source_name,confidence,created_at,substr(content,1,190) excerpt FROM records WHERE '+' AND '.join(where)+' ORDER BY created_at DESC LIMIT ? OFFSET ?',args).fetchall()
   return [dict(r) for r in rows]
  if action=='record':
   row=c.execute('SELECT * FROM records WHERE id=?',(data.get('id'),)).fetchone();return dict(row) if row else None
  if action=='export':return export_records(c,base,data)
  if action=='archive':return archive(c,base,data)
  if action=='migrate':return migrate(c,base,data)
  if action=='projects':
   return [{'project':p,'topics':collections.Counter(t for r in c.execute('SELECT topics FROM records WHERE project=?',(p,)) for t in json.loads(r[0])).most_common(6),'recommendation':'Quellen/Hashes mit dem nativen Hauptsystem vergleichen; keine automatische Promotion.', 'records':c.execute('SELECT count(*) FROM records WHERE project=?',(p,)).fetchone()[0]} for (p,) in c.execute('SELECT name FROM projects ORDER BY name')]
  raise ValueError('Unbekannte Aktion')
 finally:c.close()
if __name__=='__main__':
 try:print(json.dumps({'ok':True,'result':run(json.loads(sys.stdin.read()))},ensure_ascii=False))
 except Exception as e:print(json.dumps({'ok':False,'error':str(e)},ensure_ascii=False))
