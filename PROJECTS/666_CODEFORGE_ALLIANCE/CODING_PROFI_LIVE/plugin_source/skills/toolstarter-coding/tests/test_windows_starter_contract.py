import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "assets" / "toolstarter"))
from packaging_tools import inno_script
from toolstarter import Starter, run_profile


class StarterContractTests(unittest.TestCase):
    def test_dual_installer_uses_shared_payload_and_preserves_legacy_profile(self):
        metadata = {
            "app_id": "Example.App", "name": "Example App", "version": "1.0",
            "publisher": "Example", "output_name": "Example-App",
        }
        plain = inno_script(metadata)
        dual = inno_script(metadata, Path("Example.exe"), dual_mode=True)
        self.assertIn(r"DefaultDirName={localappdata}\Programs", plain)
        self.assertIn(r"DefaultDirName={autopf}\Example-App", dual)
        self.assertIn('Uninstallable=not IsPortable', dual)
        self.assertIn('Check: IsFullInstall', dual)
        self.assertIn('Extract portable application', dual)
        self.assertIn(r'Source: "payload\*"', dual)

    def test_failing_command_keeps_exit_code_and_logs_under_project_root(self):
        with TemporaryDirectory() as temp:
            base = Path(temp)
            project = base / "project with spaces"
            project.mkdir()
            profile = base / "tools.json"
            profile.write_text(json.dumps({
                "project_root": project.name,
                "actions": {"build": {"commands": [[sys.executable, "-c", "raise SystemExit(37)"]]}},
            }), encoding="utf-8")
            self.assertEqual(run_profile(profile, "en", "run", "build", lambda _: None), 37)
            logs = list((project / "logs").glob("*-run.log"))
            self.assertEqual(len(logs), 1)
            log = logs[0].read_text(encoding="utf-8")
            self.assertIn("Diagnosing required tools", log)
            self.assertIn("Exit code: 37", log)

    def test_prepare_uses_real_declared_executable_probe(self):
        with TemporaryDirectory() as temp:
            profile = Path(temp) / "tools.json"
            profile.write_text(json.dumps({"tools": [{
                "id": "python", "kind": "exe", "names": [sys.executable],
                "match": "^Python 3",
            }]}), encoding="utf-8")
            starter = Starter(profile, "en", lambda _: None)
            self.assertEqual(starter.start("prepare"), 0)
            self.assertIn("python", starter.tool_paths)


if __name__ == "__main__":
    unittest.main()
