"""Registry-native TDH-UI: evidenzgebundene Ansichten und beratender Daemon.

Nur Darstellung. Weder UI noch Daemon erhalten Routing- oder Schreibautorität.
"""
from __future__ import annotations


def _view(ident: str, title: str, summary: str, source: str,
          status: str, facts: list[str]) -> dict:
    return {"id": ident, "title": title, "summary": summary,
            "source": source, "status": status, "facts": facts}


def build_view_model(*, registry: dict, routes: dict, token: str | None,
                     release: str, profile: dict | None, continuity: dict | None,
                     pointer_state: str, files_verified: int | None = None) -> dict:
    """Baue ausschließlich für das direkt gewählte Ziel eine prüfbare Oberfläche."""
    names = registry["children"]
    root_commands = ("SYSTEMSTART", "STATUS", "HELP", "WEITER", "NEW CHAT",
                     "DASHBOARD", "VISUAL", "HOST RECOVERY", "UPDATE")
    options: list[dict] = []
    verified_text = "Lokaler Current-Readback" + (f" · {files_verified} Dateien SHA-256-geprüft" if files_verified is not None else "")
    branch = names[token] if token else None
    if token is None:
        title = "666TRACKDESIGNHUB"
        for branch_token, child in names.items():
            options.append({"id": branch_token, "title": child["name"],
                            "command": f"666TDH {branch_token} SYSTEMSTART", "kind": "copy-trigger"})
        options.extend({"id": "hub-" + cmd, "title": cmd, "command": "666TDH " + cmd,
                        "kind": "copy-trigger"} for cmd in root_commands if cmd in routes["root"])
        sections = [
            _view("whole", "Whole TDH", "Repo-Current und native Systemidentität",
                  "CURRENT_POINTER.json", "VERIFIZIERT_LOKAL",
                  ["System-ID: " + registry["system_id"], "Native Version: " + release,
                   "Repo-Zustand: " + pointer_state, verified_text]),
            _view("children", "Child-Registry", "Fünf getrennte Track-Childs, keine automatische Aktivierung",
                  "runtime/REGISTRY.json", "VERIFIZIERT_LOKAL",
                  [t + " · " + c["name"] + " · " + c["version"] + " · " + c["current_path"]
                   for t, c in names.items()]),
            _view("continuity", "LiveCircle / Handoff", "Nur zum bestätigten Ziel passende Kontinuität",
                  "continuity/CURRENT_HANDOFF.json", "OFFEN" if not continuity else continuity.get("status", "OFFEN"),
                  ["Kein Handoff ersetzt den Current-Pointer.",
                   "Ein Chat-Checkpoint ist benutzergegeben und revisionsgebunden.",
                   "WEITER liest zuerst den vollständigen nativen Current."]),
            _view("evidence", "Evidenz / Prüfstatus", "Prüfgrenzen und verbleibende Host-Abnahme",
                  "runtime/REPO_UPDATE_AUTHORITY.md", "PARTIAL_HOST_ACCEPTANCE",
                  [verified_text, "Chat-Host-Rendering: OPEN_NOT_VERIFIED",
                   "FSE Source Vault: externer Recovery-Verweis, niemals Autoload",
                   "PFS- und Fremdsystemautorität: NONE"]),
        ]
    else:
        title = branch["name"]
        for action in routes["child"]:
            options.append({"id": f"{token}-{action}", "title": action,
                            "command": f"666TDH {token} {action}", "kind": "copy-trigger"})
        options.append({"id": "back", "title": "Zurück zum Hub",
                        "command": "666TDH SYSTEMSTART", "kind": "copy-trigger"})
        holds = list(profile.get("holds", []))
        sections = [
            _view(f"section-{i+1}", label,
                  f"{token}-Subfacette · native Arbeitsphase {i+1}/{len(profile['ui_sections'])}",
                  profile["current_path"] if i == 0 else profile["visual_adapter_path"],
                  "HOLD" if holds else "VERIFIZIERTE_KONFIGURATION",
                  ["Fachziel: " + label,
                   "Zulässiger Lebenszyklus: " + " → ".join(profile["local_lifecycle"]),
                   "Child-Current: " + profile["current_path"],
                   "Visual-Adapter: " + profile["visual_adapter_path"],
                   "Nur deklarierte Fähigkeit; kein automatisch ausgeführter Track-Schritt."]
                  + (["Offene Holds: " + ", ".join(holds)] if holds else []))
            for i, label in enumerate(profile["ui_sections"])
        ]
    holds = list(profile.get("holds", [])) if profile else []
    if holds:
        daemon_state = "HOLD_VISIBLE"
        next_step = "Quell-HOLD prüfen; ungeklärte Identität weder rekonstruieren noch veröffentlichen."
    elif continuity is not None and continuity.get("status") == "LOCAL_SCOPED_CHECKPOINT_UNVERIFIED_TASK":
        daemon_state = "CHECKPOINT_REVIEW_REQUIRED"
        next_step = "Angegebene Entwicklungsposition und offenen Schritt am aktuellen Child-Current gegenprüfen."
    elif continuity is not None and continuity.get("status") == "NO_BOUND_HANDOFF":
        daemon_state = "NO_BOUND_HANDOFF"
        next_step = "Kein zielgebundener Handoff: offenen Schritt nicht erraten; Current-Status prüfen."
    else:
        daemon_state = "READ_ONLY_GUIDANCE"
        next_step = "Aktuellen Zustand und die zulässige nächste Benutzeraktion prüfen."
    next_command = f"666TDH {token} STATUS" if token else "666TDH STATUS"
    companion = {"name": "666TDH Begleit-Daemon", "mode": "ADVISORY_ONLY",
                 "autoactive": True, "scope": token or "HUB",
                 "target_system_id": branch["system_id"] if branch else registry["system_id"],
                 "state": daemon_state, "evidence": ["CURRENT_POINTER.json", "runtime/REGISTRY.json"] +
                 ([profile["current_path"]] if profile else []),
                 "holds": holds, "next_safe_action": next_step,
                 "suggested_command": next_command,
                 "countercheck": "GitHub Current und zielgebundenen Child-Pointer derselben Revision rücklesen",
                 "routing_authority": "NONE", "write_authority": "NONE", "decision_authority": "NONE"}
    daemon_menu = ([{"id": "daemon-" + cmd, "title": cmd,
                     "command": "666TDH DAEMON " + cmd, "kind": "copy-trigger"}
                    for cmd in routes.get("daemon", [])] if token is None else [])
    return {"schema": "666tdh.intelligent-ui.1", "system_id": registry["system_id"],
            "native_release": release, "repository_state": pointer_state,
            "scope": token or "HUB", "title": title, "sections": sections,
            "menu": options, "daemon_menu": daemon_menu, "companion": companion,
            "host_acceptance": "OPEN_NOT_VERIFIED", "render_capability": "LOCAL_HTML_OR_CHAT_NATIVE_HOST",
            "integrity": {"verified_files": files_verified, "basis": "REPOSITORY_CURRENT"}}
