"""R02.8: verbindet frische Asset-Evidenz, externe Freigabe und Resume.
Keine automatische Rechtefreigabe. Originalmodule bleiben unverändert.
"""
import hashlib
from pathlib import Path
from asset_review import inspect
from publish_resume import approved, sources, transfer
from binary_readback import verify


def release(root, manifest, archives, matrix, approvals, expected_head, *, apply=False, **options):
    src = sources(root, manifest)
    allow = approved(manifest, approvals)
    if not allow.issubset(matrix):
        raise ValueError('Missing asset review')
    fresh = inspect(Path(root), manifest, archives, sorted(allow))
    for p in allow:
        old, now, permission = matrix[p], fresh[p], approvals[p]
        for key in ('sha','sha256','bytes','archive','member','kind','source_review'):
            if old.get(key) != now.get(key):
                raise ValueError('Stale review: '+p)
        if now['source_review'] != 'PASS' or permission.get('sha256') != now['sha256']:
            raise ValueError('Approval not bound to reviewed bytes: '+p)
        if now['kind']=='diagnostic' and (now.get('windows_path') or now.get('credential_pattern')):
            raise ValueError('Sensitive original log held: '+p)
        if hashlib.sha256(src[p].read_bytes()).hexdigest()!=now['sha256']:
            raise ValueError('Source changed: '+p)
    receipt = transfer(root,manifest,approvals,expected_head,apply=apply,**options)
    if receipt['published']:
        from publish_resume import REMOTE, TARGET
        rb=verify(options.get('remote',REMOTE),options.get('target',TARGET),receipt['commit'],manifest,receipt['selected'])
        for p,row in rb['files'].items():
            if row['sha256']!=fresh[p]['sha256']:
                raise RuntimeError('READBACK_PENDING: SHA256 mismatch')
        receipt['independent_readback']=rb
    return receipt
