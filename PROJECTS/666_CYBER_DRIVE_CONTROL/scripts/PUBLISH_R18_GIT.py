#!/usr/bin/env python3
"""Publish the already imported original R18 source with scoped Git verification."""
import argparse
import hashlib
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = 'xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM'
BRANCH = '666MAIN_BRAIN'
SUBTREE = Path('PROJECTS/666_CYBER_DRIVE_CONTROL/r18-legacy')
SHA256 = '0364d38d1fe41492bad821e636d0c089be13ac0304a9fcf01761c79d4d2fce8b'

def git(checkout, *args):
    p = subprocess.run(['git', *args], cwd=checkout, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError(f'git {args[0]} failed: {p.stderr[:1200]}')
    return p.stdout.strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('original_zip', type=Path)
    parser.add_argument('--checkout', type=Path, default=Path.cwd())
    args = parser.parse_args()
    checkout = args.checkout.resolve(strict=True)
    source = args.original_zip.resolve(strict=True)
    if hashlib.sha256(source.read_bytes()).hexdigest() != SHA256:
        raise RuntimeError('Original R18 ZIP SHA256 mismatch')
    destination = checkout / SUBTREE
    if not destination.is_dir():
        raise RuntimeError('R18 subtree missing: import first')
    with zipfile.ZipFile(source) as z:
        inputs = {i.filename: hashlib.sha256(z.read(i)).hexdigest()
                  for i in z.infolist() if not i.is_dir()}
    if len(inputs) != 186:
        raise RuntimeError('Expected 186 original R18 files')
    found = {p.relative_to(destination).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in destination.rglob('*') if p.is_file()}
    if inputs != found:
        raise RuntimeError('R18 subtree differs from original ZIP; nothing published')
    if Path(git(checkout, 'rev-parse', '--show-toplevel')).resolve() != checkout:
        raise RuntimeError('Expected canonical checkout root')
    if git(checkout, 'branch', '--show-current') != BRANCH:
        raise RuntimeError('Wrong branch')
    if REPO not in git(checkout, 'remote', 'get-url', 'origin'):
        raise RuntimeError('Remote repository mismatch')
    if git(checkout, 'diff', '--cached', '--name-only'):
        raise RuntimeError('Other staged changes exist')
    head = git(checkout, 'rev-parse', 'HEAD')
    remote = git(checkout, 'ls-remote', '--heads', 'origin', BRANCH).split()
    if not remote or remote[0] != head:
        raise RuntimeError('Remote branch changed: fetch and reconcile first')
    git(checkout, 'add', '--', SUBTREE.as_posix())
    staged = git(checkout, 'diff', '--cached', '--name-only').splitlines()
    if len(staged) != 186 or any(not p.startswith(SUBTREE.as_posix() + '/') for p in staged):
        raise RuntimeError('Unexpected Git scope; manual review required')
    git(checkout, 'commit', '-m', 'feat(cyber-drive): import original 186-file R18 source')
    published = git(checkout, 'rev-parse', 'HEAD')
    git(checkout, 'push', 'origin', 'HEAD:refs/heads/' + BRANCH)
    remote = git(checkout, 'ls-remote', '--heads', 'origin', BRANCH).split()
    if not remote or remote[0] != published:
        raise RuntimeError('READBACK_PENDING: remote head did not match')
    print('VERIFIED R18 original sources: 186/186, GitHub HEAD', published)

if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, zipfile.BadZipFile) as e:
        print('PUBLISH_BLOCKED:', e, file=sys.stderr)
        sys.exit(1)
