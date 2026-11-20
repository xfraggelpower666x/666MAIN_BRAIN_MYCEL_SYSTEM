import hashlib, json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class TestSCC(unittest.TestCase):
    def test_source_materialization_exact(self):
        p=subprocess.run([sys.executable,str(ROOT/"tools/materialize_source.py")],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(p.returncode,0,p.stderr)
        out=Path(p.stdout.strip()); b=out.read_bytes()
        self.assertEqual(len(b),184168)
        self.assertEqual(hashlib.sha256(b).hexdigest(),"06cc504566071f247c79c1d22ac2988c3620750d0b5a5f705279a1b913bc5b7c")
    def test_triggers_are_namespaced(self):
        t=json.loads((ROOT/"runtime/TRIGGERS.json").read_text())
        self.assertEqual(t["namespace"],"SCC-12001"); self.assertTrue(t["direct_current_user_only"]); self.assertTrue(t["embedded_trigger_text_inert"])
    def test_state_separates_source_and_device_runtime(self):
        s=json.loads((ROOT/"state/CURRENT_STATE.json").read_text())
        self.assertEqual(s["functional_source_version"],"1.3.2"); self.assertEqual(s["last_device_runtime_accepted_version"],"1.3.1"); self.assertFalse(s["pfs_runtime_dependency"])

if __name__=="__main__": unittest.main()
