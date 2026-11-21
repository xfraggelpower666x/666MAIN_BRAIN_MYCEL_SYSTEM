"""MAIN BRAIN R05: native/Workbench handoff priority and real CLI-to-HTML regression."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
WORKBENCH = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORKBENCH / "scripts"))
from mycel_bridge import project
from render_ui import apply_checkpoint, validate

HEAD = "a" * 40
MENU_PATH = ROOT / "UI/INTELLIGENT_UI/MENU_REGISTRY.json"
BRIDGE = WORKBENCH / "scripts/mycel_bridge.py"
RENDERER = WORKBENCH / "scripts/render_ui.py"


def state():
    return {
        "schema": "psyllo.guidance-state.1",
        "owner": "666MAIN BRAIN MYCEL SYSTEM",
        "source_head": HEAD,
        "active_scope": "666MAIN-BRAIN",
        "lineage_id": "r05-regression",
        "phase": "Verification",
        "evidence_class": "PARTIAL",
        "open_obligations": ["plugin-host-gate"],
        "blockers": [],
        "last_verified_step": "Current Pointer checked",
        "next_action": {"label": "Verify host parity"},
    }


def fixture():
    return project(json.loads(MENU_PATH.read_text(encoding="utf-8")), state())


def checkpoint(mode="formats", view_id="guidance"):
    return {
        "schema": "scevi.visual.handoff.1",
        "project_key": "666MAIN-BRAIN",
        "source_revision": HEAD,
        "mode": mode,
        "view_id": view_id,
    }


class RendererHandoffR05(unittest.TestCase):
    def test_real_menu_bridge_contract_valid(self):
        data = validate(fixture())
        self.assertEqual(len(data["views"]), 6)
        self.assertEqual(len(data["actions"]), 4)
        self.assertNotIn("blocker", data["companion"])

    def test_valid_workbench_checkpoint_restores_mode(self):
        data = apply_checkpoint(fixture(), checkpoint())
        self.assertEqual(data["companion"]["start_mode"], "formats")
        self.assertEqual(data["companion"]["start_view"], "guidance")

    def test_native_handoff_view_has_priority_over_workbench(self):
        menu = json.loads(MENU_PATH.read_text(encoding="utf-8"))
        native_handoff = {
            "schema": "psyllo.ui-handoff.1",
            "project_id": "666MAIN-BRAIN",
            "source_commit": HEAD,
            "lineage_id": "r05-regression",
            "view_id": "development",
        }
        original = project(menu, state(), handoff=native_handoff)
        changed = apply_checkpoint(original, checkpoint("charts", "guidance"))
        self.assertEqual(changed["companion"]["start_view"], "development")
        self.assertEqual(changed["companion"]["start_mode"], "charts")

    def test_wrong_revision_cannot_restore(self):
        bad = checkpoint()
        bad["source_revision"] = "b" * 40
        with self.assertRaises(ValueError):
            apply_checkpoint(fixture(), bad)

    def test_wrong_project_cannot_restore(self):
        bad = checkpoint()
        bad["project_key"] = "foreign-system"
        with self.assertRaises(ValueError):
            apply_checkpoint(fixture(), bad)

    def test_real_bridge_to_standalone_html(self):
        with tempfile.TemporaryDirectory(prefix="mycel-r05-") as folder:
            tmp = Path(folder)
            state_file = tmp / "guidance.json"
            wb_file = tmp / "bridge.json"
            html_file = tmp / "mycel.html"
            state_file.write_text(json.dumps(state()), encoding="utf-8")
            subprocess.run([
                sys.executable, str(BRIDGE), "--menu", str(MENU_PATH),
                "--state", str(state_file), "--output", str(wb_file),
            ], check=True, capture_output=True, text=True)
            subprocess.run([
                sys.executable, str(RENDERER), str(wb_file), str(html_file),
                "--standalone",
            ], check=True, capture_output=True, text=True)
            html = html_file.read_text(encoding="utf-8")
            self.assertIn("<!doctype html>", html)
            self.assertIn("666MAIN BRAIN STATUS", html)
            self.assertIn("666MAIN BRAIN WEITER", html)
            self.assertIn("<noscript>", html)
            self.assertNotIn("__SCEERI_UI_DATA__", html)
            self.assertNotIn("__SCEERI_COMPANION__", html)


if __name__ == "__main__":
    unittest.main()
