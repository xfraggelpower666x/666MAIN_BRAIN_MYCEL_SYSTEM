"""Proof-oriented clear-source storage with project-local authority and immutable releases.

A manager is never an execution authority for registered foreign native systems.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA = 'mainbrain.klarcode.1'
PROJECT_ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_-]{1,63}$')
SOURCE_EXTENSIONS = {'.py','.js','.mjs','.cjs','.ts','.tsx','.jsx','.json','.md','.txt','.html','.css','.scss','.yaml','.yml','.toml','.sh','.bat','.ps1','.java','.cs','.cpp','.c','.h','.hpp','.go','.rs','.xml','.sql'}
BLOCK_NAMES = {'.env', '.npmrc', '.pypirc', 'id_rsa', 'id_ed25519', 'credentials.json', 'secrets.json', 'token.json', '.git', '__pycache__', 'node_modules', 'venv', '.venv'}
MAX_FILE_SIZE = 5 * 1024 * 1024


class GateError(RuntimeError):
    pass


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf8')


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write_exclusive(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())


def atomic_replace(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.incoming-', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def valid_project(value: str) -> str:
    if not PROJECT_ID.fullmatch(value):
        raise GateError('Invalid project ID')
    return value


def safe_relative(path: str) -> Path:
    p = PurePosixPath(path.replace('\\', '/'))
    if (p.is_absolute() or not p.parts or any(part in ('', '..', '.') for part in p.parts)
            or ':' in path or any(part in BLOCK_NAMES for part in p.parts)):
        raise GateError('Unsafe path: ' + path)
    return Path(*p.parts)


def read_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise GateError(f'Missing or symlinked file: {path}')
    try:
        obj = json.loads(path.read_text(encoding='utf8'))
    except (UnicodeError, ValueError) as exc:
        raise GateError(f'Invalid JSON {path}') from exc
    if not isinstance(obj, dict):
        raise GateError('Expected JSON object')
    return obj


def safe_subpath(base: Path, relative: str) -> Path:
    rel = safe_relative(relative)
    dest = base / rel
    if base.is_symlink() or dest.is_symlink() or any(p.is_symlink() for p in dest.parents if p != base.parent):
        raise GateError('Symlinked path is disallowed')
    if not dest.resolve().is_relative_to(base.resolve()):
        raise GateError('Path escape')
    return dest


@dataclass
class Manager:
    workspace: Path

    def __post_init__(self):
        self.workspace = self.workspace.resolve()
        self.projects = self.workspace / 'PROJECTS'
        self.registry_file = self.workspace / '.klarcode_control' / 'REGISTRY.json'

    def _registry(self) -> dict:
        if not self.registry_file.exists():
            return {'schema': SCHEMA, 'projects': {}}
        reg = read_json(self.registry_file)
        if reg.get('schema') != SCHEMA or not isinstance(reg.get('projects'), dict):
            raise GateError('Invalid manager registry')
        return reg

    def _save_registry(self, registry: dict, expected_sha: str | None) -> None:
        current = sha(self.registry_file.read_bytes()) if self.registry_file.exists() else None
        if current != expected_sha:
            raise GateError('Registry CAS conflict')
        atomic_replace(self.registry_file, canonical(registry))

    def register(self, project: str, owner: str, kind: str, *, root: str | None = None,
                 native_pointer: str | None = None) -> dict:
        valid_project(project)
        if not owner.strip() or kind not in ('LOCAL_MINI', 'NATIVE_DELEGATED'):
            raise GateError('Missing owner or invalid project kind')
        reg = self._registry()
        if project in reg['projects']:
            raise GateError('Already registered: no overwrite')
        reg_sha = sha(self.registry_file.read_bytes()) if self.registry_file.exists() else None
        relroot = f'PROJECTS/{project}' if root is None else str(safe_relative(root)).replace('\\','/')
        if not (relroot.startswith('PROJECTS/') and len(relroot.split('/')) == 2):
            raise GateError('Project root must be PROJECTS/<one-folder>')
        project_root = safe_subpath(self.workspace, relroot)
        # Native systems never receive a second manager-owned pointer.
        if kind == 'NATIVE_DELEGATED':
            if not native_pointer:
                raise GateError('Native pointer must be named for delegated registration')
            pointer = safe_subpath(project_root, native_pointer)
            if not pointer.is_file():
                raise GateError('Native authority proof missing')
            native_body = read_json(pointer)
            proof_owner = native_body.get('system_id') or native_body.get('owner')
            if proof_owner != owner:
                raise GateError('Native owner proof mismatch or absent')
            native_authority = native_body.get('authority')
            if isinstance(native_authority, dict) and native_authority.get('root') not in (None, relroot):
                raise GateError('Native pointer root does not match designated project path')
            psha = sha(pointer.read_bytes())
            record = {'owner': owner, 'kind': kind, 'root': relroot,
                      'native_pointer': native_pointer, 'observed_pointer_sha256': psha,
                      'write_policy': 'NATIVE_OWNER_ONLY'}
        else:
            if project_root.exists() and any(project_root.iterdir()):
                raise GateError('Cannot adopt nonempty project as new mini-system')
            if project_root.is_symlink():
                raise GateError('Project root symlink')
            project_root.mkdir(parents=True, exist_ok=True)
            pointer_path = project_root / 'CURRENT.json'
            if pointer_path.exists():
                raise GateError('Existing pointer')
            live = {'schema': SCHEMA + '.livecircle', 'project': project, 'owner': owner,
                    'return_anchor': 'INITIAL', 'next_step': 'REGISTER_FIRST_SOURCE_RELEASE',
                    'state': 'READY_FOR_FIRST_SAVE', 'created_at': utc()}
            live_bytes = canonical(live)
            write_exclusive(project_root / 'LIVECIRCLE.json', live_bytes)
            write_exclusive(project_root / 'REHYDRATION.md',
                            f'# {project} · Mini-LiveCircle\n\nOwner: {owner}\nRead CURRENT.json and verify the release manifest and LIVECIRCLE.json before execution.\n'.encode())
            pointer = {'schema': SCHEMA + '.current', 'project': project, 'owner': owner,
                       'current_release': None, 'livecircle_path': 'LIVECIRCLE.json', 'livecircle_sha256': sha(live_bytes),
                       'revision': 0, 'previous_pointer_sha256': None, 'created_at': utc()}
            # Initial Current is published last for this project.
            record = {'owner': owner, 'kind': kind, 'root': relroot,
                      'native_pointer': 'CURRENT.json', 'write_policy': 'LOCAL_MINI_ONLY'}
        reg['projects'][project] = record
        self._save_registry(reg, reg_sha)
        if kind == 'LOCAL_MINI':
            # Do not modify any managed file after the new project's Current.
            write_exclusive(pointer_path, canonical(pointer))
        return {'project': project, 'registered': True, 'record': record}

    def record(self, project: str) -> tuple[dict, Path]:
        valid_project(project)
        reg = self._registry()
        if project not in reg['projects']:
            raise GateError('Unregistered project')
        record = reg['projects'][project]
        root = safe_subpath(self.workspace, record['root'])
        if record['root'].split('/')[-1] != project and record['kind']=='LOCAL_MINI':
            raise GateError('Registry identity mismatch')
        return record, root

    def _verify_release(self, project: str, root: Path, pointer: dict) -> dict:
        release = pointer['current_release']
        if release is None:
            return {'files': 0, 'release': None, 'validated': True}
        if not re.fullmatch(r'[a-f0-9]{64}', release):
            raise GateError('Invalid release identity')
        release_dir = root / 'releases' / release
        manifest = read_json(release_dir / 'MANIFEST.json')
        if manifest.get('project') != project or manifest.get('release') != release:
            raise GateError('Release manifest identity mismatch')
        if sha(canonical(manifest)) != pointer.get('manifest_sha256'):
            raise GateError('Manifest fingerprint mismatch')
        files = manifest.get('files')
        if not isinstance(files, dict) or not files:
            raise GateError('Empty release manifest')
        for name, checksum in files.items():
            body = safe_subpath(release_dir / 'src', name)
            if not body.is_file() or sha(body.read_bytes()) != checksum:
                raise GateError('Missing or modified code: ' + name)
        return {'files': len(files), 'release': release, 'validated': True}

    def status(self, project: str) -> dict:
        record, root = self.record(project)
        pointer_path = root / record['native_pointer']
        pointer_bytes = pointer_path.read_bytes()
        if record['kind'] == 'NATIVE_DELEGATED':
            return {'project': project, 'owner': record['owner'], 'mode': 'NATIVE_DELEGATED',
                    'native_pointer_sha256': sha(pointer_bytes),
                    'changed_since_registration': sha(pointer_bytes) != record['observed_pointer_sha256'],
                    'authorization': 'READ_ONLY_HANDOFF_REQUIRED'}
        pointer = read_json(pointer_path)
        if pointer.get('project') != project or pointer.get('owner') != record['owner']:
            raise GateError('Authority/identity drift')
        livecircle_path = safe_subpath(root, pointer.get('livecircle_path', 'LIVECIRCLE.json'))
        if not livecircle_path.is_file() or sha(livecircle_path.read_bytes()) != pointer.get('livecircle_sha256'):
            raise GateError('LiveCircle drift; no silent promotion')
        check = self._verify_release(project, root, pointer)
        return {'project': project, 'owner': record['owner'], 'mode': record['kind'],
                'pointer_sha256': sha(pointer_bytes), 'revision': pointer['revision'],
                'livecircle': read_json(livecircle_path), **check}

    def save(self, project: str, source: Path, *, owner: str, expected_pointer: str) -> dict:
        record, root = self.record(project)
        if record['kind'] != 'LOCAL_MINI':
            raise GateError('Delegated native system: owner update trigger required')
        if owner != record['owner']:
            raise GateError('Owner mismatch')
        current = self.status(project)
        if current['pointer_sha256'] != expected_pointer:
            raise GateError('Stale pointer; CAS rejected')
        source = source.resolve()
        if not source.is_dir() or source == root or source.is_relative_to(root):
            raise GateError('Invalid source directory')
        originals: dict[str, bytes] = {}
        for file in sorted(source.rglob('*')):
            if file.is_symlink():
                raise GateError('Source symlink is not allowed')
            if file.is_dir():
                continue
            rel = file.relative_to(source).as_posix()
            safe_relative(rel)
            if file.suffix.lower() not in SOURCE_EXTENSIONS:
                raise GateError('Unsupported code file: ' + rel)
            if file.stat().st_size > MAX_FILE_SIZE:
                raise GateError('Oversized code file')
            originals[rel] = file.read_bytes()
        if not originals:
            raise GateError('No code files')
        hashes = {name: sha(data) for name, data in originals.items()}
        content_hash = sha(canonical(hashes))
        release_dir = root / 'releases' / content_hash
        if release_dir.exists():
            raise GateError('Identical release already exists (no duplicate write)')
        pointer_path = root / 'CURRENT.json'
        before_pointer = read_json(pointer_path)
        # First store immutable code and verify its full readback.
        release_dir.mkdir(parents=True, exist_ok=False)
        try:
            for name, data in originals.items():
                file = safe_subpath(release_dir / 'src', name)
                write_exclusive(file, data)
                if sha(file.read_bytes()) != hashes[name]:
                    raise GateError('Body readback mismatch')
            manifest = {'schema': SCHEMA + '.release', 'project': project,
                        'owner': owner, 'release': content_hash,
                        'source_hash_sha256': content_hash, 'files': hashes,
                        'created_at': utc()}
            manifest_bytes = canonical(manifest)
            write_exclusive(release_dir / 'MANIFEST.json', manifest_bytes)
            live = {'schema': SCHEMA + '.livecircle', 'project': project, 'owner': owner,
                    'return_anchor': f'RELEASE:{content_hash}',
                    'next_step': 'REHYDRATE_AND_CONTINUE_FROM_VERIFIED_RELEASE',
                    'state': 'SOURCE_SAVED_HOST_EXECUTION_NOT_VERIFIED',
                    'previous_pointer_sha256': expected_pointer,
                    'revision': before_pointer['revision'] + 1, 'created_at': utc()}
            live_bytes = canonical(live)
            write_exclusive(release_dir / 'LIVECIRCLE.json', live_bytes)
        except Exception:
            shutil.rmtree(release_dir)
            raise
        if sha(pointer_path.read_bytes()) != expected_pointer:
            raise GateError('Concurrent pointer move; candidate release quarantined')
        next_ptr = {**before_pointer, 'revision': before_pointer['revision'] + 1,
                    'current_release': content_hash, 'manifest_sha256': sha(manifest_bytes),
                    'livecircle_path': f'releases/{content_hash}/LIVECIRCLE.json',
                    'livecircle_sha256': sha(live_bytes),
                    'previous_pointer_sha256': expected_pointer, 'updated_at': utc()}
        # The pointer itself is the sole live authority; immutable releases are source evidence.
        atomic_replace(pointer_path, canonical(next_ptr))
        verified = self.status(project)
        if verified['release'] != content_hash or not verified['validated']:
            raise GateError('New pointer readback failed')
        return {'status': 'VERIFIED', 'project': project, 'release': content_hash,
                'files': len(originals), 'pointer_sha256': verified['pointer_sha256']}

    def handoff(self, project: str, *, desired_action: str) -> dict:
        record, root = self.record(project)
        if record['kind'] != 'NATIVE_DELEGATED':
            raise GateError('Only native delegates use handoffs')
        pointer = safe_subpath(root, record['native_pointer'])
        current = sha(pointer.read_bytes())
        return {'schema': SCHEMA + '.handoff', 'project': project, 'owner': record['owner'],
                'action': desired_action, 'path': record['root'], 'pointer': record['native_pointer'],
                'observed_pointer_sha256': current, 'write_authority': 'NATIVE_OWNER_ONLY',
                'status': 'PREPARED_NOT_DELIVERED'}

    def whole_delta(self, observed_head: str, current_head: str, *, whole_pointer_present: bool) -> dict:
        if not re.fullmatch(r'[a-f0-9]{40}', observed_head) or not re.fullmatch(r'[a-f0-9]{40}', current_head):
            raise GateError('Invalid Git HEAD')
        return {'schema': SCHEMA + '.whole-delta', 'observed_head': observed_head,
                'current_head': current_head, 'head_changed': observed_head != current_head,
                'main_brain_pointer_present': whole_pointer_present,
                'decision': 'READBACK_PENDING' if not whole_pointer_present else
                            ('REVALIDATION_REQUIRED' if observed_head != current_head else 'NO_CHANGE'),
                'auto_mutation': False, 'next_authority': '666 MAIN BRAIN UPDATE'}
