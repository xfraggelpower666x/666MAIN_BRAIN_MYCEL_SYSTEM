"""KAIRON candidate: verify connector bytes, execute scoped regression, capture evidence."""
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile


def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def path_parts(name):
    if not isinstance(name, str) or '\\' in name or ':' in name or any(p in ('', '.', '..') for p in name.split('/')):
        raise ValueError('INVALID_PATH')
    p = PurePosixPath(name)
    if p.is_absolute():
        raise ValueError('INVALID_PATH')
    return p.parts


def run(bundle):
    if bundle.get('system_id') != '666TDI-001' or bundle.get('namespace') != 'KAIRON' or bundle.get('scope') != 'PROJECTS/KAIRON/':
        raise ValueError('FOREIGN_SCOPE')
    if not re.fullmatch(r'[0-9a-f]{40}', bundle.get('commit', '')):
        raise ValueError('COMMIT_REQUIRED')
    if bundle.get('execute') is not True:
        raise ValueError('EXECUTION_APPROVAL_REQUIRED')
    sources = {}
    for entry in bundle['files']:
        name = entry['path']; path_parts(name)
        if name in sources:
            raise ValueError('DUPLICATE_PATH')
        data = base64.b64decode(''.join(entry['base64'].split()), validate=True)
        if blob(data) != entry['sha']:
            raise ValueError('BLOB_MISMATCH:'+name)
        sources[name] = data
    test = bundle['test']; path_parts(test)
    if test not in sources or not PurePosixPath(test).name.startswith('test_') and not test.endswith('.test.cjs'):
        raise ValueError('TEST_NOT_BOUND')
    with tempfile.TemporaryDirectory(prefix='kairon-regression-') as tmp:
        root = Path(tmp)
        for name, data in sources.items():
            dst = root.joinpath(*path_parts(name)); dst.parent.mkdir(parents=True, exist_ok=True); dst.write_bytes(data)
            if blob(dst.read_bytes()) != blob(data):
                raise ValueError('LOCAL_READBACK_MISMATCH:'+name)
        env = {k: os.environ[k] for k in ('PATH','SYSTEMROOT','WINDIR','TEMP','TMP') if k in os.environ}
        env.update(PYTHONPATH=os.pathsep.join(map(str, (root/'source', (root/test).parent))), PYTHONDONTWRITEBYTECODE='1', HOME=tmp)
        if test.endswith('.py'):
            cmd = [sys.executable, '-m', 'unittest', 'discover', '-s', str((root/test).parent), '-p', PurePosixPath(test).name, '-v']
        elif test.endswith('.test.cjs'):
            cmd = ['node', '--test', str(root/test)]
        else:
            raise ValueError('UNSUPPORTED_TEST')
        result = subprocess.run(cmd, cwd=root, env=env, capture_output=True, text=True, timeout=120)
        count = re.search(r'^Ran (\d+) tests? in ', result.stderr, re.M) if test.endswith('.py') else re.search(r'^# tests (\d+)$', result.stdout, re.M)
        executed = int(count.group(1)) if count else 0
        status = 'NO_TESTS_EXECUTED' if count and executed == 0 else ('REGRESSION_FAILED' if result.returncode else ('PROCESS_EXIT_ZERO' if executed > 0 else 'NO_TESTS_EXECUTED'))
        return {'test_count':executed,'system_id':'666TDI-001','commit':bundle['commit'],'test':test,'blobs':{k:blob(v) for k,v in sources.items()},'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'status':status,'production_release':False,'host_acceptance':'OPEN'}


if __name__ == '__main__':
    result=run(json.load(sys.stdin)); print(json.dumps(result, ensure_ascii=False)); sys.exit(result['exit_code'] or (2 if result['status'] != 'PROCESS_EXIT_ZERO' else 0))
