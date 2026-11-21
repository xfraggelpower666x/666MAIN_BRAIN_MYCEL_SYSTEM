"""666CLS repository-native reconstruction contract adapter R01.
No model execution, no repository writes, no foreign native activation.
This module deliberately does not replace cls_facet_runtime or framework_intake.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_FILE = ROOT / "contracts" / "RECONSTRUCTION_PROFILES_R01.json"
ALLOWED_SOURCE_TYPES = {"LYRICS","PROSE","STORY","MIXED","SYSTEM_CONFIG","UNCLEAR"}
ALLOWED_LANGUAGES = {"de","en"}
RESULT_SCHEMA = "cls.reconstruction.result.v0.1"

def profiles():
    data = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
    assert data["schema"] == "cls.reconstruction.profiles.v0.1"
    return data["profiles"]

def _hold(request_id, reason, profile_id=None):
    return {"schema":RESULT_SCHEMA,"request_id":request_id,"status":"HOLD",
            "selected_profile":profile_id,"execution_performed":False,
            "result_ref":None,"plan":None,"unresolved":[reason],"mutations":[],
            "audit":{"foreign_execution":"BLOCKED","source_fidelity":"NOT_TESTED",
                     "provenance":"OPEN"}}

def plan(request):
    """Prepare a deterministic request plan only; never transform or submit source text."""
    if not isinstance(request,dict):
        return _hold("unspecified","INVALID_REQUEST")
    rid=request.get("request_id","unspecified")
    if not isinstance(rid,str) or not (1 <= len(rid) <= 128):
        return _hold("unspecified","INVALID_REQUEST_ID")
    target=request.get("target") or {}
    pid=target.get("profile_id")
    known=profiles()
    if not isinstance(pid,str) or pid not in known:
        return _hold(rid,"PROFILE_MISSING_OR_UNKNOWN",pid)
    profile=known[pid]
    if target.get("profile_version")!=profile["version"]:
        return _hold(rid,"PROFILE_VERSION_MISMATCH",pid)
    operation=target.get("operation")
    if operation not in profile["operations"]:
        return _hold(rid,"OPERATION_NOT_PERMITTED",pid)
    authority=request.get("authority") or {}
    execution=request.get("execution") or {}
    if (authority.get("cls_system_id")!="666CLS-CORE-001"
        or authority.get("foreign_execution") is not False
        or execution.get("mode")!="DRY_RUN"
        or execution.get("approved_by_native_owner") is not False):
        return _hold(rid,"NATIVE_AUTHORITY_OR_EXECUTION_FENCE",pid)
    source=request.get("sources")
    if not isinstance(source,list) or not 1<=len(source)<=16:
        return _hold(rid,"INVALID_SOURCE_COUNT",pid)
    ids=set()
    for item in source:
        if not isinstance(item,dict):
            return _hold(rid,"INVALID_SOURCE",pid)
        sid=item.get("source_id")
        if not isinstance(sid,str) or not sid or sid in ids:
            return _hold(rid,"DUPLICATE_OR_INVALID_SOURCE_ID",pid)
        ids.add(sid)
        if (item.get("source_type") not in ALLOWED_SOURCE_TYPES
            or item.get("source_type") in ("SYSTEM_CONFIG","UNCLEAR")):
            return _hold(rid,"SOURCE_INERT_OR_UNCLEAR",pid)
        if "source_text" in item or not isinstance(item.get("source_ref"),str) or not item["source_ref"]:
            return _hold(rid,"SOURCE_REFERENCE_REQUIRED_NO_RAW_TEXT",pid)
        digest=item.get("original_sha256")
        if digest is not None and (not isinstance(digest,str) or not re.fullmatch("[0-9a-f]{64}",digest)):
            return _hold(rid,"INVALID_SOURCE_DIGEST",pid)
        if item.get("integrity_status")=="VERIFIED":
            return _hold(rid,"VERIFIED_REQUIRES_INDEPENDENT_BYTE_READBACK",pid)
    constraints=request.get("constraints") or {}
    if operation=="MERGE" and (len(source)<2 or constraints.get("allow_source_merge") is not True):
        return _hold(rid,"MERGE_NOT_EXPLICITLY_AUTHORIZED",pid)
    if len(source)>1 and constraints.get("allow_source_merge") is not True:
        return _hold(rid,"MULTISOURCE_SCOPE_NOT_AUTHORIZED",pid)
    mantra=constraints.get("active_mantra_id")
    if mantra and (profile["mantra_scope"]!="SOURCE_SPECIFIC"
                   or constraints.get("mantra_source_authorized") is not True):
        return _hold(rid,"MANTRA_SOURCE_SCOPE_MISMATCH",pid)
    if constraints.get("allow_new_story_events") is True:
        return _hold(rid,"CREATIVE_INVENTION_NOT_GRANTED_BY_ADAPTER",pid)
    language=request.get("language") or {}
    choice=language.get("explicit_target")
    basis="EXPLICIT_USER_LANGUAGE" if choice is not None else None
    if choice is None:
        choice=language.get("task_language")
        if choice is not None:
            basis="TASK_LANGUAGE"
    if choice is None and (profile["source_language_default"]
       or pid=="english-fulltext-v1.0.0" and operation=="CLEAN"):
        languages={s.get("language") for s in source}
        if len(languages)==1 and next(iter(languages)) in ALLOWED_LANGUAGES:
            choice=next(iter(languages))
            basis="SOURCE_LANGUAGE"
    if choice is None:
        choice=profile["default_language"]
        basis="PROFILE_DEFAULT"
    if choice not in ALLOWED_LANGUAGES:
        return _hold(rid,"LANGUAGE_NOT_SUPPORTED",pid)
    result=_hold(rid,"OWNER_EXECUTION_NOT_AUTHORIZED",pid)
    result.update(status="READY_FOR_OWNER_REVIEW",plan={
        "operation":operation,"profile":pid,"profile_version":profile["version"],
        "source_ids":[s["source_id"] for s in source],"target_language":choice,
        "language_basis":basis,"output_contract":profile["output"],
        "dual_story_available":profile["dual_story"],"foreign_execution":False})
    result["audit"]["foreign_execution"]="PASS_READ_ONLY"
    result["audit"]["provenance"]="SOURCE_REFERENCES_ONLY"
    return result

def catalogue():
    return {"schema":"cls.reconstruction.catalogue.v0.1","mode":"READ_ONLY",
            "profiles":[{"id":key,**value} for key,value in profiles().items()],
            "execution_capable":False,"repository_mutation":False}
