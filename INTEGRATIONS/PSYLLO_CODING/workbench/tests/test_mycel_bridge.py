"""MYCEL R02 bridge regression: no side effects, strict source/lineage validation."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from mycel_bridge import project

HEAD = "a" * 40
VIEWS = ("OVERVIEW", "DEVELOPMENT", "FACETS", "GUIDANCE", "EVIDENCE", "CONTINUITY")


def menu():
    return {"schema": "psyllo.intelligent-menu.1",
            "owner": "666MAIN BRAIN MYCEL SYSTEM",
            "views": [{"id": name, "label": name.title(), "action": "local_view"}
                      for name in VIEWS]}


def state():
    return {"schema": "psyllo.guidance-state.1",
            "owner": "666MAIN BRAIN MYCEL SYSTEM", "source_head": HEAD,
            "active_scope": "666MAIN-BRAIN", "lineage_id": "line-a",
            "phase": "Analyse", "evidence_class": "PARTIAL",
            "open_obligations": ["host-acceptance"],
            "blockers": ["Fresh Chat offen"],
            "last_verified_step": "Pointer gelesen",
            "next_action": {"label": "Host prüfen"}}


class MycelBridgeTests(unittest.TestCase):
    def test_six_native_views_renderer_shape(self):
        result = project(menu(), state())
        self.assertEqual(len(result["views"]), 6)
        self.assertEqual(result["views"][0]["id"], "overview")
        self.assertEqual(result["companion"]["status"], "PARTIAL")
        self.assertEqual(result["companion"]["source_revision"], HEAD)
        self.assertEqual(result["handoff_format"], "neutral")

    def test_matching_handoff_restores_view(self):
        handoff = {"schema": "psyllo.ui-handoff.1", "project_id": "666MAIN-BRAIN",
                   "source_commit": HEAD, "lineage_id": "line-a",
                   "view_id": "development"}
        self.assertEqual(project(menu(), state(), handoff=handoff)["companion"]["start_view"],
                         "development")

    def test_mismatched_revision_rejected(self):
        handoff = {"schema": "psyllo.ui-handoff.1", "project_id": "666MAIN-BRAIN",
                   "source_commit": "b" * 40, "lineage_id": "line-a"}
        with self.assertRaises(ValueError):
            project(menu(), state(), handoff=handoff)

    def test_mismatched_lineage_rejected(self):
        handoff = {"schema": "psyllo.ui-handoff.1", "project_id": "666MAIN-BRAIN",
                   "source_commit": HEAD, "lineage_id": "different"}
        with self.assertRaises(ValueError):
            project(menu(), state(), handoff=handoff)

    def test_missing_lineage_cannot_restore_handoff(self):
        s = state()
        s.pop("lineage_id")
        handoff = {"schema": "psyllo.ui-handoff.1", "project_id": "666MAIN-BRAIN",
                   "source_commit": HEAD}
        with self.assertRaises(ValueError):
            project(menu(), s, handoff=handoff)

    def test_foreign_owner_rejected(self):
        bad = menu()
        bad["owner"] = "666DEV"
        with self.assertRaises(ValueError):
            project(bad, state())

    def test_malformed_sha_rejected(self):
        bad = state()
        bad["source_head"] = "not-a-commit"
        with self.assertRaises(ValueError):
            project(menu(), bad)

    def test_invalid_project_key_rejected(self):
        bad = state()
        bad["active_scope"] = "666 MAIN BRAIN"
        with self.assertRaises(ValueError):
            project(menu(), bad)

    def test_menu_mutation_rejected(self):
        bad = menu()
        bad["views"][0]["action"] = "execute_command"
        with self.assertRaises(ValueError):
            project(bad, state())

    def test_missing_blocker_and_action_is_explicit(self):
        s = state()
        s["blockers"] = []
        s["next_action"] = None
        result = project(menu(), s)
        self.assertIn("keine", result["companion"]["blocker"].lower())
        self.assertIn("prüfen", result["companion"]["next_step"])


if __name__ == "__main__":
    unittest.main()
