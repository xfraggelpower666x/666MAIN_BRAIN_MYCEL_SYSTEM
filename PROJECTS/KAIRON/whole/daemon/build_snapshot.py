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
    # Read exact original headers/message instead of git show formatting.
    headers, message = raw.split(b'\n\n', 1)
    lines = headers.decode('utf-8').split('\n')
    tree = lines[0].split(' ', 1)[1]
    parents = [line[7:] for line in lines if line.startswith('parent ')]
    from datetime import datetime, timezone
    def identity(kind):
        line = next(x for x in lines if x.startswith(kind+' '))[len(kind)+1:]
        person, stamp, zone = line.rsplit(' ', 2)
        name, email = person.rsplit(' <', 1)
        return dict(name=name,email=email[:-1],date=datetime.fromtimestamp(int(stamp),timezone.utc).isoformat())
    # raw_commit tries both no suffix and one newline. Preserve all other bytes.
    body = message.decode('utf-8')
    meta = dict(sha=TESTED, tree=tree, parents=parents,
                author=identity('author'), committer=identity('committer'),
                message=body[:-1] if body.endswith('\n') else body,
                verification={'reason':'unsigned'})
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
