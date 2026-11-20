"""Repository-nativer Start, Archivprüfung und kontrollierte lokale Releases."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
SYSTEM = "666CLS-CORE-001"
AUTHORITY = {"repository": "xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM",
             "branch": "666MAIN_BRAIN", "root": "PROJECTS/666CLS"}
DOMAINS = {"LYRICS": "LYRIC", "RAW_MATERIAL": "RAW_MATERIAL", "STORIES": "STORY", "TEXT": "TEXT"}
SCHEMA = "1.12.0"
TRIGGERS = {"666CLS SYSTEMSTART": "status", "666CLS WEITER": "continue", "666CLS UPDATE": "update"}
VERSION = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}")
SENSITIVE_FIELD = re.compile(
    r"password|passphrase|credential|clientsecret|privatekey|apikey|accesstoken|refreshtoken|"
    r"authtoken|bottoken|sessiontoken|sessioncookie|secret|token",
    re.IGNORECASE,
)
SENSITIVE_TEXT = re.compile(
    r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----|"
    r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"sk-(?:proj-)?[A-Za-z0-9_-]{20,})\b|"
    r"\b(?:authorization\s*:\s*bearer|api[_ -]?key\s*[:=]|"
    r"password\s*[:=]|access[_ -]?token\s*[:=])\s*[\x22\x27]?[A-Za-z0-9_./+=!@#%\-]{8,}|"
    r"https?://[^/\s:@]+:[^/\s@]+@",
    re.IGNORECASE,
)
REPO_CONTROLS = (
    "control/AUTHORITY.json", "control/BOOTSTRAP.json", "control/FRAMEWORK.md",
    "control/SYSTEM_REGISTRY.json", "continuity/LIVECIRCLE.json", "control/INTEGRATIONS.json",
)
DATA_PATHS = tuple(f"{directory}/{domain}_{suffix}.json" for domain in DOMAINS
                   for directory, suffix in (("DATABASE", "ARCHIVE"), ("MENU", "MENU")))
REQUIRED_RELEASE_FILES = {*DATA_PATHS, "AUDIT.json"}


def read(path):
    def unique(pairs):
        result = dict(pairs)
        if len(result) != len(pairs):
            raise ValueError(f"Doppelter JSON-Schlüssel in {path.name}")
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)


def json_text(value):
    return json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json_text(value), encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def version_key(version):
    require(isinstance(version, str) and VERSION.fullmatch(version), "Ungültige Release-Version")
    return tuple(map(int, version.split(".")))


def entries_by_id(entries, domain):
    require(isinstance(entries, list), f"{domain}: entries muss eine Liste sein")
    indexed = {}
    for entry in entries:
        require(isinstance(entry, dict), f"{domain}: Datensatz muss ein Objekt sein")
        ident = entry.get("id")
        require(isinstance(ident, str) and ID.fullmatch(ident) and ident not in indexed,
                f"{domain}: ungültige oder doppelte ID")
        title = entry.get("title")
        require(isinstance(title, str) and title.strip(), f"{domain}/{ident}: Titel fehlt")
        require(any(isinstance(entry.get(key), str) and entry[key].strip()
                    for key in ("source_text", "canonical_text", "clean_text", "normalized_text"))
                or (domain == "RAW_MATERIAL" and bool(entry.get("source_vault_ref"))),
                f"{domain}/{ident}: Text oder Quellenreferenz fehlt")
        indexed[ident] = entry
    return indexed


def requires_source_vault(value):
    """Erkennbare Zugangsdaten bleiben im privaten Quellenbestand."""
    if isinstance(value, dict):
        return any(
            (SENSITIVE_FIELD.fullmatch(re.sub(r"[_ -]", "", key)) and bool(item))
            or requires_source_vault(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(requires_source_vault(item) for item in value)
    return isinstance(value, str) and SENSITIVE_TEXT.search(value) is not None


def menu_for(entries, domain):
    result = {"schema_version": SCHEMA, "content_type": DOMAINS[domain],
              "menu_count": len(entries), "menu": []}
    families = {}
    for ident, entry in entries.items():
        row = {key: entry[key] for key in ("id", "title", "version", "family_id", "family_title",
                                           "status", "source_entry_indices") if key in entry}
        row["content_ref"] = f"DATABASE/{domain}_ARCHIVE.json#{ident}"
        result["menu"].append(row)
        if domain == "LYRICS" and entry.get("family_id"):
            family_id = entry["family_id"]
            require(isinstance(family_id, str), "LYRICS: ungültige Familien-ID")
            family = families.setdefault(family_id, {
                "family_id": family_id, "family_title": entry.get("family_title", family_id), "members": []})
            family["members"].append(ident)
    if domain == "LYRICS":
        result["families"] = list(families.values())
    return result


def inspect_data(release):
    counts = {}
    seen = set()
    for domain, kind in DOMAINS.items():
        db = read(release / f"DATABASE/{domain}_ARCHIVE.json")
        menu = read(release / f"MENU/{domain}_MENU.json")
        require(db["schema_version"] == SCHEMA and db["content_type"] == kind,
                f"{domain}: Datenbankschema oder Inhaltstyp weicht ab")
        indexed = entries_by_id(db["entries"], domain)
        require(type(db["entry_count"]) is int and db["entry_count"] == len(indexed),
                f"{domain}: Datenbankzähler weicht ab")
        require(menu == menu_for(indexed, domain), f"{domain}: Menüparität verletzt")
        require(not seen.intersection(indexed), f"{domain}: ID überschneidet Archivbereiche")
        seen.update(indexed)
        counts[domain] = len(indexed)
    return counts


def inspect_release(release, version):
    manifest = read(release / "MANIFEST.json")
    require(manifest["system_id"] == SYSTEM and manifest["version"] == version
            and manifest["schema_version"] == SCHEMA, "Release-Identität stimmt nicht")
    paths = set(manifest["sha256"])
    require(REQUIRED_RELEASE_FILES <= paths <= REQUIRED_RELEASE_FILES | {"FREEZE.json"},
            "Release-Inventar weicht ab")
    for name, expected in manifest["sha256"].items():
        require(sha(release / name) == expected, f"Prüfsumme weicht ab: {name}")
    counts = inspect_data(release)
    audit = read(release / "AUDIT.json")
    require(audit["version"] == version and audit["status"] == "VERIFIZIERT"
            and manifest["domains"] == audit["domains"] == counts, "Audit und Release weichen ab")
    if "FREEZE.json" in paths:
        freeze = read(release / "FREEZE.json")
        require(freeze["system_id"] == SYSTEM and freeze["version"] == version,
                "Freeze und Release weichen ab")
    return counts


def rehydrate(root):
    pointer = read(root / "CURRENT_POINTER.json")
    version = pointer["current_version"]
    version_key(version)
    release_path = f"releases/{version}"
    require(pointer["system_id"] == SYSTEM and pointer["authority"] == AUTHORITY
            and pointer["release_path"] == release_path, "Current Pointer oder Authority ungültig")
    for name, expected in pointer["controls"].items():
        require(name in REPO_CONTROLS and sha(root / name) == expected, f"Steuerdatei abweichend: {name}")
    require(set(pointer["controls"]) == set(REPO_CONTROLS), "Steuerinventar unvollständig")
    authority, bootstrap, _, registry, circle, integrations = [
        read(root / name) if name.endswith(".json") else None for name in REPO_CONTROLS]
    require(all(obj["system_id"] == SYSTEM for obj in (authority, bootstrap, registry, circle, integrations)),
            "Native System-ID weicht ab")
    require(authority["authority"] == AUTHORITY and circle["authority"] == AUTHORITY
            and bootstrap["triggers"] == circle["triggers"] == TRIGGERS
            and registry["domains"] == DOMAINS and registry["schema_version"] == SCHEMA,
            "Authority, Trigger oder Archivschema weichen ab")
    for item in integrations["integrations"]:
        for name, expected in item["sha256"].items():
            path = root / name
            require(path.resolve().is_relative_to(root.resolve()) and sha(path) == expected,
                    f"Integration weicht ab: {name}")
    release = root / release_path
    require(sha(release / "MANIFEST.json") == pointer["manifest_sha256"], "Release-Manifest weicht ab")
    counts = inspect_release(release, version)
    require(pointer["domains"] == counts, "Pointer-Zähler weichen ab")
    return {"status": "VERIFIZIERT", "system_id": SYSTEM, "version": version,
            "domains": counts, "total": sum(counts.values()), "schema_version": SCHEMA,
            "authority": AUTHORITY, "source": release_path, "next_step": circle["next_step"]}


def build_release(release, version, records, phase):
    require(isinstance(records, dict) and set(records) == set(DOMAINS), "Vier Archivbereiche erforderlich")
    for domain, kind in DOMAINS.items():
        entries = entries_by_id(records[domain], domain)
        require(not any(requires_source_vault(entry) for entry in entries.values()),
                f"{domain}: HOLD / SOURCE_VAULT_ONLY. Eintrag privat fachlich prüfen.")
        write(release / f"DATABASE/{domain}_ARCHIVE.json",
              {"schema_version": SCHEMA, "content_type": kind,
               "entry_count": len(entries), "entries": list(entries.values())})
        write(release / f"MENU/{domain}_MENU.json", menu_for(entries, domain))
    counts = inspect_data(release)
    write(release / "AUDIT.json", {"version": version, "status": "VERIFIZIERT",
          "domains": counts, "phase": phase, "checks": ["Schema", "IDs", "Menüparität", "Zähler"]})
    write(release / "MANIFEST.json", {"system_id": SYSTEM, "version": version,
          "schema_version": SCHEMA, "domains": counts,
          "sha256": {name: sha(release / name) for name in (*DATA_PATHS, "AUDIT.json")}})
    inspect_release(release, version)
    return counts


def pointer_for(root, release, version, counts):
    return {"system_id": SYSTEM, "authority": AUTHORITY, "current_version": version,
            "release_path": f"releases/{version}", "domains": counts,
            "manifest_sha256": sha(release / "MANIFEST.json"),
            "controls": {name: sha(root / name) for name in REPO_CONTROLS}}


def backup_current(root, current, backup_dir):
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = Path(tempfile.mkdtemp(prefix="666CLS-", dir=backup_dir)) / f"pre-update-{current['version']}.zip"
    files = {root / "CURRENT_POINTER.json", *(root / name for name in REPO_CONTROLS)}
    for release in (root / "releases").iterdir():
        if release.is_dir() and VERSION.fullmatch(release.name):
            inspect_release(release, release.name)
            files.update(release / name for name in (*read(release / "MANIFEST.json")["sha256"], "MANIFEST.json"))
    integrations = read(root / "control/INTEGRATIONS.json")
    for item in integrations["integrations"]:
        files.update(root / name for name in item["sha256"])
    expected = {p.relative_to(root).as_posix(): sha(p) for p in sorted(files)}
    with backup.open("xb") as stream, ZipFile(stream, "w", ZIP_DEFLATED) as z:
        for name in expected:
            z.write(root / name, name)
    with ZipFile(backup) as z:
        actual = {name: hashlib.sha256(z.read(name)).hexdigest() for name in z.namelist()}
        require(actual == expected and z.testzip() is None, "Sicherung: Readback fehlgeschlagen")
    return backup


def update(root, candidate_path, backup_dir):
    require(not backup_dir.resolve().is_relative_to(root.resolve()),
            "Sicherung außerhalb des Projektordners ablegen")
    lock = root / ".666cls-update.lock"
    lock.mkdir()
    try:
        current = rehydrate(root)
        candidate = read(candidate_path)
        require(candidate["system_id"] == SYSTEM and candidate["base_version"] == current["version"],
                "Update-Basis ist veraltet oder systemfremd")
        version = candidate["version"]
        require(version_key(version) > version_key(current["version"]), "Release-Version muss steigen")
        target = root / "releases" / version
        require(not target.exists(), "Release-Version existiert bereits")
        with tempfile.TemporaryDirectory(prefix=".666cls-stage-", dir=root) as staging:
            stage = Path(staging)
            release = stage / "release"
            counts = build_release(release, version, candidate["records"], "LOCAL_REAUDIT")
            backup = backup_current(root, current, backup_dir)
            require(rehydrate(root) == current, "Current hat sich während des Updates geändert")
            pointer = stage / "CURRENT_POINTER.json"
            write(pointer, pointer_for(root, release, version, counts))
            os.rename(release, target)
            try:
                inspect_release(target, version)
                os.replace(pointer, root / "CURRENT_POINTER.json")
            except (OSError, ValueError, KeyError):
                shutil.rmtree(target)
                raise
        result = rehydrate(root)
        return {**result, "backup": str(backup), "scope": "LOCAL_CHECKOUT"}
    finally:
        lock.rmdir()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=tuple(TRIGGERS) + ("status",))
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--backup-dir", type=Path)
    parser.add_argument("--dashboard", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    args = parser.parse_args()
    route = TRIGGERS.get(args.command, args.command)
    try:
        if route == "update":
            require(args.candidate and args.backup_dir and not args.dashboard and not args.checkpoint,
                    "UPDATE benötigt --candidate und --backup-dir")
            result = update(ROOT, args.candidate, args.backup_dir)
        else:
            require(not args.candidate and not args.backup_dir, "Update-Argumente nur mit 666CLS UPDATE")
            require(not args.checkpoint or args.dashboard, "UI-Handoff benötigt --dashboard")
            result = rehydrate(ROOT)
            if route == "continue":
                result = {**result, "continuity_anchor": {"system_id": SYSTEM,
                          "authority": AUTHORITY, "version": result["version"],
                          "source": result["source"]}}
            if args.dashboard:
                from dashboard import render_dashboard
                require(not args.dashboard.resolve().is_relative_to(ROOT.resolve()) and
                        args.dashboard.suffix.lower() == ".html", "HTML-Ausgabe außerhalb des Projektordners wählen")
                try:
                    render_dashboard(ROOT, result, args.dashboard, args.checkpoint)
                except ValueError as error:
                    if not args.checkpoint:
                        raise
                    print(f"UI-Handoff übersprungen: {error}", file=sys.stderr)
                    render_dashboard(ROOT, result, args.dashboard, None)
        print(json_text(result), end="")
        return 0
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        print(json_text({"status": "BLOCKIERT", "reason": str(error)}), file=sys.stderr, end="")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
