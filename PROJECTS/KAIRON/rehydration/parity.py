"""Read-only candidate audit; never grants production release."""
import hashlib, json, re, sys
from pathlib import Path

def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def audit(root):
    root=Path(root).resolve()
    def read(name):
        p=(root/name).resolve()
        if not p.is_relative_to(root): raise ValueError('FOREIGN_PATH')
        return p.read_bytes()
    def load(name): return json.loads(read(name))
    raw=read('CURRENT_POINTER.json'); p=json.loads(raw)
    t=load('triggers/TRIGGER_REGISTRY.json'); c=load('livecircle/CURRENT_STATE.json'); a=load('identity/CHARACTER.json')
    if any(x.get('system_id')!='666TDI-001' for x in (p,t,c,a)): raise ValueError('FOREIGN_IDENTITY')
    if a.get('pronoun_de')!='er' or c.get('foreign_repo_write_allowed') is not False: raise ValueError('IDENTITY_SCOPE')
    commands=t['direct_chat_triggers']
    if not commands or len(commands)!=len(set(commands)) or any(not re.fullmatch(r'KAIRON [A-Z]+(?: [A-Z]+)*',x) for x in commands): raise ValueError('TRIGGER_REGISTRY')
    previous='GENESIS'
    for i,e in enumerate(c['events'],1):
        body=json.dumps({k:v for k,v in e.items() if k!='hash'},ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
        if e['seq']!=i or e['prev_hash']!=previous or e['hash']!=hashlib.sha256(body).hexdigest(): raise ValueError('LIVE_CIRCLE_CHAIN')
        previous=e['hash']
    if c['revision']!=len(c['events']): raise ValueError('LIVE_CIRCLE_REVISION')
    keys=sorted((k for k in p if re.fullmatch(r'native_musical_intelligence_r\d+',k)),key=lambda k:int(k.rsplit('r',1)[1]))
    if not keys or [int(k.rsplit('r',1)[1]) for k in keys]!=list(range(1,len(keys)+1)): raise ValueError('NMI_SEQUENCE')
    count=0
    for k in keys:
        e=p[k]
        if e['root']!='PROJECTS/KAIRON/native/musical_intelligence/' or not e['bindings']: raise ValueError('NMI_SCOPE')
        for name,sha in e['bindings'].items():
            if Path(name).name!=name or '/' in name or '\\' in name or name in ('.','..'): raise ValueError('NMI_PATH')
            if blob(read('native/musical_intelligence/'+name))!=sha: raise ValueError('NMI_HASH:'+name)
            count+=1
    w=load('windows_studio/NATIVE_BINDING.json'); q=load('plugin/release-binding.json')
    pointer=blob(raw)
    if w['system_id']!='666TDI-001' or q['system_id']!='666TDI-001': raise ValueError('SURFACE_IDENTITY')
    aligned=w['pointer_git_blob_sha1']==q['canonical_pointer_blob']==pointer and w['expected_nmi_revisions']==len(keys) and w['expected_nmi_bindings']==count
    return {'status':'SOURCE_BINDINGS_ALIGNED' if aligned else 'NATIVE_EVOLUTION_PENDING','pointer':pointer,'nmi_revisions':len(keys),'bindings':count,'triggers':len(commands),'events':c['revision'],'production_release':False,'host_acceptance':'OPEN'}

if __name__=='__main__':
    try:
        result=audit(sys.argv[1]); print(json.dumps(result,indent=2)); sys.exit(0 if result['status']=='SOURCE_BINDINGS_ALIGNED' else 2)
    except Exception as exc:
        print(json.dumps({'status':'READBACK_PENDING','error':str(exc)})); sys.exit(2)
