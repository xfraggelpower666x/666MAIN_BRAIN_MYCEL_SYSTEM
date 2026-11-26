"""R19.6 candidate: Git object membership gate for the existing execution bridge.
Trusted head must originate outside the untrusted bundle. Not an OS sandbox.
"""
import base64
import hashlib
import re

ROOT = 'PROJECTS/KAIRON/'
SHA = re.compile(r'[0-9a-f]{40}\Z')

def oid(kind, data):
    return hashlib.sha1(kind.encode() + b' ' + str(len(data)).encode() + b'\0' + data).hexdigest()

def verify_object(objects, key, kind):
    if not isinstance(key, str) or not SHA.fullmatch(key):
        raise ValueError('INVALID_OBJECT_ID')
    if key not in objects:
        raise ValueError('OBJECT_MISSING')
    raw = base64.b64decode(objects[key], validate=True)
    if oid(kind, raw) != key:
        raise ValueError('OBJECT_HASH_MISMATCH')
    return raw

def tree_entries(raw):
    entries = {}
    while raw:
        mode, sep, tail = raw.partition(b' ')
        name, end, rest = tail.partition(b'\0')
        if not sep or not end or len(rest) < 20 or not name or b'/' in name or name in (b'.', b'..') or name in entries:
            raise ValueError('INVALID_TREE')
        entries[name] = (mode, rest[:20].hex())
        raw = rest[20:]
    return entries

def verify_bundle(bundle, objects, *, trusted_head):
    if bundle.get('commit') != trusted_head:
        raise ValueError('HEAD_MISMATCH')
    if (bundle.get('system_id'), bundle.get('namespace'), bundle.get('scope')) != ('666TDI-001', 'KAIRON', ROOT):
        raise ValueError('FOREIGN_SCOPE')
    commit = verify_object(objects, trusted_head, 'commit')
    first = commit.split(b'\n', 1)[0]
    if not first.startswith(b'tree '):
        raise ValueError('INVALID_COMMIT')
    tree = first[5:].decode('ascii')
    verified = {}
    for entry in bundle['files']:
        path = entry['path']
        if not isinstance(path, str) or '\\' in path or ':' in path or any(p in ('', '.', '..') for p in path.split('/')):
            raise ValueError('INVALID_PATH')
        if path in verified:
            raise ValueError('DUPLICATE_PATH')
        parts = (ROOT + path).encode('utf-8').split(b'/')
        current = tree
        for i, part in enumerate(parts):
            records = tree_entries(verify_object(objects, current, 'tree'))
            if part not in records:
                raise ValueError('PATH_NOT_IN_COMMIT')
            mode, current = records[part]
            if i < len(parts)-1 and mode != b'40000':
                raise ValueError('NOT_DIRECTORY')
        if mode not in (b'100644', b'100755'):
            raise ValueError('NOT_REGULAR_FILE')
        data = base64.b64decode(''.join(entry['base64'].split()), validate=True)
        if current != entry['sha'] or oid('blob', data) != current:
            raise ValueError('BLOB_NOT_IN_COMMIT')
        verified[path] = current
    if not verified or bundle.get('test') not in verified:
        raise ValueError('TEST_NOT_BOUND')
    return {'commit': trusted_head, 'tree': tree, 'blobs': verified, 'status': 'COMMIT_TREE_BLOB_VERIFIED'}

def run_verified(bundle, objects, *, trusted_head):
    # Existing bridge remains the execution authority; no automatic dispatch.
    evidence = verify_bundle(bundle, objects, trusted_head=trusted_head)
    from execution_bridge import run
    result = run(bundle)
    return {**result, 'membership_evidence': evidence, 'production_release': False}
