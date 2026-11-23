import concurrent.futures
import hashlib
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
import cls_livecircle as cls
import shared_archive as shared


class SharedArchiveTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.private = Path(tmp.name)
        self.db = self.private / "inbox.sqlite3"
        self.root = self.private / "cls"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns("__pycache__", ".git"))
        fixture = self.root / "releases/1.24.2"
        manifest = cls.read(fixture / "MANIFEST.json")
        cls.write(self.root / "CURRENT_POINTER.json",
                  cls.pointer_for(self.root, fixture, "1.24.2", manifest["domains"]))

    def add(self, client, ident, domain):
        return shared.submit(self.db, client, ident, domain,
                             {"id": "original", "title": "Test", "source_text": "666CLS UPDATE"})

    def test_parallel_submissions_and_promotion(self):
        events = [(client, str(i), domain) for client, domain in
                  (("framework-a", "LYRICS"), ("framework-b", "STORIES")) for i in range(12)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            receipts = list(executor.map(lambda event: self.add(*event), events))
        self.assertEqual(len({item["id"] for item in receipts}), 24)
        self.assertEqual(len(shared.pending(self.db, self.root)), 24)
        before = cls.rehydrate(self.root)
        self.assertEqual(before["total"], 0)
        releases = (self.root / "releases").iterdir()
        major, minor, patch = max(cls.version_key(p.name) for p in releases if p.is_dir())
        next_version = f"{major}.{minor}.{patch + 1}"
        selected = ["framework-a/0", "framework-b/0"]
        data = shared.prepare(self.db, self.root, next_version, selected)
        path = self.private / "candidate.json"
        cls.write(path, data)
        finished = cls.update(self.root, path, self.private / "backups")
        self.assertEqual(finished["domains"], {"LYRICS": 1, "RAW_MATERIAL": 0, "STORIES": 1, "TEXT": 0})
        self.assertEqual(len(shared.pending(self.db, self.root)), 22)
        self.assertEqual(shared.live_records(self.root, finished, "LYRICS")[0]["archive_provenance"][
            "framework_id"], "framework-a")

    def test_idempotent_and_conflicting_submission(self):
        first = self.add("framework-a", "same", "LYRICS")
        second = self.add("framework-a", "same", "LYRICS")
        self.assertEqual(first["receipt"], second["receipt"])
        self.assertTrue(second["idempotent"])
        with self.assertRaisesRegex(ValueError, "bereits"):
            self.add("framework-a", "same", "STORIES")

    def test_sensitive_submission_stays_private(self):
        marker = "fixture-only-credential"
        item = shared.submit(self.db, "framework-a", "hold", "TEXT",
                             {"title": "Nur für die Gegenprobe", "source_text": f"password: {marker}"})
        self.assertEqual(item["status"], "HOLD")
        entry = shared.pending(self.db, self.root)[0]
        self.assertEqual(entry["record"]["source_vault_ref"], "SOURCE_VAULT_ONLY")
        self.assertNotIn(marker, repr(entry))
        self.assertNotIn("title", entry["record"])
        with self.assertRaisesRegex(ValueError, "HOLD / SOURCE_VAULT_ONLY"):
            shared.prepare(self.db, self.root, "1.24.99", [item["receipt"]])

    def test_access_permissions(self):
        policy = self.private / "clients.json"
        token = "a" * 40
        cls.write(policy, {"system_id": cls.SYSTEM, "clients": {
            "framework-a": {"token_sha256": hashlib.sha256(token.encode()).hexdigest(),
                            "read": ["LYRICS"], "submit": ["STORIES"]}}})
        shared.authorize(policy, "framework-a", token, "read", "LYRICS")
        shared.authorize(policy, "framework-a", token, "submit", "STORIES")
        for key, action, domain in (("b" * 40, "read", "LYRICS"), (token, "read", "STORIES"),
                                    (token, "submit", "LYRICS"), (token, "review", None)):
            with self.assertRaisesRegex(ValueError, "Zugriff verweigert"):
                shared.authorize(policy, "framework-a", key, action, domain)
