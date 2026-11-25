"""R06 immutable-snapshot source binding; trust is NOT conferred by untrusted input.

This module verifies that documents match a *separately supplied* pre-approved registry.
It DOES NOT authenticate the registry's author (SHA256 is not a signature), validate
real-world causal truth, or fetch/execute remote content. No filesystem/network I/O.
"""
from __future__ import annotations
import hashlib
from .evidence_graph_r05 import evaluate_documents, _identifier, _timestamp, MAX_DOCUMENTS

SCHEMA = "666CURES_R06_PROVENANCE_EVIDENCE_V1"
REGISTRY_SCHEMA = "666CURES_R06_SOURCE_REGISTRY_V1"
ALLOWED_KEYS = {"document_id", "source_group", "observed_at", "content_sha256", "provenance_ref", "issuer_id"}
HEX = frozenset("0123456789abcdef")

def _digest(v):
    if not isinstance(v, str) or len(v) != 64 or not set(v) <= HEX:
        raise ValueError("invalid sha256")
    return v

def _entry(value):
    if not isinstance(value, dict) or set(value) != ALLOWED_KEYS:
        raise ValueError("registry entry shape mismatch")
    return {"document_id": _identifier(value["document_id"],"document_id"),
            "source_group": _identifier(value["source_group"],"source_group"),
            "observed_at": _timestamp(value["observed_at"]),
            "content_sha256": _digest(value["content_sha256"]),
            "provenance_ref": _identifier(value["provenance_ref"],"provenance_ref"),
            "issuer_id": _identifier(value["issuer_id"],"issuer_id")}

def verify_sources(documents, registry):
    """Fail-closed integrity binding to an externally reviewed registry snapshot.

    Trust is explicitly out-of-band: registry supplied by caller MUST have an
    authenticated review/transport channel. Untrusted document input must not
    provide or replace that registry. Output only reports matching evidence.
    """
    if not isinstance(registry,dict) or set(registry)!={"schema","entries","review_status"}:
        raise ValueError("registry shape mismatch")
    if registry["schema"]!=REGISTRY_SCHEMA or registry["review_status"]!="EXTERNAL_REVIEW_REQUIRED":
        raise ValueError("registry review marker invalid")
    entries=registry["entries"]
    if not isinstance(entries,list) or not 1 <= len(entries) <= MAX_DOCUMENTS:
        raise ValueError("registry entries out of bounds")
    approved={}
    for raw in entries:
        entry=_entry(raw)
        if entry["document_id"] in approved: raise ValueError("duplicate registry document ID")
        approved[entry["document_id"]]=entry
    if not isinstance(documents,list) or not 1 <= len(documents) <= MAX_DOCUMENTS:
        raise ValueError("documents count out of bounds")
    matched=[]
    for doc in documents:
        if not isinstance(doc,dict):raise ValueError("document must be object")
        doc_id=_identifier(doc.get("document_id"),"document_id")
        reg=approved.get(doc_id)
        if reg is None:raise ValueError("unregistered document")
        if set(doc) - {"document_id","source_group","observed_at","content_sha256","source_text"}:
            raise ValueError("unexpected document keys")
        raw=doc.get("source_text")
        if not isinstance(raw,str):raise ValueError("missing source text")
        digest=hashlib.sha256(raw.encode("utf-8")).hexdigest()
        if digest!=reg["content_sha256"]:raise ValueError("registered content hash mismatch")
        if doc.get("content_sha256",digest)!=digest: raise ValueError("document content hash mismatch")
        if _timestamp(doc.get("observed_at"))!=reg["observed_at"]:
            raise ValueError("observed time differs from registry")
        if doc.get("source_group",doc_id)!=reg["source_group"]:
            raise ValueError("source group differs from registry")
        matched.append(reg)
    # R05 retains all bounded parsing and evidence safety constraints.
    graph=evaluate_documents(documents)
    match_by_id={e["document_id"]:e for e in matched}
    for doc in graph["documents"]:
        reg=match_by_id[doc["document_id"]]
        doc["provenance_ref"]=reg["provenance_ref"]
        doc["issuer_id"]=reg["issuer_id"]
        doc["integrity_status"]="MATCHED_EXTERNALLY_SUPPLIED_REGISTRY"
    for edge in graph["edges"]:
        for ev in edge["evidence"]:
            reg=match_by_id[ev["document_id"]]
            ev["provenance_ref"]=reg["provenance_ref"]
            ev["issuer_id"]=reg["issuer_id"]
    graph.update({"schema":SCHEMA,"source_registration":"ALL_PROVIDED_DOCUMENTS_MATCH_REGISTRY",
                  "registry_authenticity":"NOT_VERIFIED_BY_THIS_MODULE",
                  "trusted_origin_claim":"NOT_ESTABLISHED_WITHOUT_EXTERNAL_SIGNED_APPROVAL",
                  "source_content_integrity":True,
                  "automatic_truth_promotion":False,
                  "temporal_conflicts_preserved":True,
                  "external_io":False,
                  "allowed_to_execute":False})
    return graph
