#!/usr/bin/env python3
"""MYCEL R02: sichere, rein lesende Menü-/Daemon-Projektion für bestehende Workbench."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

VALID = {"VERIFIZIERT", "ABGELEITET", "VORGESCHLAGEN", "OFFEN",
         "BLOCKIERT", "PARTIAL", "WRITE_BLOCKED", "READBACK_PENDING",
         "CONFLICT_QUARANTINE"}
MENU_SCHEMA = "psyllo.intelligent-menu.1"
STATE_SCHEMA = "psyllo.guidance-state.1"
HANDOFF_SCHEMA = "psyllo.ui-handoff.1"


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 320:
        raise ValueError(f"{field}: nichtleerer Text bis 320 Zeichen erforderlich")
    return value.strip()


def _same_context(state: dict, handoff: dict) -> bool:
    return (isinstance(state.get("lineage_id"), str)
            and bool(state["lineage_id"].strip())
            and handoff.get("schema") == HANDOFF_SCHEMA
            and handoff.get("project_id") == state.get("active_scope")
            and handoff.get("source_commit") == state.get("source_head")
            and handoff.get("lineage_id") == state.get("lineage_id"))


def project(menu: dict, state: dict, *, handoff: dict | None = None) -> dict:
    """Erzeugt einen Datensatz im existierenden render_ui.py-Format, ohne Seiteneffekte."""
    if menu.get("schema") != MENU_SCHEMA or menu.get("owner") != "666MAIN BRAIN MYCEL SYSTEM":
        raise ValueError("MENU: falscher Schema- oder System-Eigner")
    if state.get("schema") != STATE_SCHEMA or state.get("owner") != "666MAIN BRAIN MYCEL SYSTEM":
        raise ValueError("DAEMON: falscher Schema- oder System-Eigner")
    head = _text(state.get("source_head"), "source_head")
    scope = _text(state.get("active_scope"), "active_scope")
    if len(head) != 40 or any(c not in "0123456789abcdef" for c in head):
        raise ValueError("source_head: vollständige Git-SHA erforderlich")
    status = state.get("evidence_class")
    if status not in VALID:
        raise ValueError("evidence_class: ungültiger Status")
    if not isinstance(state.get("open_obligations"), list) or not isinstance(state.get("blockers"), list):
        raise ValueError("open_obligations/blockers: Listen erforderlich")
    entries = menu.get("views")
    if not isinstance(entries, list) or len(entries) != 6:
        raise ValueError("MENU: genau sechs bestehende MYCEL-Ansichten erforderlich")
    expected = ("OVERVIEW", "DEVELOPMENT", "FACETS", "GUIDANCE", "EVIDENCE", "CONTINUITY")
    if tuple(x.get("id") for x in entries if isinstance(x, dict)) != expected:
        raise ValueError("MENU: Reihenfolge oder IDs verändert")
    views = []
    for entry in entries:
        identifier = entry["id"].lower()
        if entry.get("action") != "local_view":
            raise ValueError("MENU: nicht-lokale Aktion in View")
        label = _text(entry.get("label"), "menu.label")
        description = {
            "OVERVIEW": "GitHub Current, Native Authority und Projektbindung",
            "DEVELOPMENT": "PSYLLO Coding Workbench und DEV-Quellengrenzen",
            "FACETS": "15 native PSYLLO-Facetten, lazy nach Intent",
            "GUIDANCE": "Shared Guidance Daemon: Handlungsvorschläge ohne Write-Autorität",
            "EVIDENCE": "Quelle, Host-Abnahme, Blocker und Gegenprüfung",
            "CONTINUITY": "Whole LifeCircle, Lineage und Return-Anchor",
        }[entry["id"]]
        views.append({
            "id": identifier, "title": label, "summary": description,
            "kind": "cards", "route_terms": [label, identifier],
            "source": "UI/INTELLIGENT_UI/MENU_REGISTRY.json @ " + head,
            "status": status if identifier == "overview" else "ABGELEITET",
            "items": [{"label": "Verifizierte Projektbindung",
                       "text": scope + " @ " + head},
                      {"label": "Funktion", "text": description}],
        })
    blocker = state["blockers"][0] if state["blockers"] else "Keine weitere Blockeraussage belegt"
    next_action = state.get("next_action")
    next_text = (next_action.get("label") if isinstance(next_action, dict) else None)
    if next_text is None:
        next_text = "Nächste Aktion anhand der Quellenlage prüfen"
    companion = {
        "phase": _text(state.get("phase"), "phase"),
        "status": status,
        "project_key": scope,
        "source_revision": head,
        "last_evidence": _text(state.get("last_verified_step") or "Kein letzter Schritt belegt", "last_verified_step"),
        "blocker": _text(str(blocker), "blocker"),
        "next_step": _text(next_text, "next_step"),
        "reason": "MAIN-BRAIN Current und Zustandsnachweis; keine autonome Ausführung",
        "countercheck": "Pointer, Source-HEAD, Scope und tatsächliches Hostverhalten gegenprüfen",
        "start_mode": "project",
    }
    if handoff is not None:
        if not isinstance(handoff, dict) or not _same_context(state, handoff):
            raise ValueError("UI-Handoff: Projekt, Revision oder Lineage abweichend")
        view_id = handoff.get("view_id")
        if view_id is not None:
            if view_id not in {v["id"] for v in views}:
                raise ValueError("UI-Handoff: unbekannte Ansicht")
            companion["start_view"] = view_id
    gaps = ["Host-Ausführung und Plugin-Parität getrennt prüfen"]
    gaps += [_text(str(b), "blocker") for b in state["blockers"]]
    return {
        "title": "PSYLLO · MYCEL Intelligent UI",
        "basis": "CURRENT_POINTER.md / " + head,
        "handoff_format": "neutral",
        "views": views, "gaps": gaps, "companion": companion,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--menu", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ui-handoff", type=Path)
    args = parser.parse_args()
    menu = json.loads(args.menu.read_text(encoding="utf-8"))
    state = json.loads(args.state.read_text(encoding="utf-8"))
    handoff = json.loads(args.ui_handoff.read_text(encoding="utf-8")) if args.ui_handoff else None
    result = project(menu, state, handoff=handoff)
    # Ausgabe enthält ausschließlich Datendarstellung; der Workbench-Renderer bleibt zuständig.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
