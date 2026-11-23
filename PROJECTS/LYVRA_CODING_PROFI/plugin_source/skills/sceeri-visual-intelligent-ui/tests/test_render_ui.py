import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("render_ui", ROOT / "scripts/render_ui.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def example():
    return {
        "title": "Beispiel", "basis": "Nutzereingabe", "gaps": ["Wert offen"],
        "views": [
            {"id": "story", "title": "Story", "summary": "Kurz",
             "kind": "narrative", "route_terms": ["story"], "source": "Nutzereingabe",
             "status": "VERIFIZIERT", "items": [{"label": "A", "text": "B"}]},
            {"id": "energy", "title": "Energie", "summary": "Kurz",
             "kind": "bars", "route_terms": ["energie"], "source": "Screenshot",
             "status": "ABGELEITET", "data_kind": "schematic",
             "caption": "qualitativ, keine Messwerte",
             "bars": [{"label": "A", "level": 40}, {"label": "B", "level": 80}]}
        ]
    }


class RendererTests(unittest.TestCase):
    def test_valid_and_html_escaped(self):
        data = example()
        data["views"][0]["items"][0]["text"] = "</script><script>alert(1)</script>"
        template = (ROOT / "assets/ui-template.html").read_text()
        result = module.render(data, template)
        self.assertIn("\\u003c/script\\u003e", result)
        self.assertNotIn("</script><script>alert", result)
        self.assertIn('data-nav', result)
        self.assertIn('b.dataset.view=view.id', result)
        self.assertEqual(len(json.loads(result.split('data-ui-data>')[1].split('</script>')[0])["views"]), 2)

    def test_embedded_formats_and_literal_marker_in_project_data(self):
        data = example()
        data["views"][0]["items"][0]["text"] = "__SCEERI_FORMAT_MENU__"
        template = (ROOT / "assets/ui-template.html").read_text()
        result = module.render(data, template)
        self.assertIn('data-ui-mode="project"', result)
        self.assertIn('data-ui-mode="formats"', result)
        self.assertIn('id="lyvra-intelligent-ui"', result)
        encoded = result.split('data-ui-data>')[1].split('</script>')[0]
        self.assertEqual(json.loads(encoded)["views"][0]["items"][0]["text"], "__SCEERI_FORMAT_MENU__")
        self.assertEqual(result.count("__SCEERI_FORMAT_MENU__"), 1)

    def test_chart_and_daemon_assets_are_embedded(self):
        data = example()
        data["chart"] = {"intent": "trend", "rows": "A;1\nB;", "unit": "ms"}
        data["companion"] = {"status": "READBACK_PENDING", "start_mode": "charts"}
        result = module.render(data, (ROOT / "assets/ui-template.html").read_text())
        self.assertIn('id="sceeri-visual-daemon"', result)
        self.assertIn('id="sceeri-chart-workbench"', result)
        self.assertIn('data-template', result)
        self.assertNotIn("__SCEERI_CHARTS__", result)
        data["chart"]["intent"] = "unknown"
        with self.assertRaisesRegex(ValueError, "chart.intent"):
            module.validate(data)
        data.pop("chart")
        data["companion"]["start_mode"] = " charts "
        with self.assertRaisesRegex(ValueError, "companion.start_mode"):
            module.validate(data)

    def test_handoff_restores_only_a_matching_view(self):
        data = example()
        data["companion"] = {"project_key": "owner/repo", "source_revision": "rev-1", "status": "OFFEN"}
        checkpoint = {"schema": "scevi.visual.handoff.1", "project_key": "owner/repo",
                      "source_revision": "rev-1", "mode": "charts", "status": "VERIFIZIERT"}
        result = module.apply_checkpoint(data, checkpoint)
        self.assertEqual(result["companion"]["start_mode"], "charts")
        self.assertEqual(result["companion"]["status"], "OFFEN")
        self.assertNotIn("start_mode", data["companion"])
        self.assertEqual(result["views"], data["views"])
        with self.assertRaisesRegex(ValueError, "source_revision"):
            module.apply_checkpoint(data, {**checkpoint, "source_revision": "rev-0"})
        with self.assertRaisesRegex(ValueError, "project_key"):
            module.apply_checkpoint(data, {**checkpoint, "project_key": "other/repo"})
        data["companion"]["start_mode"] = "formats"
        self.assertEqual(module.apply_checkpoint(data, checkpoint)["companion"]["start_mode"], "formats")

    def test_handoff_restores_selected_project_view_without_overwriting_explicit_view(self):
        data = example()
        data["companion"] = {"project_key": "demo", "source_revision": "rev"}
        checkpoint = {"schema": "scevi.visual.handoff.1", "project_key": "demo",
                      "source_revision": "rev", "mode": "charts", "view_id": "energy"}
        self.assertEqual("energy", module.apply_checkpoint(data, checkpoint)["companion"]["start_view"])
        data["companion"]["start_view"] = "story"
        self.assertEqual("story", module.apply_checkpoint(data, checkpoint)["companion"]["start_view"])
        with self.assertRaisesRegex(ValueError, "unbekannte Projektansicht"):
            module.apply_checkpoint(data, {**checkpoint, "view_id": "missing"})

    def test_handoff_keeps_visual_form_for_matching_project_and_revision(self):
        data = example()
        data["companion"] = {"project_key": "demo", "source_revision": "rev-1"}
        checkpoint = {"schema": "scevi.visual.handoff.1", "project_key": "demo",
                      "source_revision": "rev-1", "mode": "formats", "format_id": "iceberg",
                      "draft": "Keine Formulareingaben übernehmen"}
        result = module.apply_checkpoint(data, checkpoint)
        self.assertEqual("iceberg", result["companion"]["start_format"])
        self.assertNotIn("draft", result["companion"])
        self.assertNotIn("start_format", module.apply_checkpoint(
            data, {**checkpoint, "format_id": ["iceberg"]})["companion"])
        self.assertNotIn("start_format", module.apply_checkpoint(
            data, {**checkpoint, "mode": "charts"})["companion"])
        with self.assertRaisesRegex(ValueError, "source_revision"):
            module.apply_checkpoint(data, {**checkpoint, "source_revision": "rev-2"})
        data["companion"]["start_format"] = "canvas"
        self.assertEqual("canvas", module.apply_checkpoint(data, checkpoint)["companion"]["start_format"])

    def test_actions_require_known_acyclic_dependencies_and_evidence(self):
        data = example()
        common = {"kind": "verify", "label": "Nachweis prüfen", "source": "Akte",
                  "reason": "Beleg ist offen", "effect": "Ergebnis wird prüfbar",
                  "countercheck": "Erwartete Ausgabe prüfen"}
        first = {**common, "id": "read", "status": "VERIFIZIERT"}
        second = {**common, "id": "then", "requires": ["read"], "view_id": "story"}
        self.assertEqual([first, second], module.validate({**data, "actions": [first, second]})["actions"])
        for invalid, message in (
            ([first, {**second, "requires": ["missing"]}], "unbekannter Vorgänger"),
            ([{**first, "requires": ["then"]}, second], "zyklische Abhängigkeit"),
            ([first, {**second, "source": ""}], "actions.source"),
        ):
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                module.validate({**data, "actions": invalid})

    def test_export_is_neutral_and_refuses_an_existing_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "intelligent-ui"
            export = [sys.executable, str(ROOT / "scripts/export_template.py"), str(target)]
            subprocess.run(export, check=True, capture_output=True)
            output = target / "demo.html"
            subprocess.run([sys.executable, str(target / "scripts/render_ui.py"),
                            str(target / "view.example.json"), str(output), "--standalone"],
                           check=True, capture_output=True)
            result = output.read_text(encoding="utf-8")
            self.assertTrue(result.startswith("<!doctype html>"))
            self.assertIn('"handoff_format":"neutral"', result)
            self.assertIn('id="sceeri-visual-daemon"', result)
            self.assertNotEqual(subprocess.run(export, capture_output=True).returncode, 0)
            self.assertEqual(output.read_text(encoding="utf-8"), result)

    def test_reject_unproven_chart(self):
        data = example()
        data["views"][1]["status"] = "VERIFIZIERT"
        with self.assertRaisesRegex(ValueError, "schematisch"):
            module.validate(data)

    def test_reject_duplicate_ids_and_missing_source(self):
        data = example()
        data["views"][1]["id"] = "story"
        with self.assertRaisesRegex(ValueError, "doppelt"):
            module.validate(data)
        data = example()
        data["views"][0]["source"] = ""
        with self.assertRaisesRegex(ValueError, "source"):
            module.validate(data)


if __name__ == "__main__":
    unittest.main()

