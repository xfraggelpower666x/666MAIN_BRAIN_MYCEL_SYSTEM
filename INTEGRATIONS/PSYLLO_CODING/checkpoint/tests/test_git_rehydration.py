"""Gegenproben mit echten temporären Git-Commits."""
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from checkpoint_review import review, review_revision


class GitRehydrationTests(unittest.TestCase):
    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], text=True).strip()

    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Local Test")
        self.git("config", "user.email", "test@example.invalid")
        (self.root / "api.py").write_text("old\n")
        (self.root / "docs.md").write_text("stable\n")
        self.git("add", ".")
        self.git("commit", "-qm", "base")
        self.previous = self.git("rev-parse", "HEAD")
        self.binding = {"base_commit": self.previous, "project": "fixture",
                        "scope": "repair", "lineage_id": "main"}
        self.checkpoint = {**self.binding, "example": False, "schema_version": 1, "strands": [
            {"id": "api", "status": "VERIFIZIERT", "depends_on": [], "return_anchor": "api",
             "evidence": ["independent test"], "contract_paths": ["api.py"]},
            {"id": "consumer", "status": "OFFEN", "depends_on": ["api"],
             "return_anchor": "consumer", "contract_paths": ["docs.md"]},
            {"id": "docs", "status": "OFFEN", "depends_on": [],
             "return_anchor": "docs", "contract_paths": ["docs.md"]},
        ]}

    def change_contract(self):
        (self.root / "api.py").write_text("new\n")
        self.git("commit", "-qam", "contract changed")
        self.binding["base_commit"] = self.git("rev-parse", "HEAD")

    def review(self):
        return review_revision(self.checkpoint, self.binding, {"api"}, self.root)

    def test_drift_invalidates_only_intersection_and_dependents(self):
        self.change_contract()
        result = self.review()
        self.assertEqual(result["recovery"]["api"], {"next": "REVALIDATE", "changed_paths": ["api.py"]})
        self.assertEqual(result["strands"]["consumer"], "WAITING_FOR_PREDECESSOR")
        self.assertEqual([x["id"] for x in result["candidates"]], ["docs"])

    def test_pending_write_requires_readback_even_on_same_revision(self):
        self.checkpoint["strands"][0]["write_outcome"] = "unknown"
        self.assertEqual(self.review()["recovery"]["api"]["next"], "READBACK")
        self.assertEqual(review(self.checkpoint, self.binding, {"api"})["strands"]["api"],
                         "READBACK_PENDING")

    def test_legacy_strand_without_watches_requires_binding_on_drift(self):
        del self.checkpoint["strands"][2]["contract_paths"]
        self.change_contract()
        self.assertEqual(self.review()["recovery"]["docs"]["next"], "BIND_EVIDENCE")

    def test_foreign_project_quarantined(self):
        self.binding["project"] = "foreign"
        self.assertEqual(self.review()["status"], "CONFLICT_QUARANTINE")

    def test_same_basis_preserves_valid_candidate(self):
        result = self.review()
        self.assertEqual(result["strands"]["api"], "CONFIRMED_COMPLETE")
        self.assertEqual(result["strands"]["consumer"], "CANDIDATE")

    def review_local(self):
        return review_revision(self.checkpoint, self.binding, {"api"}, self.root,
                               include_worktree=True)

    def test_unstaged_change_quarantines_only_dependents(self):
        (self.root / "api.py").write_text("changed locally\n")
        result = self.review_local()
        self.assertEqual(result["worktree"]["relevant_paths"], {"api.py": ["worktree"]})
        self.assertEqual(result["strands"]["consumer"], "WAITING_FOR_PREDECESSOR")
        self.assertEqual([x["id"] for x in result["candidates"]], ["docs"])
        self.assertEqual(self.review()["strands"]["api"], "CONFIRMED_COMPLETE")

    def test_index_and_worktree_are_both_observed_when_net_change_cancels(self):
        (self.root / "api.py").write_text("staged change\n")
        self.git("add", "api.py")
        (self.root / "api.py").write_text("old\n")
        self.assertEqual(self.review_local()["worktree"]["relevant_paths"],
                         {"api.py": ["index", "worktree"]})

    def test_untracked_dependency_with_spaces_reaches_its_strand(self):
        target = self.root / "new config"
        target.mkdir()
        (target / "input.toml").write_text("config = true\n")
        self.checkpoint["strands"][2]["contract_paths"] = ["new config"]
        result = self.review_local()
        self.assertEqual(result["recovery"]["docs"]["changed_paths"], ["new config/input.toml"])
        self.assertEqual(result["worktree"]["relevant_paths"], {"new config/input.toml": ["untracked"]})

    def test_alternate_checkout_cannot_speak_for_current_basis(self):
        self.change_contract()
        self.git("checkout", "--detach", self.previous)
        self.assertEqual(self.review_local()["binding_mismatches"], ["worktree_head"])

    def test_real_merge_conflict_stays_in_recovery(self):
        self.git("checkout", "-qb", "competing")
        (self.root / "api.py").write_text("competing\n")
        self.git("commit", "-qam", "competing contract")
        self.git("checkout", "-qb", "chosen", self.previous)
        self.change_contract()
        merge = subprocess.run(["git", "-C", str(self.root), "merge", "competing"],
                               capture_output=True, check=False)
        self.assertEqual(merge.returncode, 1)
        result = self.review_local()
        self.assertEqual(result["recovery"]["api"]["next"], "RESOLVE_CONFLICT")
        self.assertEqual(result["strands"]["consumer"], "WAITING_FOR_PREDECESSOR")
        self.assertEqual(result["worktree"]["relevant_paths"], {"api.py": ["conflict"]})

    def test_cli_checks_worktree_from_nested_path(self):
        subdir = self.root / "nested"
        subdir.mkdir()
        (self.root / "api.py").write_text("local change\n")
        with TemporaryDirectory() as directory:
            path = Path(directory)
            checkpoint, binding = path / "checkpoint.json", path / "binding.json"
            checkpoint.write_text(json.dumps(self.checkpoint), encoding="utf-8")
            binding.write_text(json.dumps(self.binding), encoding="utf-8")
            script = Path(__file__).resolve().parents[1] / "scripts" / "checkpoint_review.py"
            result = subprocess.check_output(
                [sys.executable, script, checkpoint, binding, "--git-repo", subdir,
                 "--include-worktree", "--confirmed-complete", "api"], text=True)
        self.assertEqual(json.loads(result)["recovery"]["api"]["changed_paths"], ["api.py"])

    def test_older_basis_quarantined(self):
        self.change_contract()
        self.checkpoint["base_commit"] = self.binding["base_commit"]
        self.binding["base_commit"] = self.previous
        self.assertEqual(self.review()["binding_mismatches"], ["commit_ancestry"])


if __name__ == "__main__":
    unittest.main()
