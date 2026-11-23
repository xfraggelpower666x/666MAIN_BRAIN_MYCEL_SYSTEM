"""Read-only external framework source evidence for 666CLS; no native authority transfer."""
from pathlib import Path
import json

CATALOG = Path(__file__).resolve().parents[1] / "catalog/FRAMEWORK_SOURCE_INDEX.json"
ALLOWED_KINDS = {"ADDON_CANDIDATE", "NATIVE_CANDIDATE", "PFS_CHILD_CANDIDATE", "INDEPENDENT_SPECIALIZED_SYSTEM", "INDEPENDENT_SYSTEM", "OUTPUT_ARTIFACT"}

def load_catalog(path=CATALOG):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("system_id") != "666CLS-CORE-001" or payload.get("schema") != "666CLS_FRAMEWORK_SOURCE_CATALOG_V1":
        raise ValueError("Wrong source catalog identity")
    rows = payload["sources"]
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Duplicate source ID")
    for row in rows:
        if row["classification"] not in ALLOWED_KINDS or row["promotion"] != "NOT_AUTHORIZED" or row["foreign_autoload"] is not False:
            raise ValueError("Source authority violation")
        if len(row["source_sha256"]) != 64 or not all(len(m["sha256"]) == 64 for m in row["members"]):
            raise ValueError("Missing source hash")
    return payload

def summary():
    data = load_catalog()
    return {"status": "EVIDENCE_ONLY", "source_count": len(data["sources"]), "relationship_count": len(data["relationships"]),
            "sources": [{k: row[k] for k in ("id", "version", "classification", "owner_scope", "summary", "source_sha256", "promotion")} for row in data["sources"]],
            "relationships": data["relationships"]}

if __name__ == "__main__":
    print(json.dumps(summary(), ensure_ascii=False, indent=2))
