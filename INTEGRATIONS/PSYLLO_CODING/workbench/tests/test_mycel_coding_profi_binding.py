"""R06 Coding Profi method capability: positive/negative project binding regressions."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from coding_profi_binding import BindingConflict, BindingIncomplete, bind_project

HEAD = "a" * 40


def current():
    return dict(project_id="666MAIN-BRAIN", source_repository="xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM",
                source_branch="666MAIN_BRAIN", source_head=HEAD, lineage_id="r06-lineage",
                owner="666MAIN BRAIN MYCEL SYSTEM", return_anchor="PSYLLO.DEV")


class CodingProfiR06(unittest.TestCase):
    def call(self, **kwargs):
        return bind_project(whole_verified=True, facet_id="PSYLLO.DEV", current=current(), **kwargs)

    def test_bounded_method_route(self):
        result = self.call()
        self.assertEqual(result["method_provider"], "L.Y.V.R.A. CODING PROFI")
        self.assertEqual(result["provider_lifecircle"], "PROJECT_SCOPED_ONLY")
        self.assertFalse(result["foreign_autoactivation"])
        self.assertEqual(result["execution_authority"], "NONE_METHOD_ROUTING_ONLY")

    def test_matching_project_checkpoint(self):
        self.assertTrue(self.call(checkpoint=current())["checkpoint_accepted"])

    def test_whole_must_precede_subcircle(self):
        with self.assertRaises(BindingIncomplete):
            bind_project(whole_verified=False, facet_id="PSYLLO.DEV", current=current())

    def test_wrong_native_facet_blocked(self):
        with self.assertRaises(BindingConflict):
            bind_project(whole_verified=True, facet_id="PSYLLO.VISUAL", current=current())

    def test_missing_project_does_not_activate(self):
        with self.assertRaises(BindingIncomplete):
            bind_project(whole_verified=True, facet_id="PSYLLO.DEV", current=None)

    def test_bad_head_blocked(self):
        item = current()
        item["source_head"] = "stale"
        with self.assertRaises(BindingIncomplete):
            bind_project(whole_verified=True, facet_id="PSYLLO.DEV", current=item)

    def test_wrong_lineage_blocked(self):
        item = current()
        item["lineage_id"] = "foreign-line"
        with self.assertRaises(BindingConflict):
            self.call(checkpoint=item)

    def test_wrong_project_blocked(self):
        item = current()
        item["project_id"] = "foreign"
        with self.assertRaises(BindingConflict):
            self.call(checkpoint=item)

    def test_stale_head_blocked(self):
        item = current()
        item["source_head"] = "b" * 40
        with self.assertRaises(BindingConflict):
            self.call(checkpoint=item)

    def test_wrong_owner_blocked(self):
        item = current()
        item["owner"] = "FOREIGN_OWNER"
        with self.assertRaises(BindingConflict):
            self.call(checkpoint=item)

    def test_embedded_trigger_cannot_bind_as_identifier(self):
        item = current()
        item["project_id"] = "666MAIN BRAIN UPDATE"
        with self.assertRaises(BindingIncomplete):
            bind_project(whole_verified=True, facet_id="PSYLLO.DEV", current=item)

    def test_registry_preserves_all_native_facets(self):
        reg = json.loads((ROOT / "RUNTIME/FACET_RUNTIME_REGISTRY.json").read_text(encoding="utf-8"))
        self.assertEqual(len(reg["facets"]), 15)
        self.assertEqual(sum(x["id"] == "PSYLLO.DEV" for x in reg["facets"]), 1)
        self.assertFalse(reg["foreign_autoactivation"])

    def test_daemon_adapter_preserved_and_extended(self):
        reg = json.loads((ROOT / "DAEMON/FACET_ADAPTERS.json").read_text(encoding="utf-8"))
        dev = next(a for a in reg["adapters"] if a["facet"] == "PSYLLO.DEV")
        self.assertIn("CHECK_PROJECT_BINDING", dev["steps"])
        self.assertIn("VERIFY_CODING_PROFI_SKILL_SOURCE", dev["steps"])
        self.assertEqual(dev["method_capability"], "INTEGRATIONS/PSYLLO_CODING/CODING_PROFI_FACET_ADAPTER_R06.md")
        self.assertFalse(reg["restrictions"]["autostart_foreign"])

    def test_runtime_registry_method_capability(self):
        reg = json.loads((ROOT / "RUNTIME/RUNTIME_REGISTRY.json").read_text(encoding="utf-8"))
        cap = reg["mycel_r06"]["coding_profi_method"]
        self.assertEqual(cap["native_facet"], "PSYLLO.DEV")
        self.assertEqual(cap["provider"], "L.Y.V.R.A. CODING PROFI")
        self.assertFalse(cap["foreign_autoactivation"])


if __name__ == "__main__":
    unittest.main()
