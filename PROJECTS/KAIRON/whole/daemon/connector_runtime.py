"""KAIRON R19.6: bind authorized Git Data responses to existing execution gate."""
import base64
from datetime import datetime
from pathlib import Path
from itertools import product
from execution_trust import ROOT, SHA, oid, tree_entries, run_verified

BRIDGE = 'whole/daemon/execution_bridge.py'


def raw_commit(meta, head):
    if meta['sha'] != head:
        raise ValueError('HEAD_MISMATCH')
    if meta.get('verification', {}).get('reason') != 'unsigned':
        raise ValueError('UNSUPPORTED_COMMIT_FORMAT')
    tree = meta['tree'] if isinstance(meta['tree'], str) else meta['tree']['sha']
    parents = [p if isinstance(p, str) else p['sha'] for p in meta['parents']]
    if not all(SHA.fullmatch(s) for s in [tree, *parents]):
        raise ValueError('INVALID_COMMIT_REFERENCE')
    prefix = 'tree '+tree+'\n'+''.join('parent '+p+'\n' for p in parents)
    def identity(key, zone):
        v = meta[key]
        t = int(datetime.fromisoformat(v['date'].replace('Z', '+00:00')).timestamp())
        return f'{key} {v["name"]} <{v["email"]}> {t} {zone}\n'
    zones = list(dict.fromkeys(['+0000', '+0100', '+0200', '-0000'] + [f'{s}{h:02d}{m:02d}' for s in ('+', '-') for h in range(15) for m in (0,15,30,45)]))
    for a, b in product(zones, repeat=2):
        for suffix in ('\n', ''):
            raw = (prefix+identity('author', a)+identity('committer', b)+'\n'+meta['message']+suffix).encode()
            if oid('commit', raw) == head:
                return raw, tree
    raise ValueError('COMMIT_RAW_HASH_MISMATCH')


def raw_tree(meta, expected):
    if meta['sha'] != expected or meta.get('truncated') is not False:
        raise ValueError('TREE_INCOMPLETE_OR_MISMATCH')
    entries = meta['entries'] if 'entries' in meta else [(e['path'],e['mode'],e['sha']) for e in meta['tree']]
    raw = b''.join(mode.lstrip('0').encode()+b' '+name.encode()+b'\0'+bytes.fromhex(sha) for name,mode,sha in entries)
    if oid('tree', raw) != expected:
        raise ValueError('TREE_RAW_HASH_MISMATCH')
    tree_entries(raw)
    return raw


def acquire(read_git, read_file, *, trusted_head, paths, test, execute=False):
    """Callbacks are authorized read transports; head is independently supplied."""
    if execute is not True:
        raise ValueError('EXECUTION_APPROVAL_REQUIRED')
    if not SHA.fullmatch(trusted_head):
        raise ValueError('INVALID_HEAD')
    if len(paths) != len(set(paths)) or test not in paths or BRIDGE not in paths:
        raise ValueError('REQUIRED_PATH_OR_DUPLICATE')
    commit, root = raw_commit(read_git('commit', trusted_head), trusted_head)
    objects = {trusted_head: base64.b64encode(commit).decode()}
    cache = {}
    files = []
    for path in paths:
        if not isinstance(path,str) or '\\' in path or ':' in path or any(p in ('','.','..') for p in path.split('/')):
            raise ValueError('INVALID_PATH')
        current = root
        parts = (ROOT+path).encode().split(b'/')
        for i, part in enumerate(parts):
            if current not in cache:
                raw = raw_tree(read_git('tree',current), current)
                objects[current] = base64.b64encode(raw).decode()
                cache[current] = tree_entries(raw)
            mode, current = cache[current].get(part, (b'', ''))
            if not current or (i < len(parts)-1 and mode != b'40000'):
                raise ValueError('PATH_NOT_IN_COMMIT')
        if mode not in (b'100644',b'100755'):
            raise ValueError('NOT_REGULAR_FILE')
        data = read_file(path, trusted_head)
        if not isinstance(data,bytes) or oid('blob',data) != current:
            raise ValueError('BLOB_NOT_IN_COMMIT')
        files.append({'path':path,'sha':current,'base64':base64.b64encode(data).decode()})
    return {'system_id':'666TDI-001','namespace':'KAIRON','scope':ROOT,'commit':trusted_head,'execute':True,'test':test,'files':files}, objects


def execute_native(read_git, read_file, *, trusted_head, paths, test, execute=False):
    bundle, objects = acquire(read_git,read_file,trusted_head=trusted_head,paths=paths,test=test,execute=execute)
    import execution_bridge
    expected = next(e['sha'] for e in bundle['files'] if e['path'] == BRIDGE)
    if oid('blob',Path(execution_bridge.__file__).read_bytes()) != expected:
        raise ValueError('LOCAL_BRIDGE_MISMATCH')
    return run_verified(bundle,objects,trusted_head=trusted_head)


def main():
    import argparse
    import json
    parser = argparse.ArgumentParser(description='KAIRON: explicitly execute a trusted Git Data snapshot')
    parser.add_argument('--snapshot', required=True, type=Path)
    parser.add_argument('--trusted-head', required=True)
    parser.add_argument('--test', required=True)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if not args.execute:
        parser.error('explicit --execute required')
    snapshot = json.loads(args.snapshot.read_text(encoding='utf-8'))
    trees = {t['sha']:t for t in snapshot['trees']}
    def read_git(kind, sha):
        return snapshot['commit'] if kind == 'commit' else trees[sha]
    def read_file(path, head):
        return base64.b64decode(snapshot['files'][path], validate=True)
    result = execute_native(read_git,read_file,trusted_head=args.trusted_head,paths=list(snapshot['files']),test=args.test,execute=True)
    print(json.dumps(result,ensure_ascii=False))
    return result['exit_code'] or (0 if result['status']=='PROCESS_EXIT_ZERO' else 2)


if __name__ == '__main__':
    raise SystemExit(main())
