"""Additiver, bytegenauer Git-Transfer. Kein Checkout, keine ZIP-Veröffentlichung.
Ausführung nur mit bestehender Git-Authentifizierung; keine Tokens in Argumenten.
"""
import argparse, hashlib, json, os, pathlib, re, subprocess, tempfile

BASE='c57167da1bcdc7de85fa2a6682232abb815fbc8d'
SOURCE_REF='refs/heads/integration/lyvra-mp3-r024'
TARGET_REF='refs/heads/integration/lyvra-mp3-r025-bulk'
BACKUP_REF='refs/heads/backup/lyvra-mp3-pre-r025-c57167d'
REMOTE='https://github.com/xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM.git'
PREFIX='PROJECTS/LYVRA_MP3_COMMAND_CENTER/originals/'

def run(repo, *args, data=None, env=None):
    p=subprocess.run(['git','-C',str(repo),*args],input=data,capture_output=True,env=env)
    if p.returncode: raise RuntimeError('Git '+args[0]+' fehlgeschlagen: '+p.stderr.decode(errors='replace')[-1200:])
    return p.stdout

def blob(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def tree(repo, ref):
    out={}
    for record in run(repo,'ls-tree','-rz',ref).split(b'\0'):
        if record:
            meta,p=record.split(b'\t',1); mode,kind,sha=meta.decode().split();out[p.decode('utf-8')]=(mode,kind,sha)
    return out

def remote_ref(repo, remote, ref):
    result=run(repo,'ls-remote','--refs',remote,ref).decode().splitlines()
    if len(result)>1: raise ValueError('Mehrdeutiger Ref')
    return result[0].split('\t')[0] if result else None

def verified_sources(root, manifest):
    root=root.resolve(); result={}
    for rel,sha in manifest.items():
        pp=pathlib.PurePosixPath(rel)
        if pp.is_absolute() or any(x in ('','.','..') or '\\' in x or ':' in x for x in pp.parts) or pp.parts[0] not in ('mp3','dj','restore','boot') or not re.fullmatch('[0-9a-f]{40}',sha): raise ValueError('Ungültiger Manifestpfad: '+rel)
        src=root.joinpath(*pp.parts)
        if not src.is_file() or not src.resolve().is_relative_to(root) or any(x.is_symlink() for x in [src,*src.parents] if x!=root and x.is_relative_to(root)): raise ValueError('Quelle fehlt oder Symlink: '+rel)
        if src.suffix.lower()=='.zip': raise ValueError('ZIP im Manifest: '+rel)
        b=src.read_bytes()
        if len(b)>=100*1024*1024: raise ValueError('GitHub-Dateigrößenlimit: '+rel)
        if blob(b)!=sha: raise ValueError('SHA-Konflikt: '+rel)
        result[rel]=src
    return result

def transfer(root,manifest,remote=REMOTE,base=BASE,source_ref=SOURCE_REF,target_ref=TARGET_REF,backup_ref=BACKUP_REF,apply=False):
    sources=verified_sources(root,manifest)
    with tempfile.TemporaryDirectory(prefix='lyvra-git-') as d:
        repo=pathlib.Path(d);run(repo,'init','--bare','--quiet')
        if remote_ref(repo,remote,source_ref)!=base: raise ValueError('Quellbranch hat sich verändert')
        run(repo,'fetch','--no-tags',remote,source_ref)
        if run(repo,'rev-parse','FETCH_HEAD').decode().strip()!=base: raise ValueError('Fetch-SHA-Konflikt')
        old=tree(repo,base); existing={p[len(PREFIX):]:v for p,v in old.items() if p.startswith(PREFIX)}
        if any(p not in manifest or v[1]!='blob' or v[2]!=manifest[p] for p,v in existing.items()): raise ValueError('Vorhandene Originale weichen ab; keine Änderung')
        missing=sorted(set(manifest)-set(existing))
        receipt={'base':base,'expected':len(manifest),'preserved':len(existing),'missing':len(missing),'bytes_to_transfer':sum(sources[p].stat().st_size for p in missing),'target':target_ref,'published':False}
        if not apply: return receipt
        if remote_ref(repo,remote,target_ref) is not None: raise ValueError('Zielbranch existiert bereits')
        if remote_ref(repo,remote,backup_ref) not in (None,base): raise ValueError('Backup-Konflikt')
        run(repo,'read-tree',base)
        for rel in missing:
            b=sources[rel].read_bytes()
            if blob(b)!=manifest[rel]: raise ValueError('Quelle nach Prüfung verändert: '+rel)
            sha=run(repo,'hash-object','-w','--stdin',data=b).decode().strip()
            if sha!=manifest[rel]: raise ValueError('Git-Blob-Konflikt: '+rel)
            run(repo,'update-index','--add','--cacheinfo','100644',sha,PREFIX+rel)
        candidate=run(repo,'write-tree').decode().strip();new=tree(repo,candidate)
        if any(new.get(p)!=v for p,v in old.items()): raise ValueError('Bestehender Tree verändert')
        if set(new)-set(old)!={PREFIX+p for p in missing}: raise ValueError('Scope-Verletzung')
        if any(new[PREFIX+p][2]!=s for p,s in manifest.items()): raise ValueError('Tree-SHA-Konflikt')
        env=dict(os.environ,GIT_AUTHOR_NAME='LYVRA Source Recovery',GIT_AUTHOR_EMAIL='source-recovery@users.noreply.github.com',GIT_COMMITTER_NAME='LYVRA Source Recovery',GIT_COMMITTER_EMAIL='source-recovery@users.noreply.github.com')
        commit=run(repo,'commit-tree',candidate,'-p',base,'-m','R02.5: bytegenaue additive Originalquellen',env=env).decode().strip()
        if remote_ref(repo,remote,source_ref)!=base: raise ValueError('Quellbranch inzwischen verändert')
        if remote_ref(repo,remote,backup_ref) is None:run(repo,'push',f'--force-with-lease={backup_ref}:',remote,f'{base}:{backup_ref}')
        if remote_ref(repo,remote,backup_ref)!=base: raise ValueError('Backup-Readback fehlgeschlagen')
        run(repo,'push',f'--force-with-lease={target_ref}:',remote,f'{commit}:{target_ref}')
        if remote_ref(repo,remote,target_ref)!=commit: raise ValueError('Branch-Readback fehlgeschlagen')
        # Unabhängiger neuer Object Store: Remote-Tree erneut abrufen.
        with tempfile.TemporaryDirectory(prefix='lyvra-readback-') as rd:
            read=pathlib.Path(rd);run(read,'init','--bare','--quiet');run(read,'fetch','--no-tags',remote,target_ref)
            if run(read,'rev-parse','FETCH_HEAD').decode().strip()!=commit or tree(read,commit)!=new: raise ValueError('Unabhängiger Tree-Readback fehlgeschlagen')
            for rel,sha in manifest.items():
                if blob(run(read,'cat-file','blob',sha))!=sha: raise ValueError('Blob-Readback fehlgeschlagen: '+rel)
        receipt.update(published=True,commit=commit,tree=candidate,verified=len(manifest));return receipt

def main():
    p=argparse.ArgumentParser();p.add_argument('originals',type=pathlib.Path);p.add_argument('--manifest',type=pathlib.Path,default=pathlib.Path(__file__).with_name('original-manifest.json'));p.add_argument('--apply',action='store_true');p.add_argument('--public-review-confirmed',action='store_true');a=p.parse_args()
    m=json.loads(a.manifest.read_text(encoding='utf-8'))
    if len(m)!=308: raise SystemExit('Erwartet: vollständiges 308-Dateien-Manifest')
    if a.apply and not a.public_review_confirmed: raise SystemExit('Vor Veröffentlichung öffentliche Freigabe aller Dateien/Assets und Geheimnisprüfung bestätigen.')
    print(json.dumps(transfer(a.originals,m,apply=a.apply),indent=2))
if __name__=='__main__':main()
