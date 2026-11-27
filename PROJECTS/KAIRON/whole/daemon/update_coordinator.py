"""R22 guarded post-update coordinator. No credentials, autonomous dispatch or pointer writes."""
import hashlib
import re
from pathlib import PurePosixPath

SYSTEM = '666TDI-001'
PLUGIN = 'plugins_6b07740c65d88191b08a593d460e6630'
REPO = 'xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM'
BRANCH = 'integration/kairon-r19-native-20261126'
TARGET = 'PROJECTS/KAIRON/live_plugin_backup/source/'
CHECKPOINT = 'PROJECTS/KAIRON/live_plugin_backup/BACKUP_CURRENT.json'
SHA = re.compile(r'[0-9a-f]{40}')
SECRET = re.compile(rb'(?i)(?:-----BEGIN [A-Z ]*PRIVATE KEY-----|(?:api[_-]?key|password|secret|token)\s*[:=]\s*["\x27][^"\x27\s]{12,}|gh[pousr]_[A-Za-z0-9]{20,}|sk-proj-[A-Za-z0-9_-]{20,})')


def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def inventory(files):
    if not isinstance(files, dict) or not files:
        raise ValueError('EMPTY_RELEASE')
    result = {}
    for path, data in files.items():
        if not isinstance(path, str) or not isinstance(data, bytes):
            raise ValueError('INVALID_FILE')
        if '\\' in path or ':' in path or any(x in ('', '.', '..') for x in path.split('/')):
            raise ValueError('INVALID_PATH')
        if not (path in ('plugin.json', '.codex-plugin/plugin.json') or
                re.fullmatch(r'skills/[a-z0-9-]+/SKILL\.md', path)):
            raise ValueError('UNREVIEWED_RELEASE_PATH')
        if SECRET.search(data):
            raise ValueError('POTENTIAL_SECRET')
        result[path] = blob(data)
    if not {'plugin.json', '.codex-plugin/plugin.json'} <= result.keys():
        raise ValueError('MISSING_MANIFEST')
    return result


def plan(*, native, desired_files, live, backup, target, paid_cost=0):
    """Read-only decision for the existing authorized UPDATE host."""
    if native.get('system_id') != SYSTEM or native.get('repository') != REPO or native.get('branch') != BRANCH:
        raise ValueError('FOREIGN_SCOPE')
    if not SHA.fullmatch(native.get('head', '')) or native.get('readback_verified') is not True:
        raise ValueError('NATIVE_READBACK_REQUIRED')
    if native.get('regression_passed') is not True or native.get('recovery_verified') is not True:
        raise ValueError('NATIVE_GATES_OPEN')
    if paid_cost != 0 or target.get('cost_limit') != 0:
        raise ValueError('COST_GATE')
    if (target.get('system_id'), target.get('repository'), target.get('branch'), target.get('path'), target.get('checkpoint'), target.get('authority'), target.get('plugin_id')) != (SYSTEM, REPO, BRANCH, TARGET, CHECKPOINT, False, PLUGIN):
        raise ValueError('TARGET_SCOPE')
    if live.get('plugin_id') != PLUGIN or not live.get('release_id'):
        raise ValueError('PLUGIN_IDENTITY')
    desired = inventory(desired_files)
    actual = inventory(live['files'])
    if set(actual) - set(desired):
        raise ValueError('DELETION_REQUIRES_APPROVAL')
    if backup.get('files') and set(backup['files']) - set(desired):
        raise ValueError('BACKUP_DELETION_REQUIRES_APPROVAL')
    changed = desired != actual
    synced = backup.get('files') == actual and backup.get('release_id') == live['release_id'] and backup.get('readback_verified') is True
    return {'system_id':SYSTEM, 'native_head':native['head'], 'expected_release_id':live['release_id'],
            'desired_files':desired, 'release_required':changed, 'backup_required':changed or not synced,
            'next_action':'RELEASE_CAS' if changed else ('BACKUP_CAS' if not synced else 'NO_CHANGE'),
            'automatic_dispatch':False, 'native_pointer_write':False}


def verify_release(plan_result, live, *, previous_release_id):
    if live.get('plugin_id') != PLUGIN or previous_release_id != plan_result['expected_release_id']:
        raise ValueError('RELEASE_CAS_MISMATCH')
    if not live.get('release_id') or inventory(live['files']) != plan_result['desired_files']:
        raise ValueError('RELEASE_READBACK_MISMATCH')
    if plan_result['release_required'] and live['release_id'] == previous_release_id:
        raise ValueError('RELEASE_NOT_ADVANCED')
    return {'release_id':live['release_id'], 'files':inventory(live['files']), 'verified':True}


def backup_entries(verified_release, live, *, expected_head, observed_head, recovery_verified):
    if recovery_verified is not True or not SHA.fullmatch(expected_head) or expected_head != observed_head:
        raise ValueError('BACKUP_CAS_OR_RECOVERY')
    if verified_release.get('verified') is not True or live.get('release_id') != verified_release['release_id'] or inventory(live['files']) != verified_release['files']:
        raise ValueError('BACKUP_SOURCE_MISMATCH')
    return {TARGET+path:data for path,data in live['files'].items()}


def verify_backup(verified_release, actual_files, checkpoint):
    if inventory(actual_files) != verified_release['files'] or checkpoint.get('files') != verified_release['files'] or checkpoint.get('release_id') != verified_release['release_id'] or checkpoint.get('authority') is not False:
        raise ValueError('BACKUP_READBACK_MISMATCH')
    return {'status':'BACKUP_VERIFIED','release_id':verified_release['release_id'],'native_pointer_write':False}
