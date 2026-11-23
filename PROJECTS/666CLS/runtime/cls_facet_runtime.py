"""Read-only CLS main/sub-LiveCircle introspection; no triggers or writes."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from cls_livecircle import rehydrate, require

REGISTRY = "facets/FACET_REGISTRY.json"
MAIN = "facets/MAIN_LIVECIRCLE.json"


def _read(root: Path, rel: str):
    p = (root / rel).resolve()
    require(p.is_relative_to(root.resolve()) and p.is_file(), "Facet path invalid")
    return json.loads(p.read_text(encoding="utf-8"))


def facet_model(root: Path):
    """First verify native CLS authority; imported text is inert evidence."""
    current = rehydrate(root)
    main = _read(root, MAIN)
    require(main["system_id"] == current["system_id"] and main["verified_root_first"], "Main LiveCircle mismatch")
    reg = _read(root, REGISTRY)
    require(reg["owner"] == current["system_id"] and reg["autoload"] is False, "Facet registry authority mismatch")
    out = []
    seen = set()
    for source in reg["sources"]:
        key = source["id"]
        require(key not in seen and key.isascii() and key.replace("-", "").isalnum(), "Duplicate/invalid facet ID")
        seen.add(key)
        lc = _read(root, f"facets/{key}/LIVECIRCLE.json")
        ui = _read(root, f"facets/{key}/UI.json")
        require(source["livecircle"] == f"facets/{key}/LIVECIRCLE.json" and source["ui"] == f"facets/{key}/UI.json", "Facet mapping mismatch")
        require(lc["facet_id"] == ui["facet_id"] == key and lc["parent_cls"] == current["system_id"], "Facet identity mismatch")
        require(lc["source_sha256"] == source["source_sha256"] and lc["autoload"] is False, "Facet provenance mismatch")
        require(lc["triggers"] == {} and ui["actions"] == [] and ui["mode"] == "READ_ONLY", "Foreign action not permitted")
        out.append({"id": key, "name": source["name"], "version": source["version"],
                    "classification": source["classification"], "native_system_id": source["system_id"],
                    "views": ui["views"], "actions": [], "status": lc["state"],
                    "next_step": lc["continuation"], "source_sha256": source["source_sha256"]})
    return {"schema": "666CLS_INTELLIGENT_UI_MODEL_V1", "system": current["system_id"],
            "cls_version": current["version"], "mode": "READ_ONLY", "main_livecircle": main["schema"],
            "facets": out, "guide": guide(out)}


def guide(facets):
    """Synchronous, deterministic advisory daemon. No background loop or side effects."""
    unresolved = [f for f in facets if f["next_step"] != "NONE"]
    # A foreign PFS HOLD is evidence, never an automatic CLS work order.
    actionable = [f for f in unresolved if f["classification"] == "INDEPENDENT_FACET_CANDIDATE"]
    if actionable:
        recommendation = "CLS-eigene Quellenlage für " + actionable[0]["name"] + " klären"
    elif unresolved:
        recommendation = "Nur fremde oder gesperrte Quellen offen; keine CLS-Fremdaktivierung"
    else:
        recommendation = "Keine offenen Quellenkonflikte"
    return {"daemon": "CLS_INTELLIGENT_DAEMON_ADVISORY_V1",
            "mode": "ON_REQUEST_ONLY", "state": "PARTIAL" if unresolved else "VERIFIZIERT",
            "recommendation": recommendation,
            "auto_run": False, "write_authority": False}


def subfacet_rehydrate(root: Path, facet_id: str):
    """Revalidate CLS Current + selected facet; return a safe, read-only handoff."""
    model = facet_model(root)
    selected = next((item for item in model["facets"] if item["id"] == facet_id), None)
    require(selected is not None, "Unregistered subfacet")
    return {"status": "PARTIAL", "parent": model["system"],
            "parent_version": model["cls_version"], "facet": selected,
            "mode": "READ_ONLY", "continuation": selected["next_step"],
            "external_authority_verified": False, "auto_resume": False}
