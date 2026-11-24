"""Optionale Prüfung der nächsten Engineering-Entscheidung aus bestätigten Fakten."""

import argparse
import json
from pathlib import Path


GOALS = {
    "UNDERSTAND": (),
    "AUDIT": (),
    "REPAIR": ("defect_supported", "fix_supported"),
    "IMPROVE": ("target_criterion", "invariants_known"),
    "EXTEND": ("new_behavior_defined", "affected_contracts_known"),
    "CREATE": ("new_behavior_defined", "minimal_path_known"),
}
WRITE_GOALS = {"REPAIR", "IMPROVE", "EXTEND", "CREATE"}
FLAGS = set().union(*GOALS.values(), {
    "target_bound", "write_authorized", "write_outcome_unknown",
    "candidate_written", "acceptance_observed",
})


def decide(goal: str, facts: dict[str, bool]) -> str:
    """Gibt den nächsten fachlichen Schritt zurück. Fehlende Fakten bleiben offen."""
    if not isinstance(goal, str) or goal not in GOALS:
        raise ValueError("Unbekannte Arbeitsart.")
    if not isinstance(facts, dict) or facts.keys() - FLAGS or any(type(v) is not bool for v in facts.values()):
        raise ValueError("Erwartet werden bekannte Fakten als boolesche Werte.")
    if not facts.get("target_bound"):
        return "BIND_TARGET"
    if goal not in WRITE_GOALS:
        return "READ_ONLY"
    if facts.get("write_outcome_unknown"):
        return "READBACK_FIRST"
    if not all(facts.get(key) for key in GOALS[goal]):
        return "CLARIFY_OR_TEST"
    if facts.get("candidate_written"):
        return "COMPLETE_FOR_CHECKED_SCOPE" if facts.get("acceptance_observed") else "VERIFY_CANDIDATE"
    if not facts.get("write_authorized"):
        return "PROPOSE_ONLY"
    return "CHANGE_WITHIN_SCOPE"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON-Objekt mit goal und facts")
    args = parser.parse_args()
    try:
        request = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(request, dict):
            raise ValueError("Erwartet wird ein JSON-Objekt.")
        result = decide(request.get("goal"), request.get("facts"))
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps({"next_step": result}))


if __name__ == "__main__":
    main()
