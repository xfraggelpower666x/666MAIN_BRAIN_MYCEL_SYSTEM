import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from cls_livecircle import SYSTEM, read, rehydrate, write
from dashboard import dashboard_data, render_dashboard
from shared_archive import submit


class ArchiveDashboardTests(unittest.TestCase):
    def test_menu_distinguishes_unread_empty_and_open(self):
        state = rehydrate(ROOT)
        for counts, label, expected, status in (
            (None, "Inbox-Status abrufen", "Inbox für diese Ansicht nicht gelesen", "OFFEN"),
            (dict.fromkeys(state["domains"], 0), "Inbox später erneut lesen", "0 Einreichungen zur Prüfung", "VERIFIZIERT"),
            ({**dict.fromkeys(state["domains"], 0), "LYRICS": 2},
             "Einreichungen prüfen", "2 Einreichungen zur Prüfung", "VERIFIZIERT"),
        ):
            with self.subTest(counts=counts):
                data = dashboard_data(ROOT, state, counts)
                views = {v["id"]: v for v in data["views"]}
                self.assertEqual(set(views), {"archive", "inbox", "frameworks", "audit"})
                self.assertEqual(views["inbox"]["summary"], expected)
                self.assertEqual(views["inbox"]["status"], status)
                self.assertEqual(next(a["label"] for a in data["actions"] if a["view_id"] == "inbox"), label)

    def test_html_and_revision_bound_handoff(self):
        state = rehydrate(ROOT)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            checkpoint = path / "checkpoint.json"
            html = path / "review.html"
            write(checkpoint, {"schema": "scevi.visual.handoff.1", "project_key": state["system_id"],
                               "source_revision": state["version"], "mode": "project", "view_id": "inbox"})
            render_dashboard(ROOT, state, html, checkpoint, inbox=dict.fromkeys(state["domains"], 0))
            raw = html.read_text(encoding="utf-8")
            match = re.search(r'<script[^>]+data-ui-data[^>]*>(.*?)</script>', raw, re.DOTALL)
            self.assertIsNotNone(match)
            data = json.loads(match[1])
            self.assertEqual(data["companion"]["start_view"], "inbox")
            self.assertNotIn("__SCEERI_UI_DATA__", raw)
            altered = read(checkpoint)
            altered["source_revision"] = "0.0.0"
            write(checkpoint, altered)
            with self.assertRaisesRegex(ValueError, "source_revision"):
                render_dashboard(ROOT, state, html, checkpoint)

    def test_private_dashboard_cli_requires_reviewer_and_omits_contents(self):
        with tempfile.TemporaryDirectory() as directory:
            private = Path(directory)
            secret_text = "PRIVATE-FIXTURE-CONTENT"
            submit(private / "inbox.sqlite3", "framework-a", "hidden-receipt", "TEXT",
                   {"title": secret_text, "source_text": secret_text})
            token = "t" * 48
            digest = hashlib.sha256(token.encode()).hexdigest()
            write(private / "clients.json", {"system_id": SYSTEM, "clients": {
                "review": {"token_sha256": digest, "review": True},
                "reader": {"token_sha256": digest, "read": ["TEXT"]},
            }})
            output = private / "review.html"
            command = [sys.executable, str(ROOT / "runtime/shared_archive.py"),
                       "--private-dir", directory, "--client"]
            env = {**os.environ, "CLS_ARCHIVE_TOKEN": token}
            denied = subprocess.run([*command, "reader", "dashboard", str(output)],
                                    env=env, capture_output=True)
            self.assertEqual(denied.returncode, 1)
            self.assertFalse(output.exists())
            result = subprocess.run([*command, "review", "dashboard", str(output)],
                                    env=env, capture_output=True, check=True)
            self.assertEqual(json.loads(result.stdout)["inbox_counts"]["TEXT"], 1)
            html = output.read_text(encoding="utf-8")
            self.assertNotIn(secret_text, html)
            self.assertNotIn("hidden-receipt", html)
