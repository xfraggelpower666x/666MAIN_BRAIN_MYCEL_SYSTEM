"""R22.2 explicit post-update host adapter; connector callbacks are injected by the authorized host."""
from update_coordinator import (SYSTEM, PLUGIN, TARGET, CHECKPOINT, SHA,
                                inventory, plan, verify_release, backup_entries, verify_backup)


def run_post_update(host, *, native_head, desired_files, execute=False):
    """Called after native update readback, never from a menu or background job.
    Host must provide independent connector reads and scoped CAS writes.
    A retry reconciles observed release/source/checkpoint; no blind replay.
    """
    if execute is not True:
        raise ValueError('EXECUTION_APPROVAL_REQUIRED')
    native = host.read_native(native_head)
    if native.get('head') != native_head:
        raise ValueError('NATIVE_HEAD_DRIFT')
    target = host.read_target()
    live = host.read_plugin(PLUGIN)
    backup = host.read_backup()
    actual = inventory(backup['source_files']) if backup['source_files'] else {}
    checkpoint = backup.get('checkpoint') or {}
    prior = dict(files=actual, release_id=checkpoint.get('release_id'),
                 readback_verified=(checkpoint.get('files') == actual and
                                    checkpoint.get('authority') is False and
                                    checkpoint.get('status') == 'BACKUP_VERIFIED'))
    decision = plan(native=native, desired_files=desired_files, live=live,
                    backup=prior, target=target, paid_cost=host.additional_cost())
    if decision['release_required']:
        # Prepare recovery and upload only after exact release CAS is established.
        old = live['release_id']
        recovery = host.save_release_recovery(PLUGIN, old)
        if recovery.get('release_id') != old or recovery.get('verified') is not True:
            raise ValueError('RELEASE_RECOVERY_REQUIRED')
        if host.read_plugin(PLUGIN)['release_id'] != old:
            raise ValueError('RELEASE_CAS_CONFLICT')
        host.publish_plugin(PLUGIN, desired_files, expected_release_id=old)
        live = host.read_plugin(PLUGIN)
        verified = verify_release(decision, live, previous_release_id=old)
    else:
        verified = verify_release(decision, live, previous_release_id=live['release_id'])
    # Independently reconcile the backup after release; an earlier attempt may
    # already have published the source tree but not its checkpoint.
    backup = host.read_backup()
    head = backup['head']
    if not SHA.fullmatch(head):
        raise ValueError('INVALID_BACKUP_HEAD')
    actual = inventory(backup['source_files']) if backup['source_files'] else {}
    if set(actual) - set(verified['files']):
        raise ValueError('BACKUP_DELETION_REQUIRES_APPROVAL')
    checkpoint = backup.get('checkpoint') or {}
    if actual == verified['files'] and checkpoint.get('status') == 'BACKUP_VERIFIED':
        if checkpoint.get('files') == actual and checkpoint.get('release_id') == verified['release_id'] and checkpoint.get('authority') is False:
            return dict(verify_backup(verified, backup['source_files'], checkpoint),
                        result='NO_CHANGE', host_acceptance='UNATTESTED')
    recovery = host.save_backup_recovery(head)
    if recovery.get('head') != head or recovery.get('verified') is not True:
        raise ValueError('BACKUP_RECOVERY_REQUIRED')
    observed = host.read_backup()
    entries = backup_entries(verified, live, expected_head=head,
                             observed_head=observed['head'], recovery_verified=True)
    if actual != verified['files']:
        host.publish_backup_source(entries, expected_head=head)
    copied = host.read_backup()
    if inventory(copied['source_files']) != verified['files']:
        raise ValueError('BACKUP_SOURCE_READBACK_MISMATCH')
    if host.read_plugin(PLUGIN)['release_id'] != verified['release_id']:
        raise ValueError('RELEASE_DRIFT_BEFORE_CHECKPOINT')
    # Separate CAS transaction, only after the complete source readback.
    checkpoint = dict(schema='KAIRON_R22_BACKUP_CURRENT_V1', system_id=SYSTEM,
                      source_commit=native_head, backup_source_commit=copied['head'],
                      release_id=verified['release_id'], files=verified['files'],
                      file_count=len(verified['files']), authority=False,
                      status='BACKUP_VERIFIED', production_promotion=False)
    host.publish_checkpoint(CHECKPOINT, checkpoint, expected_head=copied['head'])
    final = host.read_backup()
    if final.get('checkpoint') != checkpoint:
        raise ValueError('CHECKPOINT_READBACK_MISMATCH')
    return dict(verify_backup(verified, final['source_files'], final['checkpoint']),
                result='SYNCHRONIZED', host_acceptance='UNATTESTED')
