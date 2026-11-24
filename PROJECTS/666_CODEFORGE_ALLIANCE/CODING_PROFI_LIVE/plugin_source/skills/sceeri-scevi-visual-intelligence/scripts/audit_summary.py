"""Ermittelt den SCEVI-Auditstand aus einer revisionsgebundenen Prüfliste."""

import argparse
from collections import Counter
import json
from pathlib import Path


ALLOWED_RESULTS = {"PASS", "FAIL", "BLOCKED", "OPEN"}


def summarize(report):
    """Berechnet Status und Balken. Evidenzreferenzen werden vom Aufrufer geprüft."""
    if not isinstance(report, dict):
        raise ValueError("Der Prüflauf muss ein JSON-Objekt sein.")
    revision = report.get("revision")
    scope_complete = report.get("scope_complete")
    checks = report.get("checks")
    if not isinstance(revision, str) or not revision.strip():
        raise ValueError("Eine Kandidatenrevision ist erforderlich.")
    if type(scope_complete) is not bool or not isinstance(checks, list):
        raise ValueError("scope_complete muss boolesch und checks eine Liste sein.")

    ids = set()
    counts = Counter()
    critical_blockers = []
    blockers = []
    unresolved = []
    for check in checks:
        if not isinstance(check, dict):
            raise ValueError("Jede Prüfung muss ein JSON-Objekt sein.")
        check_id = check.get("id")
        result = check.get("result")
        critical = check.get("critical")
        if not isinstance(check_id, str) or not check_id.strip() or check_id in ids:
            raise ValueError("Jede Prüfung braucht eine eindeutige, nichtleere ID.")
        if not isinstance(result, str) or result not in ALLOWED_RESULTS or type(critical) is not bool:
            raise ValueError(f"Ungültiges Ergebnis oder Pflichtkennzeichen bei {check_id}.")
        ids.add(check_id)

        evidence = check.get("evidence")
        if result != "OPEN" and (
            check.get("revision") != revision or not isinstance(evidence, str) or not evidence.strip()
        ):
            result = "OPEN"
        counts[result] += 1
        if result == "BLOCKED":
            blockers.append(check_id)
        if critical and result in {"FAIL", "BLOCKED"}:
            critical_blockers.append(check_id)
        if result == "OPEN":
            unresolved.append(check_id)

    total = len(checks) if scope_complete and checks else None
    passed = counts["PASS"]
    if critical_blockers or blockers:
        status = "BLOCKIERT"
    elif counts["FAIL"]:
        status = "REPAIR_REQUIRED"
    elif total is not None and passed == total:
        status = "PASS"
    elif passed:
        status = "PARTIAL"
    else:
        status = "OFFEN"

    return {
        "revision": revision,
        "audit_status": status,
        "passed": passed,
        "total": total,
        "listed_count": len(checks),
        "failed": counts["FAIL"],
        "blocked": counts["BLOCKED"],
        "open": counts["OPEN"],
        "percent_floor": passed * 100 // total if total else None,
        "filled_segments": passed * 20 // total if total else None,
        "critical_blockers": critical_blockers,
        "blockers": blockers,
        "open_ids": unresolved,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="Pfad zur revisionsgebundenen JSON-Prüfliste")
    args = parser.parse_args()
    try:
        result = summarize(json.loads(args.report.read_text(encoding="utf-8")))
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
