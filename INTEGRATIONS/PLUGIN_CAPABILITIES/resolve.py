"""Read-only MAIN BRAIN capability lookup. The caller owns trigger validation."""
import argparse
import json
from pathlib import Path

REGISTRY = Path(__file__).with_name("CAPABILITIES_R01.json")


def select(registry, capability_id=None, *, facet=None, workflow=None):
    """Return exact matches in registry order, without dispatching a provider."""
    rows = registry["capabilities"]
    if capability_id is not None:
        rows = [row for row in rows if row["id"] == capability_id]
        if not rows:
            raise KeyError(capability_id)
    return [
        row for row in rows
        if (facet is None or row["facet"] == facet)
        and (workflow is None or row["workflow"] == workflow)
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capability_id", nargs="?")
    parser.add_argument("--facet")
    parser.add_argument("--workflow")
    args = parser.parse_args()
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    try:
        rows = select(registry, args.capability_id, facet=args.facet, workflow=args.workflow)
    except KeyError:
        parser.error(f"Unbekannte Capability-ID: {args.capability_id}")
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
