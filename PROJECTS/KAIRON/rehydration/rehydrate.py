#!/usr/bin/env python3
"""666TDI-001 repository-local rehydration gate. No foreign activation or writes."""
import hashlib, json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def load(path):
    return json.loads(path.read_text(encoding="utf-8"))
def digest(data):
    return hashlib.sha256(json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()
def inspect():
    faults=[]
    pointer_path=ROOT/"CURRENT_POINTER.json"
    pointer=load(pointer_path) if pointer_path.is_file() else None
    candidate=pointer is None
    if candidate:
        authority=load(ROOT/"governance/NATIVE_UPDATE_AUTHORITY.json")
        contract=load(ROOT/"whole/KAIRON_CONTRACT.json")
        if (authority.get("system_id")!="666TDI-001" or authority.get("namespace")!="KAIRON"
            or authority.get("allowed_path_prefix")!="PROJECTS/KAIRON/"
            or authority.get("production_promotion") is not False
            or contract.get("system_id")!="666TDI-001" or contract.get("status")!="STAGED_CANDIDATE"):
            faults.append("CANDIDATE_AUTHORITY_INVALID")
        pointer={"system_id":"666TDI-001","scope":"PROJECTS/KAIRON","namespace":"KAIRON","status":"WITHHELD"}
    if pointer.get("scope")!="PROJECTS/KAIRON" or pointer.get("namespace")!="KAIRON": faults.append("FOREIGN_ACTIVE_ROOT")
    circle=load(ROOT/"livecircle/CURRENT_STATE.json")
    triggers=load(ROOT/"triggers/TRIGGER_REGISTRY.json")
    character=load(ROOT/"identity/CHARACTER.json")
    for obj,label in [(pointer,"pointer"),(circle,"livecircle"),(triggers,"triggers"),(character,"character")]:
        if obj.get("system_id")!="666TDI-001":faults.append("IDENTITY_MISMATCH:"+label)
    if character.get("pronoun_de")!="er":faults.append("CHARACTER_PRONOUN_MISMATCH")
    if circle.get("foreign_repo_write_allowed") is not False: faults.append("LIVE_CIRCLE_SCOPE_VIOLATION")
    previous="GENESIS"
    for i,event in enumerate(circle.get("events",[]),1):
        raw={k:v for k,v in event.items() if k!="hash"}
        if event.get("seq")!=i or event.get("prev_hash")!=previous or event.get("hash")!=digest(raw):
            faults.append("LIVE_CIRCLE_CHAIN_INVALID:"+str(i))
        previous=event.get("hash")
    if circle.get("revision")!=len(circle.get("events",[])):faults.append("LIVE_CIRCLE_REVISION_MISMATCH")
    required=["README.md","engine/portable.py","engine/relational.py","engine/audio_feedback.py",
              "registry/triggers.json","runtime/livecircle.json","runtime/character.json","tests/test_audio_feedback.py"]
    manifest_path=ROOT/"transfer/SOURCE_MANIFEST.json"
    if not manifest_path.is_file():faults.append("SOURCE_MANIFEST_NOT_UPLOADED")
    else:
        manifest=load(manifest_path)
        source=ROOT/"source"
        if manifest.get("scope")!="PROJECTS/KAIRON/source" or manifest.get("system_id")!="666TDI-001":
            faults.append("MANIFEST_AUTHORITY_INVALID")
        # Compare tracked source files, not generated caches or local runtime outputs.
        import subprocess
        tracked=subprocess.check_output(["git","ls-files","-z","--","source"],cwd=ROOT).decode("utf-8").split("\0")
        actual={p.removeprefix("source/") for p in tracked if p}
        declared=set(manifest.get("source_files",{}))
        for name in sorted(actual-declared): faults.append("UNMANIFESTED_SOURCE:"+name)
        for name in sorted(declared-actual): faults.append("UNTRACKED_MANIFEST_SOURCE:"+name)
        for name,expected in manifest.get("source_files",{}).items():
            path=source/name
            if not path.is_file():faults.append("MISSING_SOURCE:"+name)
            elif hashlib.sha256(path.read_bytes()).hexdigest()!=expected:faults.append("SOURCE_SHA256_MISMATCH:"+name)
        if manifest.get("source_file_count")!=len(manifest.get("source_files",{})):
            faults.append("SOURCE_MANIFEST_COUNT_MISMATCH")
        for item in required:
            if not (source/item).is_file():faults.append("MISSING_REQUIRED_SOURCE:"+item)
    if not candidate and pointer.get("status")!="VERIFIZIERT_REPO_SOURCE":
        faults.append("POINTER_READBACK_PENDING")
    return {"system_id":"666TDI-001","status":("CANDIDATE_INTEGRITY_VERIFIED" if candidate else "VERIFIZIERT_REPO_SOURCE") if not faults else "READBACK_PENDING",
            "production_promotion":False if candidate else None, "candidate_only":candidate,
            "pointer_status":pointer.get("status"),"livecircle_revision":circle.get("revision"),
            "trigger_count":len(triggers.get("direct_chat_triggers",[])),"problems":faults}
if __name__=="__main__":
    try:
        result=inspect();print(json.dumps(result,ensure_ascii=False,indent=2))
        sys.exit(0 if not result["problems"] else 2)
    except Exception as exc:
        print(json.dumps({"system_id":"666TDI-001","status":"READBACK_PENDING","error":str(exc)},ensure_ascii=False))
        sys.exit(2)
