"""666TDH: vollständige lokale Repo-Prüfung und restorable Git-Snapshot-ZIP.

Keine Provider-Mutation, keine fremde Authority, FSE Source Vault bleibt extern.
Python 3.10+ und für Backup Git for Windows erforderlich.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from zipfile import ZipFile

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NATIVE_PATH = 'PROJECTS/666TDH'


def _run(*argv: str, cwd: Path | None = None) -> str:
    result = subprocess.run(argv, cwd=cwd or PROJECT_ROOT, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for piece in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(piece)
    return h.hexdigest()


def verify() -> dict:
    sys.path.insert(0, str(PROJECT_ROOT))
    from tdh import Current, SYSTEM_ID

    current = Current(PROJECT_ROOT)
    result = current.execute('666TDH SYSTEMSTART')
    if current.pointer['system_id'] != SYSTEM_ID or current.pointer['authority'] != 'REPOSITORY_PROJECT':
        raise RuntimeError('Falsche native Authority')
    for branch, profile in current.registry['children'].items():
        run = current.execute(f'666TDH {branch} SYSTEMSTART')
        if run['target'] != profile['system_id'] or run['selected_branch'] != branch:
            raise RuntimeError('Subfacetten-Isolation verletzt: ' + branch)
    for verb in current.routes.get('daemon', []):
        d = current.execute(f'666TDH DAEMON {verb}')
        if d['daemon_operation']['authority'] != 'NONE' or d['daemon']['routing_authority'] != 'NONE':
            raise RuntimeError('Daemon-Authority verletzt: ' + verb)
    return {'status': 'VERIFIZIERT_LOCAL', 'native_release': current.pointer['release'],
            'current_manifest_count': result['files_verified'],
            'native_id': SYSTEM_ID, 'children': list(current.registry['children']),
            'daemon_commands': len(current.routes.get('daemon', [])),
            'chat_host_acceptance': 'OPEN_NOT_VERIFIED'}


def backup(output_dir: Path, *, verified: dict) -> dict:
    repo = Path(_run('git', 'rev-parse', '--show-toplevel')).resolve()
    if not PROJECT_ROOT.is_relative_to(repo):
        raise RuntimeError('TDH liegt außerhalb des Git-Repositorys')
    rel = PROJECT_ROOT.relative_to(repo).as_posix()
    if rel != NATIVE_PATH:
        raise RuntimeError('Falscher Zielpfad: ' + rel)
    if _run('git', 'status', '--porcelain', '--', rel, cwd=repo):
        raise RuntimeError('TDH Arbeitskopie enthält nicht eingecheckte Änderungen; Backup verweigert')
    commit = _run('git', 'rev-parse', 'HEAD', cwd=repo)
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise RuntimeError('Ungültiger Git-Commit')
    # Archive enthält den Git-HEAD, nicht zufällige Dateien aus dem Working Tree.
    if _run('git', 'show', 'HEAD:' + rel + '/CURRENT_POINTER.json', cwd=repo).strip() != \
            (PROJECT_ROOT / 'CURRENT_POINTER.json').read_text(encoding='utf-8').strip():
        raise RuntimeError('Checkout-Pointer und Git-HEAD stimmen nicht überein')
    target = output_dir.resolve()
    if target.is_relative_to(repo):
        raise RuntimeError('Systemsicherung darf nicht innerhalb des Git-Repositories liegen')
    target.mkdir(parents=True, exist_ok=True)
    # Keine vorhandene ZIP-Datei still überschreiben.
    filename = f'666TDH_FULL_REPO_{verified["native_release"]}_{commit[:12]}.zip'
    dest = target / filename
    manifest = dest.with_suffix('.manifest.json')
    if dest.exists() or manifest.exists():
        raise RuntimeError('Backup existiert bereits; nicht überschreiben: ' + str(dest))
    _run('git', 'archive', '--format=zip', '--output=' + str(dest), 'HEAD', rel, cwd=repo)
    try:
        expected = set(_run('git', 'ls-tree', '-r', '--name-only', 'HEAD', '--', rel, cwd=repo).splitlines())
        hashes = {}
        with ZipFile(dest) as z:
            actual = set(info.filename for info in z.infolist() if not info.is_dir())
            if expected != actual or z.testzip() is not None:
                raise RuntimeError('Backup-Dateien oder CRC stimmen nicht mit Git-HEAD überein')
            for item in sorted(actual):
                h = hashlib.sha256()
                with z.open(item) as stream:
                    for piece in iter(lambda: stream.read(1024*1024), b''):
                        h.update(piece)
                hashes[item] = h.hexdigest()
        # Repo-unabhängiger Original-Readback aus ZIP, kein fiktiver Provider-Upload.
        obj = {'status': 'LOCAL_ZIP_VERIFIED', 'native_system_id': verified['native_id'],
               'source_git_commit': commit, 'repository_scope': rel,
               'native_release': verified['native_release'], 'file_count': len(hashes),
               'zip_file': dest.name, 'zip_sha256': _sha_file(dest), 'file_sha256': hashes,
               'external_vault_not_included': True,
               'external_vault_role': 'SOURCE_VAULT_ONLY', 'github_provider_backup': 'SEPARATE_REQUIRED'}
        with manifest.open('x', encoding='utf-8') as stream:
            json.dump(obj, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        return {'status': obj['status'], 'git_commit': commit, 'zip': str(dest),
                'manifest': str(manifest), 'file_count': len(hashes),
                'zip_sha256': obj['zip_sha256'], 'external_vault_not_included': True}
    except Exception:
        # Ausschließlich den im aktuellen Lauf neu angelegten lokalen Backup-Kandidaten verwerfen.
        if dest.exists():
            dest.unlink()
        if manifest.exists():
            manifest.unlink()
        raise


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--backup-dir', type=Path, help='Vollständiges Git-Snapshot-ZIP außerhalb des Repositories erstellen')
    args = ap.parse_args()
    try:
        result = verify()
        if args.backup_dir is not None:
            result['backup'] = backup(args.backup_dir, verified=result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, KeyError, subprocess.CalledProcessError) as ex:
        print(json.dumps({'status': 'HOLD', 'error': str(ex)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
