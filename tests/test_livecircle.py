"""Regression tests for the non-mutating Research Orchestra recovery LiveCircle."""
import importlib.util
import json
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("livecircle", HERE / "tools/livecircle.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class LiveCircleTests(unittest.TestCase):
    def test_historical_manifest_is_present(self):
        self.assertGreater(len(MOD.expected_hashes()), 100)

    def test_three_original_modules_are_byte_exact(self):
        result = MOD.audit()
        self.assertGreaterEqual(result["verified"], 3)
        self.assertEqual(result["mismatch"], [])
        for name in (
            "data/topics/topic-chaos-theory.js",
            "data/topics/topic-chaos-psytrance-psychoacoustics.js",
            "data/prompts/prompt-chaos-psytrance-suno-specialist.js",
        ):
            self.assertIn(name, MOD.expected_hashes())
            self.assertIn(name, MOD.known_source_files())

    def test_incomplete_source_fails_closed(self):
        result = MOD.audit()
        self.assertEqual(result["status"], "READBACK_PENDING")
        self.assertGreater(result["missing_count"], 100)

    def test_runtime_is_nonmutating(self):
        source = (HERE / "tools/livecircle.py").read_text(encoding="utf-8")
        self.assertNotIn("update_ref", source)
        self.assertNotIn("create_file", source)
        self.assertNotIn("shutil.rmtree", source)

    def test_project_is_independent(self):
        state = json.loads((HERE / "state/LIVE_WORKSPACE_STATE.json").read_text(encoding="utf-8"))
        self.assertEqual(state["project"], "666 RESEARCH MD DATABASE ORCHESTRA")
        self.assertEqual(state["historical_release"], "v1.7.1-clean-system.1")
        self.assertEqual(state["production_promotion"], "FORBIDDEN_UNTIL_FULL_READBACK")


if __name__ == "__main__":
    unittest.main()
