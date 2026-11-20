"""Übersetzt den geprüften 666CLS-Stand in die gelieferte Visual-Oberfläche."""
from pathlib import Path
import sys

from cls_livecircle import read

RENDERER = Path(__file__).resolve().parents[1] / "integrations/visual/scripts"
sys.path.insert(0, str(RENDERER))
from render_ui import ASSETS, apply_checkpoint, render


def render_dashboard(root, status, output, checkpoint=None):
    source = status["source"] + "/MANIFEST.json"
    review = read(root / "integrations/ARCHIVE_EVIDENCE.json")
    phase = status["status"]
    data = {
        "title": "666CLS · Clean Lyric & Story Archive",
        "basis": f"Repository-Release {status['version']} · Schema {status['schema_version']}",
        "views": [
            {"id": "archive", "title": "Archiv", "summary": f"{status['total']} geprüfte Einträge",
             "source": source, "status": phase, "kind": "cards", "route_terms": ["archiv", "lyrics"],
             "items": [{"label": name, "text": str(count)} for name, count in status["domains"].items()]},
            {"id": "audit", "title": "Audit", "summary": "Datenbank und Menüs geprüft",
             "source": status["source"] + "/AUDIT.json", "status": phase, "kind": "narrative",
             "route_terms": ["audit", "prüfen"], "items": [{"label": k, "text": v} for k, v in review["de"].items()]},
        ],
        "gaps": [],
        "chart": {"intent": "compare", "rows": "\n".join(
            f"{name};{count}" for name, count in status["domains"].items()), "unit": "Einträge", "source": source},
        "companion": {"phase": "LiveCircle", "status": phase, "project_key": status["system_id"],
                      "source_revision": status["version"], "last_evidence": source,
                      "next_step": status["next_step"]},
        "actions": [{"id": "audit", "kind": "verify", "label": "Archivprüfung ansehen",
                     "source": source, "reason": "Menü und Datenbank gemeinsam prüfen",
                     "effect": "Auditansicht öffnen", "countercheck": "Release-Manifest mit Archiv vergleichen",
                     "view_id": "audit"}],
    }
    if checkpoint:
        data = apply_checkpoint(data, read(checkpoint))
    html = render(data, (ASSETS / "ui-template.html").read_text(encoding="utf-8"))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text('<!doctype html><html lang="de"><meta charset="utf-8">'
                      '<meta name="viewport" content="width=device-width, initial-scale=1">'
                      '<title>666CLS Archiv</title><body>' + html + '</body></html>', encoding="utf-8")
