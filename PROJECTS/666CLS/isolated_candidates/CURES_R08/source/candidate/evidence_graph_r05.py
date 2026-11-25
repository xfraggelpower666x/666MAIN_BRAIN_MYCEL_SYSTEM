"""R05 bounded cross-document evidence model; assertions are not causal facts.
No I/O, no shared state, no external services. Standalone R05 path; R01-R04 unchanged.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone
import hashlib, re

ASSERTIONS = {"CLAIM", "DENY", "COUNTEREXAMPLE", "HYPOTHESIS", "OBSERVE", "UNKNOWN"}
LINE_RE = re.compile(r"^(CLAIM|DENY|COUNTEREXAMPLE|HYPOTHESIS|OBSERVE|UNKNOWN) CAUSE ([A-Za-z][A-Za-z0-9_.-]*) -> ([A-Za-z][A-Za-z0-9_.-]*)$")
UTC_RE = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)$")
MAX_DOCUMENTS = 128
MAX_LINES_PER_DOCUMENT = 500
MAX_ASSERTIONS = 4000
MAX_TOTAL_CHARS = 200_000


def _timestamp(value):
    if not isinstance(value,str) or not UTC_RE.fullmatch(value):
        raise ValueError("observed_at must be timezone-qualified ISO 8601")
    try:
        dt=datetime.fromisoformat(value.replace("Z","+00:00"))
        if dt.utcoffset() is None: raise ValueError()
        return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    except ValueError as exc:
        raise ValueError("invalid observed_at") from exc


def _identifier(value, field):
    if not isinstance(value,str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}",value):
        raise ValueError(f"invalid {field}")
    return value


def evaluate_documents(documents):
    """Evaluate source ASSERTIONS across independent document IDs, no truth scoring.

    Schema: [{document_id, observed_at, source_text, optional content_sha256, optional source_group}]
    source_group denotes a declared common origin and reduces naive independence claims.
    Returns JSON-native evidence only. No automatic temporal supersession or promotion.
    """
    if not isinstance(documents,list) or not 1<=len(documents)<=MAX_DOCUMENTS: raise ValueError("documents count out of bounds")
    docs=[]; seen=set(); grouped=defaultdict(list); total=0; total_assertions=0
    for d in documents:
        if not isinstance(d,dict): raise ValueError("document must be object")
        doc_id=_identifier(d.get("document_id"),"document_id")
        if doc_id in seen: raise ValueError("duplicate document identity")
        seen.add(doc_id)
        group=_identifier(d.get("source_group",doc_id),"source_group")
        timestamp=_timestamp(d.get("observed_at"))
        raw=d.get("source_text")
        if not isinstance(raw,str) or not raw.strip(): raise ValueError("missing source_text")
        total+=len(raw)
        if total>MAX_TOTAL_CHARS: raise ValueError("total source too large")
        lines=raw.splitlines()
        if len(lines)>MAX_LINES_PER_DOCUMENT: raise ValueError("document too many lines")
        digest=hashlib.sha256(raw.encode("utf-8")).hexdigest()
        provided=d.get("content_sha256")
        if provided is not None and provided!=digest: raise ValueError("content hash mismatch")
        count=0
        for line_no, line in enumerate(lines,1):
            match=LINE_RE.fullmatch(line.strip())
            if not match: continue  # opaque material is not treated as a causal assertion
            typ,a,b=match.groups()
            grouped[(a,b)].append({"document_id":doc_id,"source_group":group,"observed_at":timestamp,
                                    "line":line_no,"assertion":typ,"source_span":line.strip(),"sha256":digest})
            count+=1;total_assertions+=1
            if total_assertions>MAX_ASSERTIONS:raise ValueError("too many assertions")
        docs.append({"document_id":doc_id,"source_group":group,"observed_at":timestamp,
                     "content_sha256":digest,"assertions_extracted":count})
    edges=[]
    for (a,b),evs in sorted(grouped.items()):
        supports=[e for e in evs if e["assertion"]=="CLAIM"]
        conflicts=[e for e in evs if e["assertion"] in ("DENY","COUNTEREXAMPLE")]
        uncertain=[e for e in evs if e["assertion"] in ("HYPOTHESIS","OBSERVE","UNKNOWN")]
        if supports and conflicts: assessment="CONTRADICTED_SOURCE_ASSERTIONS"
        elif supports: assessment="SOURCE_CLAIM_UNVERIFIED"
        elif conflicts: assessment="SOURCE_NEGATIVE_ONLY"
        else: assessment="UNCERTAIN_ONLY"
        docs_s=sorted(set(e["document_id"] for e in supports))
        docs_c=sorted(set(e["document_id"] for e in conflicts))
        groups_s=sorted(set(e["source_group"] for e in supports))
        groups_c=sorted(set(e["source_group"] for e in conflicts))
        edges.append({"source":a,"target":b,"assessment":assessment,"evidence":evs,
                      "support_document_ids":docs_s,"counter_document_ids":docs_c,
                      "support_source_groups":groups_s,"counter_source_groups":groups_c,
                      "distinct_support_groups":len(groups_s),"distinct_counter_groups":len(groups_c),
                      "source_assertion_count":len(evs),"uncertain_count":len(uncertain),
                      "provenance_conflict":bool(supports and conflicts),
                      "truth_score":None,"independently_verified":False,"is_inferred":False,
                      "temporal_supersession_applied":False})
    return {"schema":"666CURES_R05_CROSS_DOCUMENT_EVIDENCE_V1","documents":docs,
            "nodes":sorted({v for a,b in grouped for v in (a,b)}),"edges":edges,
            "assertions_extracted":total_assertions,
            "claims_not_truth":True,"group_counting_not_probability":True,
            "temporal_evidence_preserved":True,"automatic_supersession":False,
            "inferred_causal_edges":[],"transitive_causation_inferred":False,
            "authority_changed":False,"mutations":[],"autoload":False}
