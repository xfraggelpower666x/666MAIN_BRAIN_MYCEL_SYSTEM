"""Read-only MAIN BRAIN capability lookup. The caller owns trigger validation."""
import argparse
import json
from pathlib import Path

REGISTRY = Path(__file__).with_name("CAPABILITIES_R01.json")
CURRENT_KEY = "PLUGIN_CAPABILITIES_R01_REGISTRY"


def current_registry(checkout):
    """Resolve the catalog from an already selected MAIN BRAIN checkout."""
    checkout = checkout.resolve()
    runtime = json.loads(
        (checkout / "RUNTIME/RUNTIME_REGISTRY.json").read_text(encoding="utf-8")
    )
    if runtime.get("system_id") != "666MAIN-BRAIN-MYCEL-SYSTEM-001":
        raise ValueError("Checkout gehört nicht zu 666MAIN BRAIN")
    pointer = (checkout / "CURRENT_POINTER.md").read_text(encoding="utf-8")
    intelligence = runtime["intelligence"]
    catalog = bound_file(checkout, pointer, CURRENT_KEY, intelligence["plugin_capabilities"])
    bound_file(checkout, pointer, "PLUGIN_CAPABILITIES_R01_WORKFLOWS",
               intelligence["plugin_capability_workflows"])
    return catalog


def bound_file(checkout, pointer, key, reference):
    if not isinstance(reference, str) or not reference:
        raise ValueError(f"Ungültige Pfadangabe für {key}")
    declarations = [
        line.split("=", 1)[1]
        for line in pointer.splitlines()
        if line.startswith(key + "=")
    ]
    if declarations != [reference]:
        raise ValueError(f"Current-Pointer und Runtime-Registry weichen ab: {key}")
    relative_path = Path(reference)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise ValueError("Dateipfad muss checkout-relativ sein")
    catalog = (checkout / relative_path).resolve()
    if not catalog.is_relative_to(checkout):
        raise ValueError("Dateipfad verlässt den Checkout")
    if not catalog.is_file():
        raise ValueError(f"Datei fehlt für {key}")
    return catalog


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
    parser.add_argument("--checkout", type=Path, help="Katalog über MAIN BRAIN Current auflösen")
    args = parser.parse_args()
    try:
        path = current_registry(args.checkout) if args.checkout is not None else REGISTRY
        registry = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, KeyError) as error:
        parser.error(f"Katalog nicht lesbar: {error}")
    try:
        rows = select(registry, args.capability_id, facet=args.facet, workflow=args.workflow)
    except KeyError:
        parser.error(f"Unbekannte Capability-ID: {args.capability_id}")
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
