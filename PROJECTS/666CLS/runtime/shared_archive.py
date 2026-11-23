"""Gemeinsamer 666CLS-Archivzugang über eine private, transaktionale Inbox."""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import sqlite3
import sys
from contextlib import closing
from pathlib import Path

from cls_livecircle import (
    DOMAINS, ROOT, SYSTEM, entries_by_id, json_text, read, rehydrate, require, requires_source_vault, version_key,
)

CLIENT_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,31}")
REQUEST_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,47}")


def authorize(config, client, token, action, domain=None):
    policy = read(config)
    require(policy["system_id"] == SYSTEM, "Falsche System-ID in der Zugriffskonfiguration")
    account = policy["clients"].get(client)
    require(CLIENT_ID.fullmatch(client) and account and isinstance(token, str) and len(token) >= 32,
            "Zugriff verweigert")
    digest = hashlib.sha256(token.encode()).hexdigest()
    require(hmac.compare_digest(digest, account["token_sha256"]), "Zugriff verweigert")
    if domain is None:
        require(action == "review" and account.get("review") is True, "Zugriff verweigert")
    else:
        require(domain in DOMAINS and domain in account.get(action, []), "Zugriff verweigert")


def live_records(root, state, domain):
    return read(root / state["source"] / f"DATABASE/{domain}_ARCHIVE.json")["entries"]


def connect(db):
    # Der gemeinsame Datenordner liegt auf demselben Host und ist nur für den Betreiber zugänglich.
    require(db.parent.is_dir(), "Privaten Datenordner zuerst anlegen")
    conn = sqlite3.connect(db, timeout=20)
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS submissions(
                    client TEXT NOT NULL, request_id TEXT NOT NULL,
                    domain TEXT NOT NULL, record TEXT NOT NULL,
                    received_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (client, request_id)
                )
            """)
    except sqlite3.Error:
        conn.close()
        raise
    return conn


def submit(db, client, request_id, domain, source):
    require(CLIENT_ID.fullmatch(client) and REQUEST_ID.fullmatch(request_id), "Ungültige Kennung")
    require(domain in DOMAINS, "Unbekannter Archivbereich")
    require(isinstance(source, dict) and "archive_provenance" not in source,
            "Datensatz ungültig oder enthält reservierte Provenienz")
    ident = f"shared:{client}:{request_id}"
    record = {
        **source,
        "id": ident,
        "archive_provenance": {
            "framework_id": client, "submission_id": request_id, "source_id": source.get("id"),
        },
    }
    entries_by_id([record], domain)
    payload = json.dumps(record, ensure_ascii=False, allow_nan=False, sort_keys=True)
    with closing(connect(db)) as conn, conn:
        inserted = conn.execute(
            "INSERT INTO submissions (client,request_id,domain,record) VALUES (?,?,?,?) "
            "ON CONFLICT(client,request_id) DO NOTHING", (client, request_id, domain, payload),
        ).rowcount
        if not inserted:
            existing = conn.execute(
                "SELECT domain,record FROM submissions WHERE client=? AND request_id=?",
                (client, request_id),
            ).fetchone()
            require(existing == (domain, payload), "Einreichungs-ID bereits mit anderem Inhalt belegt")
    return {"receipt": f"{client}/{request_id}", "id": ident, "domain": domain,
            "status": "HOLD" if requires_source_vault(record) else "ACCEPTED_FOR_REVIEW",
            "idempotent": not inserted}


def pending(db, root, state=None):
    state = state if state is not None else rehydrate(root)
    live = {entry["id"] for domain in DOMAINS for entry in live_records(root, state, domain)}
    with closing(connect(db)) as conn:
        rows = conn.execute("SELECT client,request_id,domain,record,received_at FROM submissions "
                            "ORDER BY received_at,client,request_id").fetchall()
    entries = []
    for client, ident, domain, payload, stamp in rows:
        record = json.loads(payload)
        if record["id"] in live:
            continue
        hold = requires_source_vault(record)
        entries.append({"receipt": f"{client}/{ident}", "domain": domain, "received_at": stamp,
                        "status": "HOLD" if hold else "ACCEPTED_FOR_REVIEW",
                        "record": {"id": record["id"], "source_vault_ref": "SOURCE_VAULT_ONLY"}
                        if hold else record})
    return entries


def inbox_counts(db, root, state):
    counts = dict.fromkeys(DOMAINS, 0)
    for item in pending(db, root, state):
        counts[item["domain"]] += 1
    require(rehydrate(root) == state, "Current hat sich während der Inbox-Abfrage geändert")
    return counts


def prepare(db, root, version, receipts):
    state = rehydrate(root)
    require(version_key(version) > version_key(state["version"]), "Release-Version muss steigen")
    require(not (root / "releases" / version).exists(), "Release-Version existiert bereits")
    require(receipts and len(set(receipts)) == len(receipts), "Eindeutige Einreichungen auswählen")
    inbox = {item["receipt"]: item for item in pending(db, root, state)}
    records = {domain: live_records(root, state, domain) for domain in DOMAINS}
    for receipt in receipts:
        require(receipt in inbox, f"Einreichung fehlt oder ist bereits im Archiv: {receipt}")
        item = inbox[receipt]
        require(item["status"] != "HOLD", "HOLD / SOURCE_VAULT_ONLY. Einreichung privat fachlich prüfen.")
        records[item["domain"]].append(item["record"])
    require(rehydrate(root) == state, "Current hat sich während der Prüfung geändert")
    return {"system_id": SYSTEM, "base_version": state["version"], "version": version, "records": records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-dir", required=True, type=Path)
    parser.add_argument("--client", required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    show = commands.add_parser("read")
    show.add_argument("domain", choices=DOMAINS)
    show.add_argument("--id")
    intake = commands.add_parser("submit")
    intake.add_argument("domain", choices=DOMAINS)
    intake.add_argument("request_id")
    intake.add_argument("input", type=Path)
    commands.add_parser("pending")
    visual = commands.add_parser("dashboard")
    visual.add_argument("output", type=Path)
    visual.add_argument("--checkpoint", type=Path)
    draft = commands.add_parser("prepare")
    draft.add_argument("version")
    draft.add_argument("output", type=Path)
    draft.add_argument("receipts", nargs="+")
    args = parser.parse_args()
    try:
        private = args.private_dir.resolve()
        require(private.is_dir() and not private.is_relative_to(ROOT.resolve()),
                "Privaten Datenordner außerhalb des 666CLS-Projektordners wählen")
        require(not any((parent / ".git").exists() for parent in (private, *private.parents)),
                "Privater Datenordner muss außerhalb eines Git-Checkouts liegen")
        db = private / "inbox.sqlite3"
        token = os.environ.get("CLS_ARCHIVE_TOKEN")
        action = args.command if args.command in ("read", "submit") else "review"
        authorize(private / "clients.json", args.client, token, action, getattr(args, "domain", None))
        if args.command == "read":
            state = rehydrate(ROOT)
            entries = live_records(ROOT, state, args.domain)
            result = {"version": state["version"], "domain": args.domain, "records": [
                row for row in entries if not args.id or row["id"] == args.id]}
        elif args.command == "submit":
            result = submit(db, args.client, args.request_id, args.domain, read(args.input))
        elif args.command == "pending":
            result = pending(db, ROOT)
        elif args.command == "dashboard":
            from dashboard import render_dashboard
            output = args.output.resolve()
            require(output.is_relative_to(private) and output.suffix.lower() == ".html",
                    "Prüf-Dashboard als HTML im privaten Datenordner anlegen")
            require(not output.exists(), "HTML-Ausgabedatei existiert bereits")
            state = rehydrate(ROOT)
            counts = inbox_counts(db, ROOT, state)
            render_dashboard(ROOT, state, output, args.checkpoint, inbox=counts)
            result = {"status": "VERIFIZIERT", "version": state["version"], "inbox_counts": counts}
        else:
            output = args.output.resolve()
            require(output.is_relative_to(private), "Kandidat muss im privaten Datenordner liegen")
            data = prepare(db, ROOT, args.version, args.receipts)
            with output.open("x", encoding="utf-8") as stream:
                stream.write(json_text(data))
            result = {"status": "CANDIDATE", "base_version": data["base_version"],
                      "candidate": str(output), "accepted_receipts": args.receipts}
        print(json_text(result), end="")
        return 0
    except (ValueError, OSError, TypeError, AttributeError, KeyError, sqlite3.Error) as error:
        print(json_text({"status": "BLOCKIERT", "reason": str(error)}), file=sys.stderr, end="")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
