"""Read-only, manifest-bound asset inventory. Never grants publication rights."""
import hashlib, json, re, zipfile
from pathlib import Path
from PIL import Image

def blob(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def inspect(root, manifest, archives, pending):
    result={}
    for rel in pending:
        prefix, member=rel.split('/',1)
        with zipfile.ZipFile(archives[prefix]) as z:
            b=z.read(member)
        if blob(b)!=manifest[rel] or b!=(root/rel).read_bytes(): raise ValueError('source mismatch: '+rel)
        ext=Path(rel).suffix.lower(); row=dict(sha=manifest[rel],sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),archive=Path(archives[prefix]).name,member=member,source_review='PASS',public_release=False,rights_review='HOLD',privacy_review='HOLD')
        if ext=='.log':
            s=b.decode('utf-8',errors='replace'); row.update(kind='diagnostic',windows_path=bool(re.search(r'[A-Za-z]:[\\/]',s)),credential_pattern=bool(re.search(r'(?i)(?:api[_ -]?key|password|token|secret)\s*[:=]\s*\S+',s)),reason='Original log requires manual privacy review')
        elif ext=='.exe':
            row.update(kind='executable',pe_header=b[:2]==b'MZ',gpl_marker=b'--enable-gpl' in b,nonfree_marker=b'--enable-nonfree' in b,reason='Exact build provenance and redistribution terms unresolved')
        else:
            with Image.open(root/rel) as im:
                row.update(kind='image',format=im.format,dimensions=list(im.size),metadata_keys=sorted(map(str,im.info)),exif_present=bool(im.getexif()))
            with Image.open(root/rel) as im: im.verify()
            row['reason']='Rights and visual/metadata privacy require review'
        result[rel]=row
    return result
