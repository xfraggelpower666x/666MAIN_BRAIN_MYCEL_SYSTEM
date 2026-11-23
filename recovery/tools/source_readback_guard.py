#!/usr/bin/env python3
"""Read-only strict release preflight: full content, hashes, ZIP path security, exclusions.

No source mutation, no automatic execution of archived code, no freeze marking.
"""
import argparse
import hashlib
import json
import pathlib
import re
import stat
import sys
import zipfile
from collections import Counter

IMAGE_AUDIO_DOC_EXT = {'.pdf','.docx','.doc','.pptx','.xlsx','.jpg','.jpeg','.png','.gif','.webp','.svg','.mp3','.wav','.flac','.ogg','.aiff','.mp4','.mov','.pyc'}
FORBIDDEN_PARTS = {'__pycache__','.git','node_modules','output','rendered','contact_sheets','screenshots','archive','archives','.cache','.pytest_cache','tmp','temp'}
MAX_ZIP_MEMBERS=20000
MAX_TOTAL_UNCOMPRESSED=2*1024*1024*1024
MAX_MEMBER_UNCOMPRESSED=256*1024*1024
MAX_COMPRESSION_RATIO=2000


def parse_hashes(path):
    mapping={}
    for no,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
        if not line.strip(): continue
        m=re.fullmatch(r'([a-fA-F0-9]{64})  (.+)',line)
        if not m: raise ValueError(f'Invalid hash manifest at line {no}')
        digest, rel=m.group(1).lower(),m.group(2)
        if rel in mapping: raise ValueError(f'Duplicate manifest path: {rel}')
        if invalid_path(rel): raise ValueError(f'Unsafe manifest path: {rel}')
        mapping[rel]=digest
    return mapping


def invalid_path(name):
    x=name.replace('\\','/')
    p=pathlib.PurePosixPath(x)
    return x.startswith('/') or re.match(r'^[a-zA-Z]:',x) is not None or any(y in ('..','.','') for y in p.parts) or '\\' in name or chr(0) in name


def forbidden(name):
    p=pathlib.PurePosixPath(name)
    if any(x.lower() in FORBIDDEN_PARTS for x in p.parts):return True
    if p.suffix.lower() in IMAGE_AUDIO_DOC_EXT:return True
    if re.search(r'(^|[/_-])(search[-_]?history|chat[-_]?history|capture[-_]?register|generated[-_]?lyrics)([/_.-]|$)',name,re.I):return True
    return False


def verify_expected(expected, files, errors):
    missing=sorted(set(expected)-set(files))
    extra=sorted(set(files)-set(expected))
    mismatched=sorted(p for p in set(expected)&set(files) if expected[p]!=files[p])
    errors.extend(f'missing:{x}' for x in missing)
    errors.extend(f'unexpected:{x}' for x in extra)
    errors.extend(f'checksum_mismatch:{x}' for x in mismatched)
    return dict(missing=missing, unexpected=extra, mismatched=mismatched)


def inspect_directory(root):
    if not root.is_dir():raise ValueError(f'Not a directory: {root}')
    files={}; errors=[]
    for path in sorted(root.rglob('*')):
        rel=path.relative_to(root).as_posix()
        if path.is_symlink():errors.append(f'symlink:{rel}');continue
        if not path.is_file():continue
        if invalid_path(rel):errors.append(f'unsafe_path:{rel}');continue
        if forbidden(rel):errors.append(f'forbidden_artifact:{rel}')
        with path.open('rb') as stream:
            h=hashlib.sha256()
            for part in iter(lambda:stream.read(1024*1024),b''):h.update(part)
        files[rel]=h.hexdigest()
    return files,errors


def inspect_zip(path, expected):
    if not path.is_file():raise ValueError(f'Not a ZIP: {path}')
    hashes={}; errors=[]; raw_members=[]; size_sum=0
    with zipfile.ZipFile(path) as z:
        infos=z.infolist()
        if len(infos)>MAX_ZIP_MEMBERS:errors.append('too_many_zip_members')
        for info in infos:
            member=info.filename
            if member.endswith('/'):continue
            if invalid_path(member):errors.append(f'unsafe_member:{member}');continue
            raw_members.append(member)
            if info.file_size>MAX_MEMBER_UNCOMPRESSED:errors.append(f'oversized_member:{member}')
            size_sum+=info.file_size
            if info.file_size>0 and info.file_size/max(info.compress_size,1)>MAX_COMPRESSION_RATIO:
                errors.append(f'compression_bomb_risk:{member}')
            mode=(info.external_attr >> 16)
            if stat.S_ISLNK(mode):errors.append(f'symlink_member:{member}');continue
        if size_sum>MAX_TOTAL_UNCOMPRESSED:errors.append('too_much_uncompressed_data')
        duplicates=[x for x,c in Counter(raw_members).items() if c>1]
        errors.extend(f'duplicate_member:{x}' for x in duplicates)
        # Archives can contain exactly one top-level project folder.
        prefix=''
        names=set(raw_members)
        if set(expected)!=names:
            candidate={x.split('/',1)[0] for x in names if '/' in x}
            if len(candidate)==1:
                candidate_prefix=next(iter(candidate))+'/'
                trimmed={x[len(candidate_prefix):] for x in names if x.startswith(candidate_prefix)}
                if set(expected)==trimmed:prefix=candidate_prefix
        for info in infos:
            name=info.filename
            if name.endswith('/') or name not in raw_members:continue
            if any(name==x for x in duplicates):continue
            rel=name[len(prefix):] if name.startswith(prefix) else name
            if invalid_path(rel):errors.append(f'unsafe_path:{name}');continue
            if forbidden(rel):errors.append(f'forbidden_artifact:{rel}')
            if info.file_size>MAX_MEMBER_UNCOMPRESSED or size_sum>MAX_TOTAL_UNCOMPRESSED:continue
            h=hashlib.sha256()
            with z.open(info) as stream:
                for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
            hashes[rel]=h.hexdigest()
    return hashes,errors


def verify(source, sha_path):
    expected=parse_hashes(sha_path)
    if source.is_dir():actual,errors=inspect_directory(source)
    elif source.is_file():actual,errors=inspect_zip(source,expected)
    else:raise ValueError('Source is missing')
    diffs=verify_expected(expected,actual,errors)
    required={
        'package.json','system/bootstrap-loader.js','system/config/system-manifest.js',
        'system/core/audit-engine.js','tests/run-tests.js',
        'tools/stem_masking_analyzer.py','tools/sonification_audio_pipeline.py'
    }
    for p in sorted(required):
        if p not in actual:errors.append(f'missing_required:{p}')
    return {'status':'VERIFIED_SOURCE_ONLY' if not errors else 'READBACK_PENDING',
            'source':str(source),'expected':len(expected),'present':len(actual),
            'verified':sum(1 for x in actual if x in expected and actual[x]==expected[x]),
            'diffs':diffs,'errors':errors,
            'note':'Even a byte-perfect source check is not an executed test or an authorized Freeze.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=pathlib.Path,required=True)
    parser.add_argument('--sha-manifest',type=pathlib.Path,required=True)
    parser.add_argument('--report',type=pathlib.Path)
    args=parser.parse_args()
    try:r=verify(args.source,args.sha_manifest)
    except Exception as exc:
        r={'status':'BLOCKIERT','errors':[f'{type(exc).__name__}:{exc}']}
    output=json.dumps(r,indent=2,ensure_ascii=False)+'\n'
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(output,encoding='utf-8')
    print(output)
    return 0 if r['status']=='VERIFIED_SOURCE_ONLY' else 2

if __name__=='__main__':sys.exit(main())
