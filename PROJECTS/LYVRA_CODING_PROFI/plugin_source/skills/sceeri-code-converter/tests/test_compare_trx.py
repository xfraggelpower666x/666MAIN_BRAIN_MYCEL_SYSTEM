import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "compare_trx.py"


def trx(outcome="Passed", count=1, label="case"):
    return f"""<TestRun xmlns="http://microsoft.com/schemas/VisualStudio/TeamTest/2010">
<TestDefinitions><UnitTest id="ID"><TestMethod className="Suite"/></UnitTest></TestDefinitions>
<Results><UnitTestResult testId="ID" testName="{label}" outcome="{outcome}"/></Results>
<ResultSummary><Counters total="{count}"/></ResultSummary></TestRun>"""


class CompareTrxTests(unittest.TestCase):
    def compare(self, candidate, renames=None):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            baseline = root / "before.trx"
            after = root / "after.trx"
            baseline.write_text(trx(), encoding="utf-8")
            after.write_text(candidate, encoding="utf-8")
            command = [sys.executable, SCRIPT, baseline, after]
            if renames is not None:
                mapping = root / "renames.json"
                mapping.write_text(json.dumps(renames), encoding="utf-8")
                command += ["--renames", mapping]
            return subprocess.run(command, check=False, capture_output=True, text=True)

    def test_same_outcomes(self):
        proc = self.compare(trx())
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(json.loads(proc.stdout)["parity"])

    def test_same_count_but_test_becomes_skipped(self):
        proc = self.compare(trx(outcome="NotExecuted"))
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(json.loads(proc.stdout)["changed"]["Suite::case"]["candidate"], "NotExecuted")

    def test_same_count_but_test_replaced(self):
        proc = self.compare(trx(label="other"))
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(json.loads(proc.stdout)["missing"], ["Suite::case"])

    def test_explicit_rename(self):
        self.assertEqual(self.compare(trx(label="other"), {"Suite::case": "Suite::other"}).returncode, 0)

    def test_incomplete_results(self):
        self.assertEqual(self.compare(trx(count=2)).returncode, 2)


if __name__ == "__main__":
    unittest.main()
