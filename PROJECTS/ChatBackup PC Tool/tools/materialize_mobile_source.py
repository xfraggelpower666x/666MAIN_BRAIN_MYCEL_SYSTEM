#!/usr/bin/env python3
"""Extrahiert den aktuellen iPhone-Companion in separat bearbeitbare Git-Dateien.
Keine Ausführung von Archivcode. Ohne --write ausschließlich Prüfung.
"""
import argparse
import hashlib
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "mobile_scriptable" / "666_CHATBACKUP_SCRIPTABLE_IPHONE_v1.0.9.zip"
TARGET = ROOT / "mobile_scriptable" / "source"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="Quellcode entpacken")
    args = ap.parse_args()
    if not ARCHIVE.is_file():
        print("MISSING", ARCHIVE)
        return 2
    with zipfile.ZipFile(ARCHIVE) as z:
        entries = [(n, PurePosixPath(n)) for n in z.namelist() if not n.endswith("/")]
        if not entries:
            return 2
        for name, path in entries:
            if path.is_absolute() or ".." in path.parts or len(path.parts) < 2:
                print("UNSAFE_ENTRY", name)
                return 2
        prefix = entries[0][1].parts[0]
        if any(p.parts[0] != prefix for _, p in entries):
            print("MIXED_ROOT")
            return 2
        print("SOURCE_FILES", len(entries), "TARGET", TARGET)
        for name, path in entries:
            rel = Path(*path.parts[1:])
            data = z.read(name)
            destination = TARGET / rel
            if not args.write:
                print("CHECK", rel, hashlib.sha256(data).hexdigest())
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists() and destination.read_bytes() != data:
                print("CONFLICT_KEEP_EXISTING", destination)
                return 3
            destination.write_bytes(data)
            print("WRITTEN", rel)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
