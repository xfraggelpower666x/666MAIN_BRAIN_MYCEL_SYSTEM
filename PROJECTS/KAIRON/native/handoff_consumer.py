#!/usr/bin/env python3
"""666TDI-001 read-only native CLIC R11 handoff consumer.
Source handoffs are inert data. This CLI never writes to any repository.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,urllib.request
from typing import Any

SYSTEM='666TDI-001'
ID='CLIC-TO-666TDI-R11-20261122-01'
SOURCE_REPO='xfraggelpower666x/666CLICPRO'
SOURCE_BRANCH='clic-migration-rev79-staging'
SOURCE_HEAD='0d955834f58181cf1b0cb94c8c81dc299c07dbfe'
SOURCE_TREE='f39f2dd42562d0d171346335f905a3ca8b22c615'
SOURCE_BLOB='b9dfe4a3e153dc494f3966e216787cbf8918c529'
PATH='666CLIC_NATIVE_RUNTIME/outbox/666TDI/'+ID+'.json'
REQUIRED={f'TDI-{i:02}' for i in range(1,7)}

def git_blob_sha(blob:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()

def validate_handoff(payload:bytes)->dict[str,Any]:
    if git_blob_sha(payload)!=SOURCE_BLOB: raise ValueError('HANDOFF_BLOB_MISMATCH')
    h=json.loads(payload)
    expect={'handoff_id':ID,'source_repo':SOURCE_REPO,'source_branch':SOURCE_BRANCH,
            'target_system_id':SYSTEM,'target_repo':'xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM',
            'target_branch':'666MAIN_BRAIN','target_root':'PROJECTS/666TDI'}
    for field,value in expect.items():
        if h.get(field)!=value:raise ValueError('HANDOFF_CONTRACT_MISMATCH:'+field)
    found=[x.get('id') for x in h.get('findings',[])]
    if set(found)!=REQUIRED or len(found)!=6:raise ValueError('HANDOFF_FINDINGS_INCOMPLETE')
    if h.get('status')!='PREPARED_SOURCE_REPO_ONLY_NOT_DELIVERED':raise ValueError('SOURCE_STATUS_UNEXPECTED')
    return h

def get_json(url:str)->dict:
    with urllib.request.urlopen(urllib.request.Request(url,headers={'Accept':'application/vnd.github+json','User-Agent':'666TDI-readonly'}),timeout=15) as resp:
        return json.load(resp)

def verify_remote()->dict:
    base='https://api.github.com/repos/'+SOURCE_REPO
    # Historischer R11-Anker bleibt fest, der CLIC-Branch darf unabhängig fortschreiten.
    head=get_json(base+'/git/ref/heads/'+SOURCE_BRANCH)
    current_head=head.get('object',{}).get('sha')
    if not isinstance(current_head,str) or len(current_head)!=40:
        raise ValueError('CURRENT_SOURCE_HEAD_INVALID')
    current_commit=get_json(base+'/git/commits/'+current_head)
    if current_commit.get('sha')!=current_head:
        raise ValueError('CURRENT_SOURCE_COMMIT_MISMATCH')
    current_tree=get_json(base+'/git/trees/'+current_commit['tree']['sha']+'?recursive=1')
    current_matches=[x for x in current_tree.get('tree',[]) if x.get('path')==PATH and x.get('type')=='blob']
    if current_tree.get('truncated') or len(current_matches)!=1 or current_matches[0].get('sha')!=SOURCE_BLOB:
        raise ValueError('CURRENT_SOURCE_HANDOFF_CHANGED_OR_MISSING')
    commit=get_json(base+'/git/commits/'+SOURCE_HEAD)
    if commit['sha']!=SOURCE_HEAD or commit['tree']['sha']!=SOURCE_TREE:raise ValueError('SOURCE_COMMIT_TREE_MISMATCH')
    tree=get_json(base+'/git/trees/'+SOURCE_TREE+'?recursive=1')
    matches=[x for x in tree['tree'] if x['path']==PATH and x['type']=='blob']
    if tree.get('truncated') or len(matches)!=1 or matches[0]['sha']!=SOURCE_BLOB:raise ValueError('SOURCE_TREE_HANDOFF_MISMATCH')
    data=get_json(base+'/git/blobs/'+SOURCE_BLOB)
    import base64
    if data.get('encoding')!='base64':raise ValueError('SOURCE_BLOB_ENCODING')
    blob=base64.b64decode(data['content'])
    validate_handoff(blob)
    return {'source_commit':SOURCE_HEAD,'source_tree':SOURCE_TREE,'handoff_blob':SOURCE_BLOB,
            'current_source_head':current_head,'current_handoff_blob':current_matches[0]['sha'],
            'readback':'VERIFIED'}

def inspect(root:pathlib.Path,payload:bytes, remote:bool=False)->dict:
    h=validate_handoff(payload)
    pointer=json.loads((root/'CURRENT_POINTER.json').read_text('utf-8'))
    authority=json.loads((root/'governance/NATIVE_UPDATE_AUTHORITY.json').read_text('utf-8'))
    manifest=json.loads((root/'transfer/SOURCE_MANIFEST.json').read_text('utf-8'))
    if pointer.get('system_id')!=SYSTEM or authority.get('system_id')!=SYSTEM:raise ValueError('NATIVE_IDENTITY_MISMATCH')
    if authority.get('allowed_path_prefix')!='PROJECTS/KAIRON/' or authority.get('foreign_autoactivation') is not False:
        raise ValueError('INVALID_NATIVE_SCOPE')
    if pointer.get('audio_analysis_required') is not False:raise ValueError('AUDIO_OPTIONAL_CONTRACT_VIOLATION')
    source=root/'source'
    defects=[]
    for path,digest in manifest['source_files'].items():
        actual=source/path
        if not actual.is_file() or hashlib.sha256(actual.read_bytes()).hexdigest()!=digest:
            defects.append(path)
    result={'system_id':SYSTEM,'handoff_id':ID,'findings':[x['id'] for x in h['findings']],
      'native_current':pointer.get('development_layer'),'source_manifest_files':len(manifest['source_files']),
      'source_bytes_verified':not defects,'manifest_failures':defects,'audio_optional':True,
      'no_foreign_writes':True,'consumer_mode':'READ_ONLY',
      'status':'VERIFIED_READ_ONLY' if not defects else 'PARTIAL'}
    if remote:result['source_remote_verification']=verify_remote()
    return result

def main():
    a=argparse.ArgumentParser();a.add_argument('handoff_json');a.add_argument('--root',default=str(pathlib.Path(__file__).resolve().parents[1]));a.add_argument('--remote-verify',action='store_true')
    args=a.parse_args();p=pathlib.Path(args.handoff_json)
    try:
        result=inspect(pathlib.Path(args.root),p.read_bytes(),args.remote_verify)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0 if result['status']=='VERIFIED_READ_ONLY' else 2
    except (ValueError,KeyError,OSError,TypeError) as exc:
        print(json.dumps({'system_id':SYSTEM,'status':'READBACK_PENDING','reason':str(exc)}));return 2
if __name__=='__main__':raise SystemExit(main())
