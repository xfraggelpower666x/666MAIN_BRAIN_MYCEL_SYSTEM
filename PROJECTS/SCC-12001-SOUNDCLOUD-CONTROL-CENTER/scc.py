#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def sha256(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def git_blob_sha1(p:Path)->str:
    data=p.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()

def load_json(rel:str):
    return json.loads((ROOT/rel).read_text(encoding="utf-8"))

def verify_current():
    p=load_json("CURRENT_POINTER.json")
    if p["system_id"]!="SCC-12001": raise RuntimeError("system_id mismatch")
    for rel,expected in p["required_git_blobs"].items():
        fp=ROOT/rel
        if not fp.is_file(): raise RuntimeError(f"missing required file: {rel}")
        actual=git_blob_sha1(fp)
        if actual!=expected: raise RuntimeError(f"git-blob mismatch: {rel}")
    return p

def materialize():
    sys.path.insert(0,str(ROOT/"tools"))
    from materialize_source import materialize as _m
    return _m()

def main(argv):
    if len(argv)<2 or argv[0]!="SCC-12001":
        raise SystemExit("Use: python scc.py SCC-12001 <SYSTEMSTART|STATUS|HELP|WEITER|SOURCE>")
    route=" ".join(argv[1:]).upper()
    p=verify_current(); state=load_json("state/CURRENT_STATE.json"); handoff=load_json("continuity/CURRENT_HANDOFF.json")
    if route=="SYSTEMSTART":
        src=materialize()
        print(json.dumps({"system_id":"SCC-12001","status":"PARTIAL" if state["v1_3_2_device_runtime"].startswith("PENDING") else "READY","release":p["release"],"source_version":state["functional_source_version"],"source_path":str(src),"source_sha256":sha256(src),"return_anchor":handoff["return_anchor"],"device_runtime":state["v1_3_2_device_runtime"]},indent=2,ensure_ascii=False))
    elif route=="STATUS": print(json.dumps(state,indent=2,ensure_ascii=False))
    elif route=="HELP": print("SCC-12001 SYSTEMSTART | STATUS | HELP | WEITER | SOURCE | UPDATE | NEW CHAT | NEXT CHAT")
    elif route=="WEITER": print(json.dumps(handoff,indent=2,ensure_ascii=False))
    elif route=="SOURCE": print(materialize())
    elif route in {"NEW CHAT","NEXT CHAT"}: print(json.dumps({"bootstrap":"CURRENT_POINTER.json","handoff":handoff},indent=2,ensure_ascii=False))
    elif route=="UPDATE": print("Governed SCC update: rehydrate -> recovery -> audit -> change -> tests -> freeze -> CURRENT_POINTER last -> readback.")
    else: raise SystemExit(f"Unknown SCC route: {route}")

if __name__=="__main__": main(sys.argv[1:])
