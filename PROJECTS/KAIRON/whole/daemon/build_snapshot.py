"""Build the historical, pinned regression fixture from actual Git objects."""
import base64
import json
import subprocess
import sys
from pathlib import Path
from runtime_supervision import TESTED, FILES
from execution_trust import oid, tree_entries

def git(*args):
    return subprocess.check_output(['git', *args])

def build():
    raw = git('cat-file', 'commit', TESTED)
    if oid('commit', raw) != TESTED:
        raise ValueError('COMMIT_HASH_MISMATCH')
    fmt = '%T%x00%P%x00%an%x00%ae%x00%aI%x00%cn%x00%ce%x00%cI%x00%B'
    fields = git('show', '-s', '--format='+fmt, TESTED).decode().split('\0')
    tree, parents, an, ae, ad, cn, ce, cd, message = fields
    meta = dict(sha=TESTED, tree=tree, parents=parents.split(),
                author=dict(name=an,email=ae,date=ad),
                committer=dict(name=cn,email=ce,date=cd),
                message=message.rstrip('\n'), verification={'reason':'unsigned'})
    trees = {}
    files = {}
    for path in sorted(FILES):
        current = tree
        for part in ('PROJECTS/KAIRON/'+path).split('/'):
            if current not in trees:
                data = git('cat-file','tree',current)
                if oid('tree',data) != current:
                    raise ValueError('TREE_HASH_MISMATCH')
                entries = tree_entries(data)
                trees[current] = dict(sha=current,truncated=False,entries=[
                    [name.decode(),mode.decode(),sha] for name,(mode,sha) in entries.items()])
            current = next(e[2] for e in trees[current]['entries'] if e[0] == part)
        blob = git('cat-file','blob',current)
        if oid('blob',blob) != current:
            raise ValueError('BLOB_HASH_MISMATCH')
        files[path] = base64.b64encode(blob).decode()
    from connector_runtime import raw_commit
    raw_commit(meta, TESTED)
    return dict(commit=meta, trees=list(trees.values()), files=files)

if __name__ == '__main__':
    Path(sys.argv[1]).write_text(json.dumps(build()),encoding='utf-8')
