"""Track-local projection of native causal findings; no new inference authority."""
from copy import deepcopy


def attach(result, report, track_id):
    if (report.get('system_id') != '666TDI-001' or
            report.get('schema') != '666TDI_CREATIVE_CAUSAL_R10_V1' or
            report.get('track_id') != track_id):
        raise ValueError('CAUSAL_SCOPE_MISMATCH')
    accepted, review = [], []
    for item in report.get('emergences', []):
        entry = deepcopy(item)
        if (item.get('status') == 'CREATIVE_EMERGENCE_CANDIDATE'
                and not item.get('constraints') and item.get('evidence')
                and all(item['evidence'].get(k) for k in item.get('functions', []))):
            accepted.append(entry)
        else:
            review.append(entry)
    projection = {'source': report['schema'], 'candidates': accepted,
                  'counterevidence': review, 'collisions': deepcopy(report.get('collisions', [])),
                  'status': 'CREATOR_REVIEW_REQUIRED', 'automatic_promotion': False,
                  'audio_verified': False}
    result['causal_evidence'] = projection
    if result.get('preset_candidate') is not None:
        result['preset_candidate']['causal_evidence'] = deepcopy(projection)


# R21.3: explizite lokale, unveränderliche Preset-Versionen.
def read_versions(root, preset_id):
    import json
    import re
    from pathlib import Path
    from .music_memory import digest
    if not isinstance(preset_id,str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}',preset_id):
        raise ValueError('INVALID_PRESET_ID')
    directory=Path(root)/'presets'/preset_id
    if directory.is_symlink() or directory.parent.is_symlink():
        raise ValueError('PRESET_SYMLINK')
    rows=[]
    previous='GENESIS'
    for path in sorted(directory.glob('*.json')):
        if path.is_symlink():
            raise ValueError('PRESET_SYMLINK')
        row=json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(row,dict):
            raise ValueError('PRESET_INTEGRITY')
        version=len(rows)+1
        if (row.get('system_id')!='666TDI-001' or row.get('preset_id')!=preset_id
                or row.get('version')!=version or path.name!=f'{version:08d}.json'
                or row.get('previous_sha256')!=previous or row.get('sha256')!=digest(row)):
            raise ValueError('PRESET_INTEGRITY')
        rows.append(row)
        previous=row['sha256']
    return rows


def persist(root, preset_id, report, *, creator_approved=False, expected_version=0):
    """Lokaler expliziter Write; keine automatische Registrierung oder Promotion."""
    import json
    import os
    import tempfile
    from pathlib import Path
    from .music_memory import digest
    if creator_approved is not True:
        raise ValueError('CREATOR_APPROVAL_REQUIRED')
    if report.get('system_id')!='666TDI-001' or report.get('classification')!='PRESET_CANDIDATE':
        raise ValueError('INVALID_PRESET_REPORT')
    candidate=report.get('preset_candidate')
    if not isinstance(candidate,dict) or candidate.get('lyrics_embedded') is not False:
        raise ValueError('INVALID_PRESET_CANDIDATE')
    rows=read_versions(root,preset_id)
    if type(expected_version) is not int or len(rows)!=expected_version:
        raise ValueError('PRESET_VERSION_CONFLICT')
    # Nur funktionale Struktur speichern, keine historischen Textpassagen.
    bundles=candidate.get('functional_bundles')
    if not isinstance(bundles,list) or not bundles or not all(isinstance(x,str) for x in bundles):
        raise ValueError('INVALID_FUNCTIONAL_BUNDLES')
    row={'system_id':'666TDI-001','preset_id':preset_id,'version':len(rows)+1,
         'previous_sha256':rows[-1]['sha256'] if rows else 'GENESIS',
         'creator_approved':True,'automatic_promotion':False,
         'functional_bundles':list(bundles),
         'genre':candidate.get('genre'),'bpm':candidate.get('bpm'),
         'functional_relations':[{k:r.get(k) for k in ('relation','from','to')}
                                 for r in report.get('functional_relations',[])],
         'causal_ids':[r['id'] for r in report.get('causal_evidence',{}).get('candidates',[])],
         'lyrics_embedded':False}
    row['sha256']=digest(row)
    directory=Path(root)/'presets'/preset_id
    directory.mkdir(parents=True,exist_ok=True)
    target=directory/f"{row['version']:08d}.json"
    fd,tmp=tempfile.mkstemp(prefix='.pending-',dir=directory)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as handle:
            json.dump(row,handle,ensure_ascii=False,sort_keys=True)
            handle.flush()
            os.fsync(handle.fileno())
        # Hardlink publiziert atomar und überschreibt niemals eine vorhandene Version.
        try:
            os.link(tmp,target)
        except FileExistsError as exc:
            raise ValueError('PRESET_VERSION_CONFLICT') from exc
        except OSError as exc:
            # Fail closed on filesystems without atomic hardlink support.
            raise ValueError('PRESET_ATOMIC_PUBLICATION_UNAVAILABLE') from exc
    finally:
        os.unlink(tmp)
    verified=read_versions(root,preset_id)
    if len(verified)<row['version'] or verified[row['version']-1]!=row:
        raise ValueError('PRESET_READBACK_MISMATCH')
    return row
