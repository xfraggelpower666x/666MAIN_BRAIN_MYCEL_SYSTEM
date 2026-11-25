"""Fail-closed native source verification; never writes native authority."""
from pathlib import Path
import hashlib,json,re

def blob(path):
    data=path.read_bytes()
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def verify(studio):
    studio=Path(studio).resolve(); project=studio.parent
    binding=json.loads((studio/'NATIVE_BINDING.json').read_text(encoding='utf-8'))
    pointer=project/'CURRENT_POINTER.json'
    if blob(pointer)!=binding['pointer_git_blob_sha1']:
        raise ValueError('NATIVE_EVOLUTION_PENDING: Windows parity review required')
    state=json.loads(pointer.read_text(encoding='utf-8'))
    if state.get('system_id')!=binding['system_id']: raise ValueError('FOREIGN_AUTHORITY')
    keys=[k for k in state if re.fullmatch(r'native_musical_intelligence_r\d+',k)]
    if len(keys)!=binding['expected_nmi_revisions']:raise ValueError('NMI_REVISION_COUNT_MISMATCH')
    count=0
    for k in keys:
        entry=state[k]
        if entry['root']!='PROJECTS/666TDI/native/musical_intelligence/':raise ValueError('FOREIGN_ROOT')
        for name,sha in entry['bindings'].items():
            f=(project/'native/musical_intelligence'/name).resolve()
            if not f.is_relative_to((project/'native/musical_intelligence').resolve()) or blob(f)!=sha:raise ValueError('NMI_BINDING_MISMATCH:'+name)
            count+=1
    if count!=binding['expected_nmi_bindings']:raise ValueError('NMI_BINDING_COUNT_MISMATCH')
    return {'system_id':binding['system_id'],'status':'NATIVE_BINDINGS_VERIFIED','bindings':count,'pointer':blob(pointer)}

if __name__=='__main__':print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
