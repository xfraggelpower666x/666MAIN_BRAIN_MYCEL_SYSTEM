#!/usr/bin/env python3
"""Verify and import the exact R18 source archive into this Git worktree.
Does not overwrite existing sources or touch other projects. Publish via reviewed git.
"""
from pathlib import Path, PurePosixPath
import argparse, hashlib, os, subprocess, sys, tempfile, zipfile

SHA="0364d38d1fe41492bad821e636d0c089be13ac0304a9fcf01761c79d4d2fce8b"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("archive",type=Path)
    ap.add_argument("--dry-run",action="store_true")
    args=ap.parse_args()
    p=args.archive.resolve(strict=True)
    if hashlib.sha256(p.read_bytes()).hexdigest()!=SHA: raise ValueError("R18 ZIP SHA mismatch")
    with zipfile.ZipFile(p) as z:
        files=[i for i in z.infolist() if not i.is_dir()]
        if len(files)!=186: raise ValueError("Expected 186 source files")
        entries=[]
        seen=set()
        for i in files:
            rel=PurePosixPath(i.filename)
            if (rel.is_absolute() or ".." in rel.parts or "\\" in i.filename or
                i.filename in seen or i.file_size>16*1024*1024 or
                ((i.external_attr>>16)&0o170000)==0o120000):
                raise ValueError("Unsafe archive entry: "+i.filename)
            seen.add(i.filename)
            entries.append((rel,z.read(i)))
    with tempfile.TemporaryDirectory() as t:
        temp=Path(t)/"source"
        temp.mkdir()
        for rel,data in entries:
            target=temp.joinpath(*rel.parts)
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(data)
        env={**os.environ,"PYTHONPATH":str(temp/"src")}
        done=subprocess.run([sys.executable,"-m","pytest","-q","tests"],cwd=temp,env=env,capture_output=True,text=True)
        print(done.stdout)
        if done.returncode or "288 passed" not in done.stdout: raise RuntimeError("Regression gate failed: "+done.stderr)
        if args.dry_run:
            print("DRY_RUN VERIFIED: 186 files / 288 tests.")
            return
        repo=Path(__file__).resolve().parents[2]
        destination=Path(__file__).resolve().parents[1]/"r18-legacy"
        if destination.exists(): raise RuntimeError("Destination exists: will not overwrite")
        if not (repo/".git").exists(): raise RuntimeError("Not a Git checkout at expected repository root: "+str(repo))
        import shutil
        shutil.copytree(temp,destination,ignore=shutil.ignore_patterns('__pycache__','.pytest_cache','*.pyc'))
        for rel,data in entries:
            if hashlib.sha256(destination.joinpath(*rel.parts).read_bytes()).digest()!=hashlib.sha256(data).digest():
                raise RuntimeError("Copy hash mismatch")
        print("Imported 186 files LOCALLY. Git publication and direct readback still required.")
        print("git add PROJECTS/666_CYBER_DRIVE_CONTROL/r18-legacy")
        print("git commit -m \"feat(cyber-drive): import verified R18 original source\"")
        print("git push origin HEAD:refs/heads/666MAIN_BRAIN")

if __name__=="__main__":
    try: main()
    except Exception as e: print("IMPORT_BLOCKED:",e,file=sys.stderr);sys.exit(1)
