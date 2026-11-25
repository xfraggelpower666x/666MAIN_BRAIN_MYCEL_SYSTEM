"""Optional contract smoke test for a separately authorized candidate implementation.
Does not contain or synthesize CURES. Avoid untrusted candidate paths: imports execute code.
Usage: python tools/check_candidate.py /absolute/trusted/candidate.py
Candidate must export reconstruct(payload:dict)->dict.
"""
import importlib.util, sys, json, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    if len(sys.argv)!=2:
        print('Usage: python tools/check_candidate.py /path/to/trusted/candidate.py');return 2
    spec=importlib.util.spec_from_file_location('candidate',sys.argv[1])
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    tests=json.loads((ROOT/'fixtures/cases.json').read_text(encoding='utf-8'))
    failures=[]
    for f in tests:
        result=module.reconstruct({'source_system':f['source_system'],'source_text':f['source_text'],'kind':f['kind']})
        if not isinstance(result,dict):failures.append((f['case_id'],'not a dict'));continue
        required=('fulltext','source_system','preserved_identity','evidence_map','inferred_claims','authority_changed','mutations')
        for key in required:
            if key not in result: failures.append((f['case_id'],'missing '+key))
        if not all(k in result for k in required):continue
        txt=result['fulltext']
        if not isinstance(txt,str):failures.append((f['case_id'],'fulltext not string'));continue
        if result['source_system']!=f['source_system'] or result['preserved_identity']!=f['source_system']:
            failures.append((f['case_id'],'identity drift'))
        if result['authority_changed'] is not False or result['mutations']!=[]:
            failures.append((f['case_id'],'authority/mutation violation'))
        if not isinstance(result['evidence_map'],list) or not isinstance(result['inferred_claims'],list):
            failures.append((f['case_id'],'invalid trace shape'))
        for phrase in f['assertions']['forbidden_assertions']:
            if phrase.lower() in txt.lower():failures.append((f['case_id'],'forbidden assertion: '+phrase))
        if not any(tok.lower() in txt.lower() for tok in f['assertions']['must_contain_any_language_concept']):
            failures.append((f['case_id'],'none of concept markers found'))
    for cid,message in failures:print('FAIL',cid,message)
    print(f'CANDIDATE_SMOKE_TEST: {len(tests)} fixtures, {len(failures)} failures; semantic review still mandatory')
    return int(bool(failures))
if __name__=='__main__':raise SystemExit(main())
