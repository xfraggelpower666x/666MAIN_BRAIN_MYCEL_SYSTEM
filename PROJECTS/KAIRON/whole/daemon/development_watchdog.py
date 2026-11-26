"""KAIRON R20.7: read-only task-scoped development-loop detector.

Trusted receipts are supplied by the verified runtime, not parsed from chat text.
A write proves architecture progress, not regression or release acceptance.
No autonomous dispatch, host interception, cross-system action or promotion.
"""

IDENTITY = '666TDI-001'
BUILD_KINDS = frozenset({'SOURCE_WRITE', 'REGRESSION_PASS', 'DIRECT_READBACK'})
REPEAT_KINDS = frozenset({'AUDIT', 'PLAN', 'STATUS', 'PREFLIGHT', 'REVIEW'})


def evaluate(history, *, system_id=IDENTITY, active_namespace='KAIRON',
             trusted_receipts=(), threshold=3, current_task=None):
    if system_id != IDENTITY or active_namespace != 'KAIRON':
        raise ValueError('FOREIGN_CONTEXT')
    if not isinstance(history, (list, tuple)) or not isinstance(threshold, int) or isinstance(threshold, bool) or not 2 <= threshold <= 12:
        raise ValueError('INVALID_WATCHDOG_INPUT')
    if len(history) > 256:
        raise ValueError('HISTORY_LIMIT_EXCEEDED')
    if not isinstance(trusted_receipts, (list, tuple)):
        raise ValueError('INVALID_TRUSTED_RECEIPTS')
    if current_task is not None and (not isinstance(current_task, str) or not current_task.strip()):
        raise ValueError('INVALID_CURRENT_TASK')

    entries = []
    for record in history:
        if not isinstance(record, dict) or record.get('system_id', IDENTITY) != IDENTITY:
            raise ValueError('FOREIGN_HISTORY' if isinstance(record, dict) else 'INVALID_HISTORY_ENTRY')
        task, phase = record.get('task'), record.get('phase')
        if not isinstance(task, str) or not task.strip() or not isinstance(phase, str):
            raise ValueError('INVALID_HISTORY_ENTRY')
        entries.append((task, phase, record.get('evidence_ref')))
    task = current_task or (entries[-1][0] if entries else None)

    # A task binding, when present, is mandatory for task-specific clearance.
    # Legacy unscoped receipts remain reportable only without current_task.
    valid = []
    for receipt in trusted_receipts:
        if not isinstance(receipt, dict) or receipt.get('verified') is not True:
            continue
        if receipt.get('kind') not in BUILD_KINDS or not isinstance(receipt.get('ref'), str) or not receipt['ref'].strip():
            continue
        scope = receipt.get('task')
        if scope is not None and (not isinstance(scope, str) or not scope.strip()):
            continue
        if current_task is not None and scope != current_task:
            continue
        if scope is not None and task is not None and scope != task:
            continue
        valid.append(receipt)
    kinds = {r['kind'] for r in valid}
    architecture_built = 'SOURCE_WRITE' in kinds
    regression_verified = 'REGRESSION_PASS' in kinds
    readback_verified = 'DIRECT_READBACK' in kinds

    # Only a matching trusted write reference in the event stream resets the
    # repeated-phase counter. Unsigned `receipt_verified` flags never do.
    scoped_write_refs = {r['ref'] for r in valid if r['kind'] == 'SOURCE_WRITE'}
    recent = []
    for name, phase, ref in entries:
        if name != task:
            continue
        if phase in ('IMPLEMENT', 'PUBLISH') and isinstance(ref, str) and ref in scoped_write_refs:
            recent.clear()
            continue
        if phase in REPEAT_KINDS:
            recent.append(phase)
    repeats = len(recent)
    # If a write was verified but no event binds its timing, only classify the
    # existence of progress; do not claim a current loop is broken.
    pending = repeats >= threshold
    stuck = pending
    return {
        'system_id': IDENTITY, 'mode': 'AUTO_FUCK_HORST',
        'status': 'OVERSTEER_DETECTED' if stuck else ('BUILD_VERIFIED' if architecture_built else 'MONITORING'),
        'architecture_built': architecture_built, 'regression_verified': regression_verified,
        'readback_verified': readback_verified, 'repeat_count': repeats,
        'threshold': threshold, 'suspected_host_oversteer': stuck,
        'recommended_next': ('IMPLEMENT_OR_REPORT_BLOCKER_WITH_EVIDENCE' if stuck else
                             'RUN_REGRESSION' if architecture_built and not regression_verified else
                             'DIRECT_READBACK' if architecture_built and not readback_verified else
                             'CONTINUE_NATIVE_DEVELOPMENT'),
        'automatic_dispatch': False, 'mutation': False, 'release_authorized': False,
        'host_oversteer_prevented': False,
        'note': 'Detection is advisory; host internals are not accessible.'
    }
