"""Read-only catalog/current comparison. A hash match does NOT establish native authority."""
from __future__ import annotations
import argparse, hashlib, json, sqlite3, datetime
from pathlib import Path

def summarize(catalog:Path,project:str,current:Path|None=None,expected_sha256:str|None=None):
    uri='file:'+catalog.resolve().as_posix()+'?mode=ro'
    c=sqlite3.connect(uri,uri=True)
    try:
        counts={k:int(v) for k,v in c.execute('SELECT category, count(*) FROM records WHERE project=? AND archived=0 GROUP BY category',(project,))}
        sources=int(c.execute('SELECT count(distinct source_name) FROM records WHERE project=?',(project,)).fetchone()[0]);total=sum(counts.values())
    finally:c.close()
    reference={'status':'NO_REFERENCE','path':None,'sha256':None,'fingerprint_matches':None,'native_authority':'NOT_VERIFIED'}
    if current:
        data=current.read_bytes();digest=hashlib.sha256(data).hexdigest()
        reference.update({'status':'CANDIDATE_ONLY','path':current.name,'sha256':digest,'fingerprint_matches':None})
        if expected_sha256:
            match=digest.lower()==expected_sha256.lower()
            reference.update({'status':'CANDIDATE_HASH_MATCHED' if match else 'HASH_CONFLICT','fingerprint_matches':match})
        try:parsed=json.loads(data)
        except json.JSONDecodeError:parsed=None
        if isinstance(parsed,dict):
            reference['declared_identity']={k:parsed.get(k) for k in ('system','system_id','project','branch','repository') if k in parsed}
    return {
        'schema':'666-catalog-reconciliation.v1','project':project,
        'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'catalog':{'records':total,'categories':counts,'sources':sources},
        'reference':reference,
        'comparison':{'outcome':'REVIEW_REQUIRED','identity_conflict':('declared_identity' in reference and project.upper() not in json.dumps(reference['declared_identity']).upper()),'notes':['Catalog source categories are heuristics, not authoritative software state.','Native Current requires independent trusted repository readback; a local hash is not sufficient.','No foreign project pointers, repositories or runtimes are written.']},
        'proposals':[{'category':category,'records':n,'action':'Review matching original source evidence against native project Current'} for category,n in sorted(counts.items())]
    }

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--catalog',required=True,type=Path);p.add_argument('--project',required=True);p.add_argument('--native-current',type=Path);p.add_argument('--expected-sha256');p.add_argument('--output',type=Path);args=p.parse_args()
    result=summarize(args.catalog,args.project,args.native_current,args.expected_sha256)
    rendered=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(rendered,encoding='utf-8')
    else:print(rendered)
