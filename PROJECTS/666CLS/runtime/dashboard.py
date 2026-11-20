"""Erzeugt die 666CLS-Ansicht und leitet Menüaktionen aus geprüften Daten ab."""
from pathlib import Path
import sys

from cls_livecircle import read

RENDERER = Path(__file__).resolve().parents[1] / "integrations/visual/scripts"
sys.path.insert(0, str(RENDERER))
from render_ui import ASSETS, apply_checkpoint, render


def view(ident, title, summary, source, status, terms, items, kind="cards"):
    return {"id": ident, "title": title, "summary": summary, "source": source,
            "status": status, "kind": kind, "route_terms": terms,
            "items": [{"label": label, "text": str(value)} for label, value in items]}


def action(ident, view_id, kind, label, source, reason, effect, probe):
    return {"id": ident, "view_id": view_id, "kind": kind, "label": label,
            "source": source, "reason": reason, "effect": effect, "countercheck": probe}


def dashboard_data(root, status, inbox=None):
    source = status["source"] + "/MANIFEST.json"
    audit = status["source"] + "/AUDIT.json"
    evidence = read(root / "integrations/ARCHIVE_EVIDENCE.json")
    verified = status["status"]
    inbox_source = "Private 666CLS-Inbox"
    inbox_status = "OFFEN"
    inbox_summary = "Inbox für diese Ansicht nicht gelesen"
    inbox_items = [("Zugriff", "Mit dem Prüfzugang eine Inbox-Ansicht erzeugen.")]
    inbox_action = action("read-inbox", "inbox", "readback", "Inbox-Status abrufen", inbox_source,
                          "Für diese Ansicht fehlt eine Abfrage", "Offene Einreichungen zählen",
                          "Archivversion und Inbox-Stand abgleichen")
    framework_items = [("Rechte", "Lesen und Einreichen werden je Framework und Archivbereich vergeben."),
                       ("Prüfung", "Die Übernahme erfolgt über die 666CLS-Prüfinstanz.")]
    if inbox is not None:
        inbox_status = verified
        pending = sum(inbox.values())
        inbox_summary = f"{pending} Einreichungen zur Prüfung"
        inbox_items = list(inbox.items())
        if pending:
            inbox_action = action("review-inbox", "inbox", "verify", "Einreichungen prüfen", inbox_source,
                                  "Neue Einreichungen liegen vor", "Herkunft und Archivbereich prüfen",
                                  "Quittungen mit der ausgewählten Einreichung vergleichen")
        else:
            inbox_action = action("refresh-inbox", "inbox", "readback", "Inbox später erneut lesen", inbox_source,
                                  "Zum Zeitpunkt der Abfrage waren keine Einreichungen offen",
                                  "Neue Einreichungen seit der Abfrage erkennen", "Abfragezeit vergleichen")
    snapshot = inbox_source if inbox is not None else source
    return {
        "title": "666CLS · Gemeinsames Archiv",
        "basis": f"Release {status['version']} · Schema {status['schema_version']}",
        "views": [
            view("archive", "Archiv", f"{status['total']} geprüfte Einträge", source, verified,
                 ["archiv", "lyrics", "story", "rohmaterial", "text"], status["domains"].items()),
            view("inbox", "Eingang", inbox_summary, inbox_source, inbox_status,
                 ["eingang", "inbox", "einreichung", "quittung"], inbox_items),
            view("frameworks", "Frameworks", "Zugriff auf das gemeinsame Archiv",
                 "666CLS · shared_archive/README.md", "ABGELEITET",
                 ["framework", "zugriff", "rechte", "anbindung"], framework_items),
            view("audit", "Nachweise", "Datenbank und Menüs geprüft", audit, verified,
                 ["audit", "nachweis", "prüfsumme", "version"], evidence["de"].items(), "narrative"),
        ],
        "gaps": [] if inbox is not None else ["Inbox-Stand für diese Ansicht noch offen."],
        "chart": {"intent": "compare", "rows": "\n".join(
            f"{name};{count}" for name, count in status["domains"].items()), "unit": "Einträge", "source": source},
        "companion": {"phase": "666CLS", "project_key": status["system_id"],
                      "source_revision": status["version"], "last_evidence": snapshot},
        "actions": [
            action("verify-archive", "archive", "verify", "Archivstand abgleichen", source,
                   "Zähler stammen aus dem geprüften Release", "Freigegebenen Bestand bestätigen",
                   "Datenbank- und Menüwerte je Bereich vergleichen"),
            inbox_action,
            action("check-framework", "frameworks", "clarify", "Framework-Zugriff prüfen",
                   "Geschützter 666CLS-Host", "Rechte werden je Framework und Bereich vergeben",
                   "Passende Lese- und Einreichungsrechte bestimmen", "Erlaubte und gesperrte Vorgänge prüfen"),
            action("verify-release", "audit", "verify", "Release-Nachweis prüfen", audit,
                   "Freigabe stützt sich auf konkretes Release-Manifest", "Version und Prüfsummen rücklesen",
                   "Manifest mit dem aktuellen Pointer vergleichen"),
        ],
    }


def render_dashboard(root, status, output, checkpoint=None, *, inbox=None):
    data = dashboard_data(root, status, inbox)
    if checkpoint:
        data = apply_checkpoint(data, read(checkpoint))
    html = render(data, (ASSETS / "ui-template.html").read_text(encoding="utf-8"))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text('<!doctype html><html lang="de"><meta charset="utf-8">'
                      '<meta name="viewport" content="width=device-width, initial-scale=1">'
                      '<title>666CLS Archiv</title><body>' + html + '</body></html>', encoding="utf-8")
