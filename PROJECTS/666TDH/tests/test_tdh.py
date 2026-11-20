import json
from pathlib import Path
import shutil
import tempfile
import unittest

from tdh import Current, CurrentError


ROOT = Path(__file__).resolve().parents[1]


class RepoCurrentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.current = Current(ROOT)

    def test_root_does_not_select_a_child(self):
        result = self.current.execute("666TDH SYSTEMSTART", True)
        self.assertIsNone(result["selected_branch"])
        self.assertEqual(set(self.current.registry["children"]), {item["branch"] for item in result["commands"]})
        self.assertTrue(all(not path.startswith("runtime/children/") for path in result["bootstrap"]))

    def test_all_current_branch_bootstraps(self):
        for branch, child in self.current.registry["children"].items():
            with self.subTest(branch=branch):
                result = self.current.execute(f"666TDH {branch} SYSTEMSTART", True)
                self.assertEqual(result["target"], child["system_id"])
                foreign = [p for p in result["bootstrap"] if p.startswith("runtime/children/") and not p.startswith(f"runtime/children/{branch}/")]
                self.assertEqual(foreign, [])
                self.assertIn(child["current_path"], result["bootstrap"])

    def test_new_chat_and_handoff_scope(self):
        result = self.current.execute("666TDH LCTS NEW CHAT")
        self.assertEqual(result["next_chat_trigger"], "666TDH LCTS SYSTEMSTART")
        self.assertEqual(result["continuity"]["status"], "NO_BOUND_HANDOFF")
        self.assertIsNone(self.current.execute("666TDH WEITER")["continuity"]["open_step"])

    def test_foreign_or_inert_commands_are_rejected(self):
        for command in ("SYSTEMSTART", "666PFS SYSTEMSTART", "666TDH FAKE SYSTEMSTART", "666TDH FSE UPDATE", '\"666TDH TD SYSTEMSTART\"'):
            with self.subTest(command=command), self.assertRaises(CurrentError):
                self.current.execute(command)

    def test_tampered_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as work:
            root = Path(work)
            shutil.copy2(ROOT / "CURRENT_POINTER.json", root)
            for path in self.current.hashes:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / path, target)
            file = root / "runtime/REGISTRY.json"
            registry = json.loads(file.read_bytes())
            registry["system_id"] = "WRONG"
            file.write_text(json.dumps(registry), encoding="utf-8")
            with self.assertRaisesRegex(CurrentError, "SHA-256"):
                Current(root)

    def test_open_identity_and_visual_gates_preserved(self):
        for branch in ("FSE", "SHACHIVITI"):
            self.assertEqual(self.current.execute(f"666TDH {branch} STATUS")["child"]["source_identity"], "UNRESOLVED_HOLD")
        self.assertEqual(self.current.execute("666TDH VISUAL")["visual_host_acceptance"], "OPEN_NOT_VERIFIED")


    def test_repo_update_is_pfs_independent(self):
        result = self.current.execute("666TDH UPDATE", True)
        authority = "runtime/REPO_UPDATE_AUTHORITY.md"
        self.assertEqual(result["publication"]["target"], "666MAIN_BRAIN:PROJECTS/666TDH")
        self.assertIn(authority, result["bootstrap_order"])
        policy = result["bootstrap"][authority]
        self.assertIn("PFS_RUNTIME_AUTHORITY=NONE", policy)
        self.assertIn("PFS_MUTATION_FROM_TDH=FORBIDDEN", policy)
        self.assertIn("CURRENT_POINTER_LAST=TRUE", policy)
        self.assertIn("FSE source-original archive: SOURCE_VAULT_ONLY", policy)
        self.assertEqual(len(self.current.registry["children"]), 5)


if __name__ == "__main__":
    unittest.main()
