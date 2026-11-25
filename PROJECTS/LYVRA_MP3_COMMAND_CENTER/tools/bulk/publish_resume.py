"""R02.6: additiver Resume-Transfer, ohne Checkout oder ZIP-Publikation."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile

BASE = 'c57167da1bcdc7de85fa2a6682232abb815fbc8d'
REMOTE = 'https://github.com/xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM.git'
SOURCE = 'refs/heads/integration/lyvra-mp3-r024'
TARGET = 'refs/heads/integration/lyvra-mp3-r025-bulk'
PREFIX = 'PROJECTS/LYVRA_MP3_COMMAND_CENTER/originals/'
HEX = re.compile(r'[0-9a-f]{40}\Z')


def git(repo, *args, data=None, env=None):
    p = subprocess.run(['git', '-C', str(repo), *args], input=data,
                       capture_output=True, env=env)
    if p.returncode:
        raise RuntimeError('Git-Befehl fehlgeschlagen: ' + args[0])
    return p.stdout


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def tree(repo, ref):
    out = {}
    for row in git(repo, 'ls-tree', '-rz', ref).split(b'\0'):
        if row:
            meta, path = row.split(b'\t', 1)
            out[path.decode()] = tuple(meta.decode().split())
    return out


def remote_ref(repo, remote, ref):
    rows = git(repo, 'ls-remote', '--refs', remote, ref).decode().splitlines()
    if not rows:
        return None
    if len(rows) != 1 or rows[0].split('\t')[1] != ref:
        raise ValueError('Mehrdeutiger Remote-Ref')
    return rows[0].split('\t')[0]


def sources(root, manifest):
    root = Path(root).resolve()
    result = {}
    for rel, sha in manifest.items():
        p = PurePosixPath(rel)
        if (p.is_absolute() or str(p) != rel or len(p.parts) < 2 or
            p.parts[0] not in ('mp3', 'dj', 'restore', 'boot') or
            any(x in ('.', '..') or '\\' in x or ':' in x for x in p.parts) or
            not HEX.fullmatch(sha) or p.suffix.lower() == '.zip'):
            raise ValueError('Ungültiger Manifestpfad: ' + rel)
        f = root.joinpath(*p.parts)
        if not f.is_file() or not f.resolve().is_relative_to(root) or any(
            x.is_symlink() for x in (f, *f.parents) if x != root and x.is_relative_to(root)):
            raise ValueError('Quelle fehlt oder Symlink: ' + rel)
        if f.stat().st_size >= 100 * 1024 * 1024 or blob(f.read_bytes()) != sha:
            raise ValueError('Größe oder SHA-Konflikt: ' + rel)
        result[rel] = f
    return result


def approved(manifest, approvals):
    """Freigaben sind externe, pfad- und SHA-gebundene Evidenz, keine Lizenzprüfung."""
    result = set()
    for rel, record in approvals.items():
        if (rel not in manifest or not isinstance(record, dict) or
            record.get('sha') != manifest[rel] or record.get('public_release') is not True or
            not all(isinstance(record.get(k), str) and record[k].strip()
                    for k in ('reviewer', 'evidence')) or
            record.get('privacy_review') != 'PASS' or record.get('rights_review') != 'PASS'):
            raise ValueError('Ungültige Einzelfreigabe: ' + rel)
        result.add(rel)
    return result


def original_entries(entries, manifest):
    found = {p[len(PREFIX):]: v for p, v in entries.items() if p.startswith(PREFIX)}
    if any(p not in manifest or v[1:] != ('blob', manifest[p]) for p, v in found.items()):
        raise ValueError('Originalkonflikt im Repository')
    return found


def transfer(root, manifest, approvals, expected_head, *, remote=REMOTE,
             base=BASE, source=SOURCE, target=TARGET,
             backup_prefix='refs/heads/backup/lyvra-mp3-resume-', apply=False):
    if not HEX.fullmatch(base) or (expected_head is not None and not HEX.fullmatch(expected_head)):
        raise ValueError('Ungültiger erwarteter SHA')
    if source == target or not all(x.startswith('refs/heads/') for x in (source, target, backup_prefix)):
        raise ValueError('Ungültiger Ref-Scope')
    src = sources(root, manifest)
    allow = approved(manifest, approvals)
    with tempfile.TemporaryDirectory(prefix='r026-') as d:
        repo = Path(d)
        git(repo, 'init', '--bare', '--quiet')
        if remote_ref(repo, remote, source) != base:
            raise ValueError('Quell-HEAD-Konflikt')
        if remote_ref(repo, remote, target) != expected_head:
            raise ValueError('Ziel-HEAD-Konflikt')
        git(repo, 'fetch', '--no-tags', remote, source)
        if git(repo, 'rev-parse', 'FETCH_HEAD').decode().strip() != base:
            raise ValueError('Quell-Fetch-Konflikt')
        head = expected_head or base
        if expected_head:
            git(repo, 'fetch', '--no-tags', remote, target)
            if git(repo, 'rev-parse', 'FETCH_HEAD').decode().strip() != head:
                raise ValueError('Ziel-Fetch-Konflikt')
            git(repo, 'merge-base', '--is-ancestor', base, head)
        baseline, old = tree(repo, base), tree(repo, head)
        if any(old.get(p) != v for p, v in baseline.items()):
            raise ValueError('Basisdatei verändert')
        existing = original_entries(old, manifest)
        missing = set(manifest) - set(existing)
        selected = sorted(missing & allow)
        receipt = dict(head=head, preserved=len(existing), selected=selected,
                       held=sorted(missing-allow), published=False, verified=len(existing))
        if not apply or not selected:
            return receipt
        backup = backup_prefix + head
        if backup in (source, target):
            raise ValueError('Backup-Ref-Konflikt')
        git(repo, 'read-tree', head)
        for rel in selected:
            data = src[rel].read_bytes()
            if blob(data) != manifest[rel]:
                raise ValueError('Quelle nach Prüfung verändert')
            sha = git(repo, 'hash-object', '-w', '--stdin', data=data).decode().strip()
            if sha != manifest[rel]:
                raise ValueError('Blob-Konflikt')
            git(repo, 'update-index', '--add', '--cacheinfo', '100644', sha, PREFIX+rel)
        candidate = git(repo, 'write-tree').decode().strip()
        new = tree(repo, candidate)
        if any(new.get(p) != v for p, v in old.items()) or set(new)-set(old) != {PREFIX+p for p in selected}:
            raise ValueError('Scope-Konflikt')
        final = original_entries(new, manifest)
        env = dict(os.environ, GIT_AUTHOR_NAME='LYVRA Source Recovery',
                   GIT_AUTHOR_EMAIL='source-recovery@users.noreply.github.com',
                   GIT_COMMITTER_NAME='LYVRA Source Recovery',
                   GIT_COMMITTER_EMAIL='source-recovery@users.noreply.github.com')
        commit = git(repo, 'commit-tree', candidate, '-p', head, '-m',
                     'R02.6: approved additive original transfer', env=env).decode().strip()
        if remote_ref(repo, remote, source) != base or remote_ref(repo, remote, target) != expected_head:
            raise ValueError('Concurrent Ref-Konflikt')
        b = remote_ref(repo, remote, backup)
        if b is None:
            git(repo, 'push', '--force-with-lease='+backup+':', remote, head+':'+backup)
        elif b != head:
            raise ValueError('Backup-Konflikt')
        if remote_ref(repo, remote, backup) != head:
            raise ValueError('Backup-Readback-Konflikt')
        if remote_ref(repo, remote, source) != base:
            raise ValueError('Quell-HEAD inzwischen verändert')
        git(repo, 'push', '--force-with-lease='+target+':'+(expected_head or ''), remote, commit+':'+target)
        # Unabhängiger Object Store; keine Wiederverwendung des lokalen Trees.
        with tempfile.TemporaryDirectory(prefix='r026-readback-') as rd:
            git(rd, 'init', '--bare', '--quiet')
            git(rd, 'fetch', '--no-tags', remote, target)
            if git(rd, 'rev-parse', 'FETCH_HEAD').decode().strip() != commit or tree(rd, commit) != new:
                raise RuntimeError('READBACK_PENDING: Tree')
            for rel, v in final.items():
                if blob(git(rd, 'cat-file', 'blob', v[2])) != manifest[rel]:
                    raise RuntimeError('READBACK_PENDING: Blob')
            if remote_ref(rd, remote, target) != commit:
                raise RuntimeError('READBACK_PENDING: HEAD')
        receipt.update(published=True, commit=commit, tree=candidate, backup=backup, verified=len(final))
        return receipt


def main():
    p = argparse.ArgumentParser()
    p.add_argument('originals', type=Path)
    p.add_argument('--manifest', type=Path, default=Path(__file__).with_name('original-manifest.json'))
    p.add_argument('--approvals', type=Path, required=True)
    p.add_argument('--expected-head', required=True, help='SHA oder ABSENT für Ersttransfer')
    p.add_argument('--apply', action='store_true')
    a = p.parse_args()
    m = json.loads(a.manifest.read_text(encoding='utf-8'))
    if len(m) != 308:
        raise SystemExit('308 Originaldateien erwartet')
    print(json.dumps(transfer(a.originals, m, json.loads(a.approvals.read_text(encoding='utf-8')),
                              None if a.expected_head == 'ABSENT' else a.expected_head, apply=a.apply), indent=2))


if __name__ == '__main__':
    main()
