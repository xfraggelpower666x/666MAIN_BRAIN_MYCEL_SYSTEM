#!/usr/bin/env python3
"""Validierten SCEVI-Datensatz in ein lokales interaktives HTML-Fragment setzen."""
from __future__ import annotations

import argparse
import json
import re
import sys
from graphlib import CycleError, TopologicalSorter
from pathlib import Path

STATUSES = {
    "VERIFIZIERT", "ABGELEITET", "VORGESCHLAGEN", "OFFEN",
    "BLOCKIERT", "PARTIAL", "WRITE_BLOCKED", "READBACK_PENDING",
    "CONFLICT_QUARANTINE",
}
KINDS = {"narrative", "cards", "line", "bars"}
ID_RE = re.compile(r"^[a-z][a-z0-9-]{0,39}$")
PROJECT_KEY = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/@-]{0,179}", re.ASCII)
MODES = frozenset({"project", "formats", "charts"})
ACTION_KINDS = ("readback", "clarify", "verify", "navigate")
CHART_INTENTS = frozenset({"compare", "trend", "relationship", "composition"})
ASSETS = Path(__file__).resolve().parents[1] / "assets"
PLACEHOLDERS = {
    "__SCEERI_FORMAT_MENU__": "visualform-menu.html",
    "__SCEERI_CHARTS__": "charts.html",
    "__SCEERI_DAEMON__": "visual-daemon.html",
    "__SCEERI_COMPANION__": "companion.js",
}
DATA_MARKER = "__SCEERI_UI_DATA__"
DEFAULT_HANDOFF_FORMAT = "coding-profi"


def require_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name}: nichtleerer Text erforderlich")
    return value.strip()


def validate_companion(config: object) -> None:
    if not isinstance(config, dict):
        raise ValueError("companion: Objekt erforderlich")
    for key in ("phase", "last_evidence", "blocker", "next_step", "reason", "countercheck"):
        if key in config:
            if len(require_text(config[key], "companion." + key)) > 320:
                raise ValueError("companion." + key + ": bis zu 320 Zeichen")
    if "project_key" in config:
        key = require_text(config["project_key"], "companion.project_key")
        if not PROJECT_KEY.fullmatch(key) or key != config["project_key"]:
            raise ValueError("companion.project_key: eindeutige Projektkennung erforderlich")
    if "source_revision" in config:
        revision = require_text(config["source_revision"], "companion.source_revision")
        if len(revision) > 200 or revision != config["source_revision"]:
            raise ValueError("companion.source_revision: genaue Revisionskennung erforderlich")
    if "start_format" in config and (
        not isinstance(config["start_format"], str) or not ID_RE.fullmatch(config["start_format"])
    ):
        raise ValueError("companion.start_format: ungültige Form-ID")
    for name, allowed in (("status", STATUSES), ("start_mode", MODES)):
        if name in config and (not isinstance(config[name], str) or config[name] not in allowed):
            raise ValueError("companion." + name + ": unbekannt")



def validate_actions(actions: object, view_ids: set[str]) -> None:
    if not isinstance(actions, list) or len(actions) > 8:
        raise ValueError("actions: bis zu 8 Vorschläge in einer Liste")
    graph = {}
    for action in actions:
        if not isinstance(action, dict):
            raise ValueError("actions: Objekt erforderlich")
        ident = action.get("id")
        if not isinstance(ident, str) or not ID_RE.fullmatch(ident) or ident in graph:
            raise ValueError("actions.id: ungültig oder doppelt")
        if action.get("kind") not in ACTION_KINDS:
            raise ValueError("actions.kind: unbekannt")
        for field in ("label", "source", "reason", "effect", "countercheck"):
            if len(require_text(action.get(field), "actions." + field)) > 320:
                raise ValueError("actions." + field + ": bis zu 320 Zeichen")
        if "view_id" in action and (not isinstance(action["view_id"], str) or action["view_id"] not in view_ids):
            raise ValueError("actions.view_id: unbekannte Ansicht")
        dependencies = action.get("requires", [])
        if not isinstance(dependencies, list) or any(not isinstance(dep, str) for dep in dependencies):
            raise ValueError("actions.requires: Liste von IDs erforderlich")
        graph[ident] = dependencies
        if "status" in action and action["status"] not in ("VORGESCHLAGEN", "VERIFIZIERT", "BLOCKIERT"):
            raise ValueError("actions.status: unbekannt")
    if any(dep not in graph for dependencies in graph.values() for dep in dependencies):
        raise ValueError("actions.requires: unbekannter Vorgänger")
    try:
        list(TopologicalSorter(graph).static_order())
    except CycleError as error:
        raise ValueError("actions.requires: zyklische Abhängigkeit") from error

def validate_chart(config: object) -> None:
    if not isinstance(config, dict):
        raise ValueError("chart: Objekt erforderlich")
    if (not isinstance(config.get("intent"), str) or config["intent"] not in CHART_INTENTS):
        raise ValueError("chart.intent: unbekannt")
    rows = require_text(config.get("rows"), "chart.rows")
    if len(config["rows"]) > 6400 or len(rows.splitlines()) > 40:
        raise ValueError("chart.rows: bis zu 40 Zeilen und 6400 Zeichen")
    for field, length in (("source", 240), ("x_label", 72), ("unit", 72)):
        if field in config and len(require_text(config[field], "chart." + field)) > length:
            raise ValueError("chart." + field + ": zu lang")


def validate(data: object) -> dict:
    if not isinstance(data, dict):
        raise ValueError("Wurzel muss ein Objekt sein")
    require_text(data.get("title"), "title")
    require_text(data.get("basis"), "basis")
    views = data.get("views")
    if not isinstance(views, list) or not 1 <= len(views) <= 6:
        raise ValueError("views: 1 bis 6 Ansichten erforderlich")
    gaps = data.get("gaps")
    if not isinstance(gaps, list) or any(not isinstance(g, str) or not g.strip() for g in gaps):
        raise ValueError("gaps: Liste nichtleerer Texte erforderlich")
    if "handoff_format" in data and data["handoff_format"] not in ("coding-profi", "neutral"):
        raise ValueError("handoff_format: unbekannt")
    if "companion" in data:
        validate_companion(data["companion"])
    if "chart" in data:
        validate_chart(data["chart"])
    ids = set()
    for i, view in enumerate(views):
        if not isinstance(view, dict):
            raise ValueError(f"views[{i}]: Objekt erforderlich")
        ident = require_text(view.get("id"), f"views[{i}].id")
        if not ID_RE.fullmatch(ident) or ident in ids:
            raise ValueError(f"views[{i}].id: ungültig oder doppelt")
        ids.add(ident)
        for key in ("title", "summary", "source"):
            require_text(view.get(key), f"views[{i}].{key}")
        if not isinstance(view.get("status"), str) or view["status"] not in STATUSES:
            raise ValueError(f"views[{i}].status: unbekannt")
        kind = view.get("kind")
        if not isinstance(kind, str) or kind not in KINDS:
            raise ValueError(f"views[{i}].kind: unbekannt")
        terms = view.get("route_terms")
        if not isinstance(terms, list) or not terms or any(not isinstance(t, str) or not t.strip() for t in terms):
            raise ValueError(f"views[{i}].route_terms: nichtleere Liste erforderlich")
        if kind in ("narrative", "cards"):
            items = view.get("items")
            if not isinstance(items, list) or not items:
                raise ValueError(f"views[{i}].items: erforderlich")
            for item in items:
                if not isinstance(item, dict):
                    raise ValueError("item: Objekt erforderlich")
                require_text(item.get("label"), "item.label")
                require_text(item.get("text"), "item.text")
        else:
            if view.get("data_kind") != "schematic" or view.get("status") != "ABGELEITET":
                raise ValueError(f"views[{i}]: Kurven/Balken nur schematisch mit Status ABGELEITET")
            if "qualitativ" not in require_text(view.get("caption"), "caption").lower():
                raise ValueError(f"views[{i}].caption: 'qualitativ' kennzeichnen")
            if kind == "line":
                series = view.get("series")
                if not isinstance(series, list) or not 1 <= len(series) <= 2:
                    raise ValueError("series: 1 bis 2 Reihen")
                lengths = set()
                for item in series:
                    require_text(item.get("label") if isinstance(item, dict) else None, "series.label")
                    values = item.get("values")
                    if not isinstance(values, list) or not 2 <= len(values) <= 32 or any(type(v) not in (int, float) or not 0 <= v <= 100 for v in values):
                        raise ValueError("series.values: 2 bis 32 normierte Werte")
                    lengths.add(len(values))
                if len(lengths) != 1:
                    raise ValueError("series.values: gleiche Anzahl nötig")
            else:
                bars = view.get("bars")
                if not isinstance(bars, list) or not 2 <= len(bars) <= 12:
                    raise ValueError("bars: 2 bis 12 Balken")
                for item in bars:
                    require_text(item.get("label") if isinstance(item, dict) else None, "bars.label")
                    if type(item.get("level")) not in (int, float) or not 0 <= item["level"] <= 100:
                        raise ValueError("bars.level: normiert 0–100")
    start_view = data.get("companion", {}).get("start_view")
    if start_view is not None and (not isinstance(start_view, str) or start_view not in ids):
        raise ValueError("companion.start_view: unbekannte Ansicht")
    if "actions" in data:
        validate_actions(data["actions"], ids)
    return data


def render(data: dict, template: str) -> str:
    payload = {"handoff_format": DEFAULT_HANDOFF_FORMAT, **validate(data)}
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    encoded = encoded.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    replacements = {DATA_MARKER: encoded}
    for marker, asset in PLACEHOLDERS.items():
        if marker in template:
            replacements[marker] = (ASSETS / asset).read_text(encoding="utf-8")
    pattern = "|".join(map(re.escape, replacements))
    return re.sub(pattern, lambda match: replacements[match[0]], template)


def apply_checkpoint(data: dict, checkpoint: object) -> dict:
    """Erhält den bestätigten Projektstand und stellt die gespeicherte UI-Ansicht wieder her."""
    validate(data)
    if not isinstance(checkpoint, dict) or checkpoint.get("schema") != "scevi.visual.handoff.1":
        raise ValueError("UI-Handoff: unbekanntes Schema")
    companion = data.get("companion", {})
    for key in ("project_key", "source_revision"):
        if not companion.get(key) or checkpoint.get(key) != companion[key]:
            raise ValueError("UI-Handoff: " + key + " stimmt nicht mit der Projektbasis überein")
    mode = checkpoint.get("mode")
    if not isinstance(mode, str) or mode not in MODES:
        raise ValueError("UI-Handoff: unbekannte Ansicht")
    view_id = checkpoint.get("view_id")
    if view_id is not None and not any(view["id"] == view_id for view in data["views"]):
        raise ValueError("UI-Handoff: unbekannte Projektansicht")
    defaults = {"start_mode": mode}
    if view_id is not None:
        defaults["start_view"] = view_id
    format_id = checkpoint.get("format_id")
    if mode == "formats" and isinstance(format_id, str) and ID_RE.fullmatch(format_id):
        defaults["start_format"] = format_id
    return {**data, "companion": {**defaults, **companion}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--standalone", action="store_true")
    args = parser.parse_args()
    data = validate(json.loads(args.input.read_text(encoding="utf-8")))
    if args.checkpoint:
        try:
            checkpoint = json.loads(args.checkpoint.read_text(encoding="utf-8"))
            data = apply_checkpoint(data, checkpoint)
        except (OSError, ValueError) as error:
            print("UI-Handoff übersprungen · " + str(error), file=sys.stderr)
    template = (ASSETS / "ui-template.html").read_text(encoding="utf-8")
    if any(template.count(marker) != 1 for marker in (DATA_MARKER, *PLACEHOLDERS)):
        raise ValueError("Jeder Marker muss genau einmal in der UI-Vorlage stehen")
    html = render(data, template)
    if args.standalone:
        html = ('<!doctype html><html lang="de"><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width, initial-scale=1">'
                '<title>Intelligent UI</title><body>' + html + '</body></html>')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

