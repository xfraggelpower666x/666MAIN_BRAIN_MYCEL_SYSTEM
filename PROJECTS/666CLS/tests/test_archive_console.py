import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from archive_console import Console
from cls_livecircle import SYSTEM, read, rehydrate, version_key, write


class ConsoleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.private = Path(self.temp.name)
        self.console = Console(ROOT, self.private, "reviewer")
        write(self.private / "clients.json", {"system_id": SYSTEM, "clients": {
            "framework-a": {"read": ["LYRICS"], "submit": ["TEXT"]}}})
        write(self.private / "frameworks.json", {"frameworks": {"framework-a": {
            "name": "Framework A", "authority": "Testquelle", "revision": "test-1",
            "actions": {"start": {"mode": "chat", "trigger": "FRAMEWORK-A SYSTEMSTART"},
                        "resume": {"mode": "local", "trigger": "FRAMEWORK-A WEITER",
                                   "argv": [sys.executable, "-c", "print('Adapter bestätigt')"],
                                   "cwd": str(self.private)}}}}})

    def action(self, command, **values):
        return self.console.handle({"framework": "framework-a", "command": command, **values})

    def test_registry_and_native_actions(self):
        self.assertEqual(self.console.model()["frameworks"][0]["id"], "framework-a")
        self.assertEqual(self.action("framework", action="start")["trigger"], "FRAMEWORK-A SYSTEMSTART")
        self.assertIn("Adapter bestätigt", self.action("framework", action="resume")["output"])
        with self.assertRaisesRegex(ValueError, "nicht registriert"):
            self.action("framework", action="update")

    def test_invalid_action_is_absent_from_runnable_model(self):
        path = self.private / "frameworks.json"
        config = read(path)
        config["frameworks"]["framework-a"]["actions"]["start"]["mode"] = "unbekannt"
        write(path, config)
        with self.assertRaisesRegex(ValueError, "Aktionsmodus"):
            self.console.model()

    def test_archive_permissions_and_private_review(self):
        self.assertIn("records", self.action("read", domain="LYRICS"))
        with self.assertRaisesRegex(ValueError, "Berechtigung"):
            self.action("read", domain="TEXT")
        received = self.action("submit", domain="TEXT", receipt="note", title="Notiz", text="Privat")
        pending = self.action("pending")["entries"]
        self.assertEqual(pending[0]["receipt"], received["receipt"])
        self.assertEqual(pending[0]["record"]["submitted_by"], "reviewer")
        current = rehydrate(ROOT)
        major, minor, patch = version_key(current["version"])
        version = f"{major}.{minor}.{patch + 1}"
        made = self.action("prepare", version=version, receipts=[received["receipt"]])
        result = json.loads((self.private / made["file"]).read_text(encoding="utf-8"))
        self.assertEqual(result["records"]["TEXT"][-1]["source_text"], "Privat")
        self.assertEqual(rehydrate(ROOT), current)
        with self.assertRaises(FileExistsError):
            self.action("prepare", version=version, receipts=[received["receipt"]])

    def test_private_overview_reflects_inbox_without_exposing_contents(self):
        self.action("submit", domain="TEXT", receipt="review-test", title="Interne Probe",
                    text="Interner Beispieltext")
        html = self.private / "overview.html"
        self.console.overview(html)
        markup = html.read_text(encoding="utf-8")
        self.assertIn("1 Einreichungen zur Prüfung", markup)
        self.assertNotIn("Interner Beispieltext", markup)
