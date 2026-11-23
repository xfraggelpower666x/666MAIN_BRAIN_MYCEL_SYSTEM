import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from framework_intake import CONSOLIDATION, OWNERSHIP, analyze


class FrameworkIntakeTests(unittest.TestCase):
    def run_dossier(self, facts, target_revision="target-r2"):
        registry = {"existing": {"revision": "target-r2"}}
        dossier = {"name":"Aufnahme", "revision":"source-r1", "target":"existing",
                   "target_revision":target_revision,
                   "facts":{name: {"value": value, "source": f"Fundstelle {name}", "revision":"source-r1",
                                   "target_revision":target_revision} for name, value in facts.items()}}
        return analyze(dossier, registry)

    def test_native_framework_and_shared_component(self):
        base = {"native_authority":True, "native_entry":True}
        self.assertEqual(self.run_dossier(base)["decision"], "EIGENSTÄNDIGES_FRAMEWORK")
        self.assertEqual(self.run_dossier({**base, "shared_component":True})["decision"],
                         "EIGENSTÄNDIG_MIT_GEMEINSAMEM_BAUSTEIN")
        self.assertEqual(self.run_dossier({**base, "host_dependency":True})["decision"], "KONFLIKT_PRÜFEN")

    def test_module_and_consolidation_are_distinct(self):
        no_identity = dict.fromkeys(OWNERSHIP, False)
        self.assertEqual(self.run_dossier({**no_identity, "host_dependency":True})["decision"],
                         "MODUL_VORSCHLAGEN")
        facts = {**no_identity, **dict.fromkeys(CONSOLIDATION, True)}
        self.assertEqual(self.run_dossier(facts)["decision"], "KONSOLIDIERUNG_VORSCHLAGEN")
        self.assertEqual(self.run_dossier({**facts, "continuity_preserved":False})["decision"], "OFFEN")

    def test_stale_or_missing_comparison_remains_open(self):
        result = self.run_dossier({**dict.fromkeys(OWNERSHIP, False),
                                   **dict.fromkeys(CONSOLIDATION, True)}, "old-target")
        self.assertEqual(result["decision"], "OFFEN")
        self.assertTrue(any("Revision" in gap or "Zielrevision" in gap for gap in result["gaps"]))
        self.assertEqual(self.run_dossier({"same_purpose":True})["decision"], "OFFEN")

    def test_package_roles_and_inverse_contract(self):
        self.assertEqual(self.run_dossier({"package_only": True})["decision"], "QUELLARTEFAKT")
        self.assertEqual(self.run_dossier({"inverse_contract": True})["decision"],
                         "GETRENNTE_TRANSFORMATIONSWEGE")
        self.assertEqual(self.run_dossier({"native_child": True})["decision"], "OFFEN")
        for fact, decision in (("native_child", "NATIVES_CHILD_ERHALTEN"),
                               ("native_addon", "NATIVES_ADDON_ZUORDNEN")):
            dossier = {"name": "Paket", "revision": "r1", "parent": "EXISTING-001",
                       "facts": {fact: {"value": True, "source": "Vertrag", "revision": "r1"}}}
            self.assertEqual(analyze(dossier, {})["decision"], decision)
        self.assertEqual(self.run_dossier({"package_only": True, "native_authority": True,
                                          "own_state": True})["decision"], "KONFLIKT_PRÜFEN")
