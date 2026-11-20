"""Compare declared Markdown module IDs with an explicit numbered registry."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re


MODULE_ID = r"MOD-[A-Z0-9]+(?:-[A-Z0-9]+)*-[0-9]+"
ACTIVE = re.compile(rf"^MOD-ID:[ \t]+({MODULE_ID})[ \t]*$", re.MULTILINE)
LEGACY = re.compile(rf"^LEGACY-MOD-ID:[ \t]+({MODULE_ID})[ \t]*$", re.MULTILINE)
BARE = re.compile(rf"^({MODULE_ID})[ \t]*$", re.MULTILINE)
REGISTERED = re.compile(rf"^[0-9]+\.[ \t]+({MODULE_ID})[ \t]*$", re.MULTILINE)


def verify(master, registry):
    active = Counter(ACTIVE.findall(master))
    registered = Counter(REGISTERED.findall(registry))
    if not active or not registered:
        raise ValueError("Master and registry must both contain module declarations")

    findings = {
        "unregistered_active": sorted(active.keys() - registered.keys()),
        "missing_active": sorted(registered.keys() - active.keys()),
        "duplicate_active": sorted(module for module, count in active.items() if count > 1),
        "duplicate_registry": sorted(module for module, count in registered.items() if count > 1),
        "bare_module_ids": sorted(set(BARE.findall(master))),
    }
    return {
        "status": "MODULE_REGISTRY_MISMATCH" if any(findings.values()) else "MODULE_REGISTRY_MATCH",
        "active_module_count": len(active),
        "registry_module_count": len(registered),
        "legacy_definition_count": len(LEGACY.findall(master)),
        **findings,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("master", type=Path)
    parser.add_argument("registry", type=Path)
    args = parser.parse_args()
    try:
        report = verify(
            args.master.read_text(encoding="utf-8-sig"),
            args.registry.read_text(encoding="utf-8-sig"),
        )
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "MODULE_REGISTRY_MATCH" else 1


if __name__ == "__main__":
    raise SystemExit(main())
