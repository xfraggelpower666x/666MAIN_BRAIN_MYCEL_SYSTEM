import unittest
from engine import semantic_intelligence as s

class SemanticIntelligenceR09Tests(unittest.TestCase):
    def test_positive_function_evidence(self):
        x=s.assess({"motor":"relentless rolling psybass"})
        self.assertIn("FORWARD_MOTION",[f["id"] for f in x["functions"]])
        self.assertIn("LOW_ANCHOR",[f["id"] for f in x["functions"]])

    def test_avoid_swing_is_constraint_not_support(self):
        x=s.assess({"avoid":"avoid swing bass"})
        f=next(f for f in x["functions"] if f["id"]=="BASS_SWING")
        self.assertEqual(f["status"],"EXPLICITLY_CONSTRAINED")
        self.assertFalse(f["support_evidence"])

    def test_negation_does_not_create_positive_support(self):
        x=s.assess({"structure":"not a static loop"})
        f=next(f for f in x["functions"] if f["id"]=="STATIC_REPETITION")
        self.assertEqual(f["status"],"EXPLICITLY_CONSTRAINED")

    def test_negation_scope_does_not_leak_to_next_clause(self):
        x=s.assess({"motor":"not swing bass, relentless rolling groove"})
        by={f["id"]:f for f in x["functions"]}
        self.assertEqual(by["BASS_SWING"]["status"],"EXPLICITLY_CONSTRAINED")
        self.assertEqual(by["FORWARD_MOTION"]["status"],"SUPPORTED")

    def test_voice_and_dense_layers_collision(self):
        x=s.assess({"voice":"clear vocal","mid":"dense acid layers"})
        pair=next(c for c in x["collisions"] if set(c["functions"])=={"VOICE_CLARITY","DENSE_LAYERS"})
        self.assertEqual(pair["status"],"POTENTIAL_COLLISION_REQUIRES_REVIEW")

    def test_arrangement_can_resolve_collision_candidate(self):
        x=s.assess({"voice":"clear vocal","mid":"dense acid layers",
                    "structure":"sparse verse then return; separate sections"})
        pair=next(c for c in x["collisions"] if set(c["functions"])=={"VOICE_CLARITY","DENSE_LAYERS"})
        self.assertEqual(pair["status"],"SEQUENCING_OR_ARRANGEMENT_MAY_RESOLVE")

    def test_motor_and_bass_swing_collision(self):
        x=s.assess({"motor":"straight kick and stable sub","mid":"swing bass"})
        self.assertTrue(any(set(c["functions"])=={"LOW_ANCHOR","BASS_SWING"} for c in x["collisions"]))

    def test_constraint_field_never_supports_function(self):
        x=s.assess({"avoid":"no long silence"})
        f=next(f for f in x["functions"] if f["id"]=="LONG_SILENCE")
        self.assertEqual(f["status"],"EXPLICITLY_CONSTRAINED")

    def test_function_explains_why(self):
        x=s.assess({"energy":"build tension"})
        f=next(f for f in x["functions"] if f["id"]=="TENSION")
        self.assertTrue(f["why_it_matters"])
        self.assertTrue(f["musical_job"])
        self.assertTrue(f["design_guard"])

    def test_track_local_read_only_contract(self):
        x=s.assess({"track_id":"t-1","motor":"forward motion"})
        self.assertEqual(x["system_id"],"666TDI-001")
        self.assertTrue(x["read_only"])
        self.assertFalse(x["global_promotion"])

    def test_empty_input_is_not_invented(self):
        x=s.assess({"title":"Untitled"})
        self.assertEqual(x["status"],"INSUFFICIENT_SEMANTIC_EVIDENCE")
        self.assertEqual(x["functions"],[])

    def test_reject_non_object(self):
        with self.assertRaises(ValueError):
            s.assess("rolling psy")

if __name__ == "__main__":
    unittest.main()
