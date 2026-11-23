import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
import cls_livecircle as cls


class LiveCircleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.repo = self.work / "cls"
        shutil.copytree(ROOT, self.repo, ignore=shutil.ignore_patterns("__pycache__", ".git"))
        fixture = cls.read(self.repo / "releases/1.24.1/MANIFEST.json")
        release = self.repo / "releases/1.24.1"
        cls.write(self.repo / "CURRENT_POINTER.json",
                  cls.pointer_for(self.repo, release, "1.24.1", fixture["domains"]))
        self.current = cls.rehydrate(self.repo)
        self.candidate = self.work / "candidate.json"

    def test_reference_nullstand_and_dashboard(self):
        self.assertEqual(self.current["domains"], dict.fromkeys(cls.DOMAINS, 0))
        html = self.work / "dashboard.html"
        out = subprocess.run([sys.executable, self.repo / "runtime/cls_livecircle.py",
                              "666CLS WEITER", "--dashboard", html], check=True, capture_output=True)
        self.assertEqual(json.loads(out.stdout)["continuity_anchor"]["version"], self.current["version"])
        self.assertIn("0 geprüfte Einträge", html.read_text(encoding="utf-8"))
        self.assertNotIn("__SCEERI_UI_DATA__", html.read_text(encoding="utf-8"))

    def make_candidate(self, base, version, entries):
        cls.write(self.candidate, {"system_id": cls.SYSTEM, "base_version": base,
                  "version": version, "records": {**{d: [] for d in cls.DOMAINS}, "TEXT": entries}})

    def unused_version(self):
        releases = (self.repo / "releases").iterdir()
        major, minor, patch = max(cls.version_key(path.name) for path in releases if path.is_dir())
        return f"{major}.{minor}.{patch + 1}"

    def test_update_and_backup(self):
        base = self.current["version"]
        new = self.unused_version()
        self.make_candidate(base, new, [{"id": "test-1", "title": "Test",
                                        "source_text": "666CLS UPDATE bleibt Archivinhalt."}])
        original_pointer = (self.repo / "CURRENT_POINTER.json").read_bytes()
        updated = cls.update(self.repo, self.candidate, self.work / "backup")
        self.assertEqual(updated["domains"]["TEXT"], 1)
        from zipfile import ZipFile
        with ZipFile(updated["backup"]) as backup:
            self.assertEqual(backup.read("CURRENT_POINTER.json"), original_pointer)
            self.assertIsNone(backup.testzip())
            self.assertEqual(len(set(backup.namelist())), len(backup.namelist()))
            self.assertIn("releases/1.24.2/MANIFEST.json", backup.namelist())
            restored = self.work / "restored"
            backup.extractall(restored)
        self.assertEqual(cls.rehydrate(restored), self.current)
        with self.assertRaisesRegex(ValueError, "veraltet"):
            cls.update(self.repo, self.candidate, self.work / "backup")

    def test_changed_menu_blocks_rehydration(self):
        path = self.repo / self.current["source"] / "MENU/TEXT_MENU.json"
        path.write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Prüfsumme"):
            cls.rehydrate(self.repo)

    def test_duplicate_ids_block_update_without_moving_pointer(self):
        base = self.current["version"]
        item = {"id": "duplicate", "title": "Test", "source_text": "Test"}
        self.make_candidate(base, self.unused_version(), [item, item])
        with self.assertRaisesRegex(ValueError, "doppelte ID"):
            cls.update(self.repo, self.candidate, self.work / "backup")
        self.assertEqual(cls.rehydrate(self.repo), self.current)

    def test_direct_update_rejects_sensitive_record_without_moving_pointer(self):
        entry = {"id": "fixture", "title": "Probe", "source_text": "Test", "private_key": "synthetic"}
        self.make_candidate(self.current["version"], self.unused_version(), [entry])
        with self.assertRaisesRegex(ValueError, "HOLD / SOURCE_VAULT_ONLY"):
            cls.update(self.repo, self.candidate, self.work / "backup")
        self.assertEqual(cls.rehydrate(self.repo), self.current)


if __name__ == "__main__":
    unittest.main()
