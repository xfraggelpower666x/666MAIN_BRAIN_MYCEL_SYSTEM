"""Unabhängige Byteprüfung über Git; kein Checkout und keine Schreiboperation."""
import argparse, hashlib, json, re, tempfile
from pathlib import Path
from publish_resume import git, blob, tree, remote_ref, PREFIX


def verify(remote, ref, expected_head, manifest, selected=None):
    if not re.fullmatch(r'[0-9a-f]{40}', expected_head):
        raise ValueError('Immutable commit SHA required')
    paths = sorted(manifest if selected is None else selected)
    if len(paths) != len(set(paths)) or any(p not in manifest for p in paths):
        raise ValueError('Unknown or duplicate path')
    with tempfile.TemporaryDirectory(prefix='r028-readback-') as d:
        git(d, 'init', '--bare', '--quiet')
        if remote_ref(d, remote, ref) != expected_head:
            raise ValueError('HEAD conflict before fetch')
        git(d, 'fetch', '--no-tags', remote, ref)
        if git(d, 'rev-parse', 'FETCH_HEAD').decode().strip() != expected_head:
            raise ValueError('Fetch conflict')
        entries = tree(d, expected_head)
        result = {}
        for p in paths:
            e = entries.get(PREFIX+p)
            if e is None or e[1:] != ('blob', manifest[p]) or e[0] not in ('100644','100755'):
                raise ValueError('Tree mismatch: '+p)
            data = git(d, 'cat-file', 'blob', e[2])
            if blob(data) != manifest[p]:
                raise ValueError('Byte mismatch: '+p)
            result[p] = dict(sha=blob(data),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
        if remote_ref(d, remote, ref) != expected_head:
            raise ValueError('HEAD conflict after fetch')
        return dict(status='BYTE_READBACK_VERIFIED',head=expected_head,files=result)

if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('remote'); p.add_argument('ref'); p.add_argument('head'); p.add_argument('manifest',type=Path); p.add_argument('--path',action='append'); a=p.parse_args()
    print(json.dumps(verify(a.remote,a.ref,a.head,json.loads(a.manifest.read_text(encoding='utf-8')),a.path),indent=2))
