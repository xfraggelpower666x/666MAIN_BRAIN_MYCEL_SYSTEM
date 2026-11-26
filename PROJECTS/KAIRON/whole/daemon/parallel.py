"""KAIRON R16: bounded parallel planning, not autonomous deployment."""
from itertools import combinations
from pathlib import PurePosixPath

MODES = ('MAXIMUM_PARALLEL', 'DEEP_EVOLUTION', 'REPAIR_REGRESSION',
         'CREATIVE_EXPLORATION', 'INTEGRATION_FREEZE')


def _scope(value):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value:
        raise ValueError('INVALID_SCOPE')
    p = PurePosixPath(value)
    if p.is_absolute() or any(x in ('', '.', '..') for x in value.split('/')):
        raise ValueError('INVALID_SCOPE')
    if p.parts[:2] != ('PROJECTS', 'KAIRON'):
        raise ValueError('FOREIGN_SCOPE')
    return p.parts


def _overlap(a, b):
    n = min(len(a), len(b))
    return a[:n] == b[:n]


def _conflict(a, b):
    return (a['barrier'] or b['barrier'] or
            any(_overlap(x, y) for x in a['writes'] for y in b['reads'] + b['writes']) or
            any(_overlap(x, y) for x in b['writes'] for y in a['reads']))


def plan(tasks, completed=(), max_exact=16):
    """Return dependency-safe waves; exact maximum width per wave up to max_exact.

    Completed IDs must come from caller-verified evidence. No action is executed.
    """
    if not isinstance(max_exact, int) or not 1 <= max_exact <= 20:
        raise ValueError('INVALID_EXACT_LIMIT')
    rows = {}
    for raw in tasks:
        key = raw['id']
        if not isinstance(key, str) or not key or key in rows:
            raise ValueError('INVALID_TASK_ID')
        if raw.get('mode') not in MODES[1:]:
            raise ValueError('INVALID_MODE')
        if not isinstance(raw.get('authorized'), bool):
            raise ValueError('AUTHORIZATION_REQUIRED')
        if not isinstance(raw.get('evidence_ref'), str) or not raw['evidence_ref'].strip():
            raise ValueError('EVIDENCE_REQUIRED')
        row = dict(raw)
        for name in ('reads', 'writes', 'depends_on'):
            if not isinstance(raw.get(name), (list, tuple)):
                raise ValueError('INVALID_TASK_SCOPE')
        row['reads'] = tuple(_scope(x) for x in raw['reads'])
        row['writes'] = tuple(_scope(x) for x in raw['writes'])
        if not row['reads'] and not row['writes']:
            raise ValueError('EMPTY_SCOPE')
        row['depends_on'] = set(raw['depends_on'])
        row['barrier'] = raw.get('barrier', False)
        if not isinstance(row['barrier'], bool):
            raise ValueError('INVALID_BARRIER')
        rows[key] = row
    done = set(completed)
    if any(k not in rows and k not in done for row in rows.values() for k in row['depends_on']):
        raise ValueError('UNKNOWN_DEPENDENCY')
    pending = set(rows) - done
    waves, blocked, exact = [], {}, True
    while pending:
        ready = sorted(k for k in pending if rows[k]['authorized'] and rows[k]['depends_on'] <= done)
        if not ready:
            for k in sorted(pending):
                blocked[k] = 'AUTHORIZATION_MISSING' if not rows[k]['authorized'] else 'DEPENDENCY_UNRESOLVED_OR_CYCLE'
            break
        def compatible(group):
            return all(not _conflict(rows[a], rows[b]) for a, b in combinations(group, 2))
        if len(ready) <= max_exact:
            wave = next(group for size in range(len(ready), 0, -1)
                        for group in combinations(ready, size) if compatible(group))
        else:
            exact = False
            picked = []
            for k in ready:
                if compatible(picked + [k]): picked.append(k)
            wave = tuple(picked)
        waves.append(list(wave))
        done.update(wave)
        pending.difference_update(wave)
    return {'status': 'PLAN_PARTIAL' if blocked else 'PLAN_READY', 'waves': waves,
            'blocked': blocked, 'exact_maximum_per_wave': exact,
            'alternatives': {m: [k for k in sorted(rows) if rows[k]['mode'] == m]
                             for m in MODES[1:]},
            'dispatch_performed': False, 'execution_verified': False}
