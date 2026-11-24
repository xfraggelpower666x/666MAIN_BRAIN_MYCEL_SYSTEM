"""Additive migration of original R03 metadata and cyclic cover selection.
Preserves legacy/tool.ps1 and existing output naming contracts.
"""
import json
import random
from pathlib import Path

META_FIELDS=('artist','album','year','genre','comment','album_artist','composer','disc','track')
ORIGINAL_DEFAULTS={
 'artist':'xXXx_FRAGGLE_xXXx', 'album':'666SOUUNDsDESIGn 2026',
 'year':'2026','genre':'DARKTECHNO-PSYTRANCE',
 'comment':'xXXx_FRAGGLE_xXXx - FRAGGLEPOWER666 - 666SOUUNDsDESIGn 2026',
 'album_artist':'xXXx_FRAGGLE_xXXx','composer':'FRAGGLEPOWER666',
 'disc':'666','track':'666'
}
IMAGE_EXT={'.jpg','.jpeg','.png','.webp'}

def metadata_profile(job, original_profile=None):
    if not job.get('write_metadata'):
        return None
    profile=dict(ORIGINAL_DEFAULTS)
    if original_profile is not None:
        source=Path(original_profile)
        if source.is_file():
            values=json.loads(source.read_text(encoding='utf-8-sig'))
            if not isinstance(values,dict):
                raise ValueError('metadata.json must contain an object')
            profile.update({key:str(values[key]) for key in META_FIELDS if key in values and values[key] is not None})
    # Optional explicit job overrides are bounded to the known original tag fields.
    overrides=job.get('metadata',{})
    if overrides:
        if not isinstance(overrides,dict):raise ValueError('metadata must be an object')
        for key,value in overrides.items():
            if key not in META_FIELDS or not isinstance(value,str) or len(value)>1024:
                raise ValueError('Invalid metadata field')
            profile[key]=value
    return profile

def metadata_ffmpeg_args(profile,title):
    if profile is None:return []
    pairs={'title':title,'artist':profile['artist'],'album':profile['album'],
           'date':profile['year'],'genre':profile['genre'],'comment':profile['comment'],
           'album_artist':profile['album_artist'],'composer':profile['composer'],
           'disc':profile['disc'],'track':profile['track']}
    result=[]
    for k,v in pairs.items():result.extend(['-metadata',f'{k}={v}'])
    return result

class CoverRotation:
    def __init__(self, folder, seed=None):
        d=Path(folder)
        self._covers=sorted((p for p in d.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXT),key=lambda x:x.name.lower()) if d.is_dir() else []
        self._rng=random.Random(seed)
        self._idx=0
        self._rng.shuffle(self._covers)
    def next(self):
        if not self._covers:return None
        if self._idx>=len(self._covers):
            self._rng.shuffle(self._covers)
            self._idx=0
        result=self._covers[self._idx]
        self._idx+=1
        return result
