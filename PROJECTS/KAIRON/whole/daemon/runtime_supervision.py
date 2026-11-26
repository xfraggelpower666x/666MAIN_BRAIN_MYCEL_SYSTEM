"""R19.7: connect verified native execution to existing R17/R18 and guidance.
Candidate-only, no autonomous dispatch, no host or production acceptance.
"""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
from execution_trust import oid
from connector_runtime import execute_native
from guidance import guidance

BASE = 'f95229f549196522142e1b59a83c7d3d9a64ae6d'
TESTED = '2f374738359feaff564e73fd90c5b52766b26529'
ROOT = Path(__file__).resolve().parents[2]
PINS = {
    'whole/daemon/CONTRACT.json': '2e2ac3ff473b765d58937f8ae64d36dcc18f9a06',
    'whole/daemon/supervision.mjs': '10156e77995a5b015640c6f7709399800381b9ba',
    'whole/daemon/guidance.py': '594de3184b718d49f137904ada2451dffb1569c0',
    'whole/daemon/connector_runtime.py': '4c752b6a3b8be6e604834da4d9ba32b3e1242d1c',
    'whole/daemon/execution_trust.py': 'e09ffca2c18e1c4aa1f5dbb659163340989cf062',
    'whole/daemon/execution_bridge.py': '5441a8baccbb61a0211002bb5a01b3381e108c1f',
    'whole/daemon/development_watchdog.py': '970fccc937f724e33d1718914e9d61559866d126',
    'whole/visual/MENU.json': '4e9693337ad06c514206211224503cd7303e6b8f',
}
SUITES = {'source/tests/test_creative_causal.py': 9,
          'source/tests/test_semantic_intelligence.py': 12}
FILES = frozenset((*SUITES, 'whole/daemon/execution_bridge.py', 'source/engine/__init__.py',
                   'source/engine/semantic_intelligence.py', 'source/engine/creative_causal.py'))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def check_pins(root):
    for name, sha in PINS.items():
        if oid('blob', (root/name).read_bytes()) != sha:
            raise ValueError('RUNTIME_PIN_MISMATCH:'+name)


def classify(result, test):
    """Only called on an execution result produced in this invocation."""
    evidence = result.get('membership_evidence', {})
    if (result.get('system_id') != '666TDI-001' or result.get('commit') != TESTED
        or result.get('test') != test or evidence.get('commit') != TESTED
        or evidence.get('status') != 'COMMIT_TREE_BLOB_VERIFIED'
        or evidence.get('tree') != '4e51f81b5a28b23a7a75785beef0db368d792472'
        or evidence.get('blobs') != result.get('blobs') or not result.get('blobs')):
        raise ValueError('UNBOUND_EXECUTION_RESULT')
    passed = (result.get('status') == 'PROCESS_EXIT_ZERO' and result.get('exit_code') == 0
              and result.get('test_count') == SUITES[test]
              and not any(s in result.get('stderr', '') for s in ('skipped=', 'expected failures=', 'unexpected successes=')))
    return passed, 'sha256:'+digest(result)


def node_supervision(root, payload):
    # Import the unchanged, pinned R17/R18 implementation; no shell or user code.
    script = "import {supervise,diagnose} from './supervision.mjs'; import fs from 'node:fs'; const p=JSON.parse(fs.readFileSync(0,'utf8')); console.log(JSON.stringify({r17:supervise(p.r17),r18:diagnose(p.r18)}));"
    r = subprocess.run(['node','--input-type=module','-e',script], cwd=root/'whole/daemon', input=json.dumps(payload), text=True, capture_output=True, timeout=30, check=True)
    return json.loads(r.stdout)


def run(snapshot, state, *, trusted_base, execute=False, test='source/tests/test_creative_causal.py'):
    if execute is not True:
        raise ValueError('EXECUTION_APPROVAL_REQUIRED')
    if trusted_base != BASE:
        raise ValueError('BASE_REQUIRES_REVALIDATION')
    if not isinstance(state, dict) or state.get('system_id') != '666TDI-001' or state.get('active_namespace') != 'KAIRON':
        raise ValueError('FOREIGN_CONTEXT')
    if not state.get('workspace') or not state.get('lineage') or not isinstance(state.get('open_gates'), list):
        raise ValueError('INCOMPLETE_CONTEXT')
    if test not in SUITES:
        raise ValueError('UNAPPROVED_SUITE')
    check_pins(ROOT)
    if set(snapshot.get('files', {})) != FILES:
        raise ValueError('UNAPPROVED_SOURCE_SET')
    trees = {t['sha']:t for t in snapshot['trees']}
    result = execute_native(lambda k,s: snapshot['commit'] if k == 'commit' else trees[s],
        lambda p,h: base64.b64decode(snapshot['files'][p], validate=True),
        trusted_head=TESTED, paths=list(snapshot['files']), test=test, execute=True)
    passed, ref = classify(result, test)
    receipts = [{'kind':'REGRESSION_PASS','ref':ref,'verified':True}] if passed else []
    observations = [] if passed else [{'kind':'EXECUTION_DRIFT','evidence_ref':ref,'verified':True}]
    # Never import caller-supplied receipts/observations or infer a productive Current.
    js = node_supervision(ROOT, {'r17':{'system_id':'666TDI-001','receipts':receipts},
        'r18':{'system_id':'666TDI-001','active_namespace':'KAIRON','direct':state.get('direct') is True,
               'command':state.get('command'),'current_verified':False,'current_ref':None,
               'workspace':state['workspace'],'observations':observations}})
    local = dict(state)
    local['open_gates'] = list(dict.fromkeys(state['open_gates']+js['r17']['missing']+['NATIVE_CURRENT_WITHHELD']))
    if not passed:
        local['open_gates'].append('NATIVE_REGRESSION')
    local['last_verified_step'] = {'evidence_ref':ref} if passed else None
    local['next_action'] = None
    view = guidance(local, root=ROOT, trusted_receipts=receipts)
    return {'revision':'R19.7','status':'CANDIDATE_REGRESSION_VERIFIED' if passed else 'REGRESSION_FAILED',
            'integration_base':BASE,'tested_commit':TESTED,'receipt_ref':ref,'execution':result,
            'supervision':js,'guidance':view,'release_authorized':False,'production_promotion':False,
            'automatic_dispatch':False,'host_acceptance':'OPEN'}


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', type=Path, required=True)
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--trusted-base', required=True)
    parser.add_argument('--test', choices=tuple(SUITES), default='source/tests/test_creative_causal.py')
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if not args.execute:
        parser.error('explicit --execute required')
    result = run(json.loads(args.snapshot.read_text(encoding='utf-8')),
                 json.loads(args.state.read_text(encoding='utf-8')),
                 trusted_base=args.trusted_base, execute=True, test=args.test)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['status'] == 'CANDIDATE_REGRESSION_VERIFIED' else 2


if __name__ == '__main__':
    raise SystemExit(main())
