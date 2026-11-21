"""R5.5 offline source relocation proposal. Read-only; never edits checkpoints or ZIPs."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

SCHEMA = '666.chatbackup.source-relocation.v1'
CHECKPOINT_SCHEMA = '666.chatbackup.batch-checkpoint.v1'
MAX_FILES = 10000

class RelocationError(ValueError):
    pass

def _digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def propose_relocations(folder: str | Path, checkpoint: str | Path, *, recursive: bool = True) -> dict:
    """Match missing checkpoint entries to present ZIPs by SHA-256, never by name.

    Ambiguous matches are not auto-selected. Symlinks are not followed.
    Returns only suggestions; calling this never mutates the source or checkpoint.
    """
    base = Path(folder).resolve()
    if not base.is_dir():
        raise RelocationError('Source directory does not exist')
    state = json.loads(Path(checkpoint).read_text(encoding='utf-8'))
    entries = state.get('completed') if isinstance(state, dict) and state.get('schema') == CHECKPOINT_SCHEMA else None
    if not isinstance(entries, dict) or len(entries) > MAX_FILES:
        raise RelocationError('Invalid or oversized checkpoint')
    for name, digest in entries.items():
        if (not isinstance(name, str) or not name or '\\' in name or
            Path(name).is_absolute() or '..' in Path(name).parts or
            not name.lower().endswith('.zip') or not isinstance(digest, str) or
            len(digest) != 64 or any(ch not in '0123456789abcdefABCDEF' for ch in digest)):
            raise RelocationError('Invalid checkpoint path or SHA-256')
    paths = base.rglob('*') if recursive else base.iterdir()
    candidates = []
    for path in paths:
        if path.is_symlink() or not path.is_file() or path.suffix.lower() != '.zip':
            continue
        if not path.resolve().is_relative_to(base):
            continue
        candidates.append(path)
        if len(candidates) > MAX_FILES:
            raise RelocationError('Source inventory too large')
    by_hash: dict[str, list[str]] = {}
    current: dict[str, str] = {}
    for path in sorted(candidates):
        rel = path.relative_to(base).as_posix()
        digest = _digest(path)
        current[rel] = digest
        by_hash.setdefault(digest, []).append(rel)
    results = []
    for name, digest in sorted(entries.items()):
        digest = digest.lower()
        if current.get(name) == digest:
            status, matches = 'VERIFIED', [name]
        elif name in current:
            status, matches = 'CHANGED', []
        else:
            matches = by_hash.get(digest, [])
            status = 'RELOCATED_CANDIDATE' if len(matches) == 1 else ('AMBIGUOUS' if matches else 'MISSING')
        results.append({'source': name, 'status': status, 'candidates': matches})
    return {'schema': SCHEMA, 'status': 'VERIFIED' if all(row['status'] == 'VERIFIED' for row in results) else 'PARTIAL',
            'sources': results, 'originals_modified': False, 'checkpoint_modified': False}

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='Read-only R5.5 ZIP source relocation suggestions')
    p.add_argument('folder', type=Path)
    p.add_argument('checkpoint', type=Path)
    p.add_argument('--flat', action='store_true', help='Scan only the top-level folder')
    args = p.parse_args()
    print(json.dumps(propose_relocations(args.folder, args.checkpoint, recursive=not args.flat), indent=2))
