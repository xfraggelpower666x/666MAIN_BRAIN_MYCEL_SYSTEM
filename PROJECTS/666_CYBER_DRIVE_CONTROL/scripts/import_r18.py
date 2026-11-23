#!/usr/bin/env python3
"""Controlled one-time migration of the original R18 source into native git working tree.

Never commits automatically. Supports an R18 source directory or ZIP. Only regular text
and binary source payloads are copied, no external commands are run or interpreted.
An existing destination is never overwritten. Produces SHA-256 inventory for review.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import shutil
import stat
import sys
import zipfile

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def members(source: pathlib.Path):
    if source.is_dir():
        for file in sorted(source.rglob("*")):
            if file.is_symlink():
                raise ValueError(f"Symlink forbidden: {file}")
            if file.is_file():
                yield file.relative_to(source).as_posix(), file.read_bytes()
    else:
        with zipfile.ZipFile(source) as z:
            for item in sorted(z.infolist(), key=lambda x: x.filename):
                if item.is_dir():
                    continue
                if stat.S_ISLNK((item.external_attr >> 16) & 0xffff):
                    raise ValueError(f"ZIP symlink forbidden: {item.filename}")
                if item.file_size > 16 * 1024 * 1024:
                    raise ValueError(f"Oversized entry: {item.filename}")
                yield item.filename, z.read(item)

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=pathlib.Path)
    parser.add_argument("--destination", type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parents[1] / "r18-legacy")
    parser.add_argument("--dry-run", action="store_true")
    args=parser.parse_args(argv)
    if not args.source.exists():
        parser.error("R18 source not found")
    if args.destination.exists() and (not args.destination.is_dir() or any(args.destination.iterdir())):
        parser.error("Destination exists and is non-empty; refusing to overwrite")
    entries=list(members(args.source))
    if not entries:
        parser.error("Empty source archive")
    # For R18 archive entry paths are already at project root.
    paths=set()
    clean=[]
    for name,data in entries:
        rel=pathlib.PurePosixPath(name)
        if rel.is_absolute() or ".." in rel.parts or name.startswith("/") or "\\" in name:
            raise ValueError(f"Unsafe ZIP path: {name}")
        if name in paths:
            raise ValueError(f"Duplicate ZIP path: {name}")
        paths.add(name)
        clean.append((name,data))
    inventory={"format":"r18-source-import.v1","source_file_count":len(clean),
        "files":{name:sha(data) for name,data in clean}}
    print(json.dumps({"count":len(clean),"destination":str(args.destination),
        "dry_run":args.dry_run},indent=2))
    if args.dry_run:
        return 0
    args.destination.mkdir(parents=True,exist_ok=True)
    for name,data in clean:
        target=args.destination.joinpath(*pathlib.PurePosixPath(name).parts)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
    (args.destination.parent / "docs" / "R18_IMPORT_SHA256.json").write_text(
        json.dumps(inventory,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("R18 source imported locally; REVIEW DIFF THEN git add/commit manually.")
    return 0

if __name__=="__main__":
    sys.exit(main())
