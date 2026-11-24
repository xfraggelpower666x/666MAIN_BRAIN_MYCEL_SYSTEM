"""Lokale Regression der Veröffentlichung mit simuliertem Setup-Compiler."""

import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "assets" / "toolstarter"))
from packaging_tools import package, verify_publication


class PublicationTests(unittest.TestCase):
    def setUp(self):
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.app = self.root / "demo.exe"
        self.app.write_bytes(b"MZ payload A")
        (self.root / "LICENSE.txt").write_text("fixture", encoding="utf-8")
        profile = {
            "launch_mode": "direct",
            "metadata": {"app_id": "demo", "output_name": "demo", "version": "1.0",
                         "name": "Demo", "publisher": "Demo"},
            "entry": "demo.exe",
            "include": [{"from": name, "to": name} for name in ("demo.exe", "LICENSE.txt")],
            "required_runtime_ids": ["app"],
            "runtime": [{"id": "app", "files": ["demo.exe"], "licenses": ["LICENSE.txt"],
                         "probes": [{"exe": "demo.exe"}]}],
        }
        self.starter = SimpleNamespace(config={"package": profile}, root=self.root, env={},
                                       probe=lambda *_: (True, "fixture"),
                                       execute=self.compiler, log=lambda *_: None, label=lambda x: x)
        self.output = self.root / "dist/toolstarter"
        self.receipt = self.output / "demo-bundle-manifest.json"
        self.portable = self.output / "demo-Portable.zip"
        self.setup = self.output / "demo-Setup.exe"

    def compiler(self, args):
        target = Path(next(a[2:] for a in args if a.startswith("-O")))
        stem = next(a[2:] for a in args if a.startswith("-F"))
        (target / f"{stem}.exe").write_bytes(b"MZ setup fixture " + self.app.read_bytes())
        return 0, "fixture"

    def build(self, mode):
        self.assertEqual(package(self.starter, mode), 0)
        return verify_publication(self.receipt)

    def test_fresh_single_and_matching_sibling(self):
        one = self.build("portable")
        self.assertEqual(set(one["artifacts"]), {"portable"})
        both = self.build("setup")
        self.assertEqual(set(both["artifacts"]), {"portable", "setup"})
        self.assertEqual(one["payload_sha256"], both["payload_sha256"])
        self.assertEqual(one["artifacts"]["portable"], both["artifacts"]["portable"])

    def test_changed_single_leaves_previous_set_intact(self):
        self.build("both")
        paths = (self.portable, self.setup, self.receipt)
        previous = [path.read_bytes() for path in paths]
        self.app.write_bytes(b"MZ payload B")
        for mode in ("portable", "setup"):
            with self.assertRaisesRegex(ValueError, "cannot be paired"):
                package(self.starter, mode)
            self.assertEqual([path.read_bytes() for path in paths], previous)
        repaired = self.build("both")
        self.assertEqual(set(repaired["artifacts"]), {"portable", "setup"})
        with ZipFile(self.portable) as archive:
            self.assertEqual(archive.read("demo.exe"), self.app.read_bytes())
            self.assertNotIn("artifacts", json.loads(archive.read("bundle-manifest.json")))

    def test_legacy_or_changed_sibling_requires_joint_build(self):
        self.build("both")
        self.receipt.unlink()
        with self.assertRaisesRegex(ValueError, "cannot be paired"):
            package(self.starter, "portable")
        self.build("both")
        self.setup.write_bytes(b"MZ changed")
        with self.assertRaisesRegex(ValueError, "cannot be paired"):
            package(self.starter, "portable")
        with self.assertRaisesRegex(ValueError, "readback mismatch"):
            verify_publication(self.receipt)

    def test_lock_preserves_current_release(self):
        before = self.build("both")
        lock = self.output / ".demo-publish.lock"
        lock.mkdir()
        with self.assertRaisesRegex(ValueError, "Publication locked"):
            package(self.starter, "both")
        self.assertEqual(verify_publication(self.receipt), before)
        self.assertTrue(lock.is_dir())

    def test_interruption_cannot_validate_mixed_output(self):
        self.build("both")
        self.app.write_bytes(b"MZ payload B")
        original_replace = Path.replace

        def interrupted(path, destination):
            if destination == self.setup:
                raise OSError("fixture interruption")
            return original_replace(path, destination)

        with patch.object(Path, "replace", interrupted):
            with self.assertRaisesRegex(OSError, "fixture interruption"):
                package(self.starter, "both")
        with self.assertRaisesRegex(ValueError, "readback mismatch"):
            verify_publication(self.receipt)
        self.build("both")


if __name__ == "__main__":
    unittest.main()
