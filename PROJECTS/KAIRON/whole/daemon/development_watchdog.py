"""KAIRON R20.6: read-only architecture progress and host-oversteer watchdog.

Classification is advisory. It never authorizes dispatch, writes or releases.
Only trusted receipts from the caller's verified execution channel count as
architecture construction; arbitrary progress descriptions do not.
"""
from collections import Counter

IDENTITY = '666TDI-001'
BUILD_KINDS = frozenset({'SOURCE_WRITE', 'REGRESSION_PASS', 'DIRECT_READBACK'})
REPEAT_KINDS = frozenset({'AUDIT', 'PLAN', 'STATUS', 'PREFLIGHT', 'REVIEW'})


def evaluate(history, *, system_id=IDENTITY, active_namespace='KAIRON',
             trusted_receipts=(), threshold=3, current_task=None):
    if system_id != IDENTITY or active_namespace != 'KAIRON':
        raise ValueError('FOREIGN_CONTEXT')
    if not isinstance(history, (list, tuple)) or not 2 <= threshold <= 12:
        raise ValueError('INVALID_WATCHDOG_INPUT')
    if len(history) > 256:
        raise ValueError('HISTORY_LIMIT_EXCEEDED')
    if not isinstance(trusted_receipts, (list, tuple)):
        raise ValueError('INVALID_TRUSTED_RECEIPTS')
    verified = tuple(r for r in trusted_receipts if isinstance(r, dict)
                     and r.get('verified') is True and r.get('kind') in BUILD_KINDS
                     and isinstance(r.get('ref'), str) and r['ref'].strip())
    kinds = {r['kind'] for r in verified}
    architecture_built = 'SOURCE_WRITE' in kinds
    regression_verified = 'REGRESSION_PASS' in kinds
    readback_verified = 'DIRECT_READBACK' in kinds
    tail = []
    for record in history:
        if not isinstance(record, dict):
            raise ValueError('INVALID_HISTORY_ENTRY')
        if record.get('system_id', IDENTITY) != IDENTITY:
            raise ValueError('FOREIGN_HISTORY')
        task = record.get('task')
        phase = record.get('phase')
        if not isinstance(task, str) or not task or not isinstance(phase, str):
            raise ValueError('INVALID_HISTORY_ENTRY')
        if current_task is not None and task != current_task:
            continue
        if phase in ('IMPLEMENT', 'TEST', 'PUBLISH') and record.get('receipt_verified') is True:
            # A claimed flag in chat history is not independent execution evidence.
            # Only the explicit trusted channel resets repetition analysis.
            if architecture_built and phase == 'IMPLEMENT':
                tail = []
                continue
        tail.append((task, phase))
    same = Counter(task for task, phase in tail if phase in REPEAT_KINDS)
    task = current_task or (tail[-1][0] if tail else None)
    repeated = sum(1 for t, phase in tail if t == task and phase in REPEAT_KINDS) >= threshold if task else False
    # A verified write is progress, even if its regression/readback is still open.
    stuck = repeated and not architecture_built
    return {
        'system_id': IDENTITY, 'mode': 'AUTO_FUCK_HORST',
        'status': 'OVERSTEER_DETECTED' if stuck else ('BUILD_VERIFIED' if architecture_built else 'MONITORING'),
        'architecture_built': architecture_built,
        'regression_verified': regression_verified,
        'readback_verified': readback_verified,
        'repeat_count': sum(1 for t, phase in tail if t == task and phase in REPEAT_KINDS) if task else 0,
        'threshold': threshold,
        'suspected_host_oversteer': stuck,
        'recommended_next': ('IMPLEMENT_OR_REPORT_BLOCKER_WITH_EVIDENCE' if stuck else
                             'RUN_REGRESSION' if architecture_built and not regression_verified else
                             'DIRECT_READBACK' if architecture_built and not readback_verified else
                             'CONTINUE_NATIVE_DEVELOPMENT'),
        'automatic_dispatch': False, 'mutation': False,
        'release_authorized': False, 'host_oversteer_prevented': False,
        'note': 'Detection and guidance only; no access to host internals.'
    }
