"""Lokale Gegenproben für die Entscheidungshierarchie."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from engineering_decision import decide


class EngineeringDecisionTests(unittest.TestCase):
    def test_decisions(self):
        bound = {"target_bound": True}
        change = {**bound, "write_authorized": True}
        repair = {**change, "defect_supported": True, "fix_supported": True}
        cases = [
            ("ungebunden", "AUDIT", {}, "BIND_TARGET"),
            ("lesendes Audit", "AUDIT", change, "READ_ONLY"),
            ("lesendes Verstehen", "UNDERSTAND", change, "READ_ONLY"),
            ("Symptom ohne Mechanismus", "REPAIR", {**change, "defect_supported": True}, "CLARIFY_OR_TEST"),
            ("Reparaturvorschlag", "REPAIR", {**repair, "write_authorized": False}, "PROPOSE_ONLY"),
            ("belegte Reparatur", "REPAIR", repair, "CHANGE_WITHIN_SCOPE"),
            ("unsicherer Write", "REPAIR", {**repair, "write_outcome_unknown": True}, "READBACK_FIRST"),
            ("Verbesserung ohne Sollwert", "IMPROVE", {**change, "invariants_known": True}, "CLARIFY_OR_TEST"),
            ("belegte Verbesserung", "IMPROVE", {**change, "target_criterion": True, "invariants_known": True}, "CHANGE_WITHIN_SCOPE"),
            ("Erweiterung ohne betroffene Verträge", "EXTEND", {**change, "new_behavior_defined": True}, "CLARIFY_OR_TEST"),
            ("beauftragte Erweiterung", "EXTEND", {**change, "new_behavior_defined": True, "affected_contracts_known": True}, "CHANGE_WITHIN_SCOPE"),
            ("Neubau mit Normalpfad", "CREATE", {**change, "new_behavior_defined": True, "minimal_path_known": True}, "CHANGE_WITHIN_SCOPE"),
            ("Patch ohne beobachtete Abnahme", "REPAIR", {**repair, "candidate_written": True}, "VERIFY_CANDIDATE"),
            ("geprüfter Kandidat", "REPAIR", {**repair, "candidate_written": True, "acceptance_observed": True}, "COMPLETE_FOR_CHECKED_SCOPE"),
        ]
        for label, goal, facts, expected in cases:
            with self.subTest(label=label):
                self.assertEqual(decide(goal, facts), expected)

    def test_invalid_input(self):
        for goal, facts in [([], {}), ("AUDIT", {"target_bound": "true"}), ("AUDIT", {"unbekannt": True})]:
            with self.subTest(goal=goal, facts=facts):
                with self.assertRaises(ValueError):
                    decide(goal, facts)


if __name__ == "__main__":
    unittest.main()
