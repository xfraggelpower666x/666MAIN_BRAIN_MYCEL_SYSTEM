import copy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_run_evidence.py"
SCOPE = {"schema": 1, "project": "fixture", "revision": "revision-1", "run_id": "run-1"}


class RunEvidenceTests(unittest.TestCase):
    def setUp(self):
        scratch = TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        self.outputs = self.root / "outputs"
        self.outputs.mkdir()
        observed = subprocess.run(
            [sys.executable, "-c", "print('known effect', end='')"],
            stdout=subprocess.PIPE, check=False,
        )
        (self.outputs / "output.txt").write_bytes(observed.stdout)
        self.contract = {**SCOPE, "steps": [
            {"id": "build", "requires": [], "exit_code": 0, "artifacts": {
                "output.txt": sha256(b"known effect").hexdigest(),
            }},
            {"id": "handoff", "requires": ["build"], "exit_code": 0, "artifacts": {}},
        ]}
        self.receipt = {**SCOPE, "steps": [
            {"id": "build", "state": "completed", "exit_code": observed.returncode},
            {"id": "handoff", "state": "completed", "exit_code": 0},
        ]}

    def check(self):
        files = (self.root / "contract.json", self.root / "receipt.json")
        for path, value in zip(files, (self.contract, self.receipt)):
            path.write_text(json.dumps(value), encoding="utf-8")
        proc = subprocess.run([sys.executable, SCRIPT, *files, self.outputs],
                              check=False, capture_output=True, text=True)
        return proc.returncode, json.loads(proc.stdout)

    def test_matches_observed_file_and_separate_expectation(self):
        code, result = self.check()
        self.assertEqual(code, 0)
        self.assertTrue(result["passed"])

    def test_zero_exit_does_not_hide_wrong_artifact(self):
        (self.outputs / "output.txt").write_text("wrong effect")
        code, result = self.check()
        self.assertEqual(code, 1)
        self.assertEqual(result["steps"]["build"]["status"], "FEHLGESCHLAGEN")
        self.assertEqual(result["steps"]["handoff"]["status"], "BLOCKIERT")

    def test_timeout_blocks_handoff_even_with_matching_file(self):
        self.receipt["steps"][0]["state"] = "timeout"
        code, result = self.check()
        self.assertEqual(code, 1)
        self.assertEqual(result["steps"]["build"]["status"], "OFFEN")
        self.assertEqual(result["steps"]["handoff"]["status"], "BLOCKIERT")

    def test_missing_artifact_is_open(self):
        (self.outputs / "output.txt").unlink()
        self.assertEqual(self.check()[1]["steps"]["build"]["status"], "OFFEN")

    def test_revision_mismatch_is_invalid(self):
        self.receipt["revision"] = "older"
        self.assertEqual(self.check()[0], 2)

    def test_cycles_are_invalid(self):
        self.contract["steps"][0]["requires"] = ["handoff"]
        self.assertEqual(self.check()[0], 2)

    def test_path_outside_root_is_invalid(self):
        checks = self.contract["steps"][0]["artifacts"]
        checks["../outside"] = checks.pop("output.txt")
        self.assertEqual(self.check()[0], 2)

    def test_duplicate_step_rejects_ambiguous_evidence(self):
        self.receipt["steps"].append(copy.copy(self.receipt["steps"][0]))
        self.assertEqual(self.check()[0], 2)


if __name__ == "__main__":
    unittest.main()
