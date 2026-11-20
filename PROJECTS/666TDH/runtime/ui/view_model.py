"""Registry-native menu + advisory daemon model. No route, write or authority."""

from __future__ import annotations


def build_view_model(*, registry: dict, routes: dict, token: str | None,
                     release: str, profile: dict | None, continuity: dict | None,
                     pointer_state: str) -> dict:
    names = registry["children"]
    root_commands = ["SYSTEMSTART", "STATUS", "HELP", "WEITER", "NEW CHAT", "DASHBOARD", "VISUAL", "HOST RECOVERY", "UPDATE"]
    options = []
    if token is None:
        for branch, child in names.items():
            options.append({"id": branch, "title": child["name"],
                            "command": f"666TDH {branch} SYSTEMSTART", "kind": "copy-trigger"})
        sections = [{"id": "whole", "title": "Whole TDH"},
                    {"id": "children", "title": "Child-Registry"},
                    {"id": "continuity", "title": "LiveCircle / Handoff"},
                    {"id": "evidence", "title": "Evidenz / Prüfstatus"}]
        title = "666TRACKDESIGNHUB"
    else:
        title = names[token]["name"]
        sections = [{"id": f"section-{i+1}", "title": section} for i, section in enumerate(profile["ui_sections"])]
        for action in routes["child"]:
            options.append({"id": f"{token}-{action}", "title": action,
                            "command": f"666TDH {token} {action}", "kind": "copy-trigger"})
        options.append({"id": "back", "title": "Zurück zum Hub",
                        "command": "666TDH SYSTEMSTART", "kind": "copy-trigger"})
    if token is None:
        options.extend({"id": "hub-"+cmd, "title": cmd,
                        "command": "666TDH "+cmd, "kind": "copy-trigger"}
                       for cmd in root_commands if cmd in routes["root"])
    holds = list(profile.get("holds", [])) if profile else []
    if holds:
        next_step = "Quell-HOLD prüfen; fehlende native Identität nicht automatisch rekonstruieren."
        next_command = f"666TDH {token} STATUS" if token else "666TDH STATUS"
    elif continuity is not None and continuity.get("status") == "NO_BOUND_HANDOFF":
        next_step = "Kein branchgebundener Handoff. Lokalen Arbeitsschritt nicht erraten."
        next_command = f"666TDH {token} STATUS" if token else "666TDH STATUS"
    else:
        next_step = "Aktuellen Zustand und zulässigen nächsten Schritt prüfen."
        next_command = f"666TDH {token} STATUS" if token else "666TDH STATUS"
    companion = {"name": "666TDH Begleit-Daemon", "mode": "ADVISORY_ONLY",
                 "autoactive": True, "scope": token or "HUB", "target_system_id": names[token]["system_id"] if token else registry["system_id"],
                 "state": "HOLD_VISIBLE" if holds else "READ_ONLY_GUIDANCE",
                 "evidence": ["CURRENT_POINTER.json", "runtime/REGISTRY.json"] + ([profile["current_path"]] if profile else []),
                 "holds": holds, "next_safe_action": next_step, "suggested_command": next_command,
                 "countercheck": "GitHub Current und zielgebundenen Child-Pointer derselben Revision rücklesen",
                 "routing_authority": "NONE", "write_authority": "NONE",
                 "decision_authority": "NONE"}
    return {"schema": "666tdh.intelligent-ui.1", "system_id": registry["system_id"],
            "native_release": release, "repository_state": pointer_state,
            "scope": token or "HUB", "title": title, "sections": sections,
            "menu": options, "companion": companion, "host_acceptance": "OPEN_NOT_VERIFIED",
            "render_capability": "LOCAL_HTML_OR_CHAT_NATIVE_HOST"}
