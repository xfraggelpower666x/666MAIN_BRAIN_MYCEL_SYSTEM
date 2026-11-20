"""Verify an immutable freeze ZIP against its complete internal SHA-256 list."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import stat
from zipfile import BadZipFile, ZipFile


def member_path(name):
    if not name or "\\" in name or ":" in name or any(
        part in ("", ".", "..") for part in name.split("/")
    ) or any(ord(char) < 32 for char in name):
        raise ValueError(f"Invalid archive member path: {name!r}")
    return name


def verify(archive, manifest="MANIFEST.json", checksums="SHA256SUMS.txt", checksum_base=""):
    manifest, checksums = member_path(manifest), member_path(checksums)
    prefix = member_path(checksum_base) + "/" if checksum_base else ""
    if manifest == checksums:
        raise ValueError("Manifest and checksum list must be separate files")

    with ZipFile(archive) as bundle:
        files = {}
        seen = set()
        for entry in bundle.infolist():
            if entry.orig_filename != entry.filename:
                raise ValueError("ZIP member name was normalized or truncated")
            name = member_path(entry.filename.removesuffix("/") if entry.is_dir() else entry.filename)
            if name in seen:
                raise ValueError(f"Duplicate ZIP member: {name!r}")
            seen.add(name)
            kind = stat.S_IFMT(entry.external_attr >> 16)
            if kind not in (0, stat.S_IFDIR if entry.is_dir() else stat.S_IFREG):
                raise ValueError(f"Unsupported ZIP member type: {name!r}")
            if not entry.is_dir():
                files[name] = entry
        if manifest not in files or checksums not in files:
            raise ValueError("Required manifest or checksum list missing")
        if files[checksums].file_size > 4 * 1024 * 1024:
            raise ValueError("Checksum list exceeds 4 MiB")

        expected = {}
        for line in bundle.read(checksums).decode("utf-8-sig").splitlines():
            if not line.strip():
                continue
            record = re.fullmatch(r"([a-fA-F0-9]{64})[ \t]+\*?(.+)", line)
            if record is None:
                raise ValueError("Invalid SHA-256 record")
            value, name = record.groups()
            name = prefix + member_path(name.removeprefix("./"))
            if name == checksums or name in expected:
                raise ValueError(f"Self-reference or duplicate checksum: {name!r}")
            expected[name] = value.lower()

        coverage = files.keys() - {checksums}
        missing = sorted(coverage - expected.keys())
        absent = sorted(expected.keys() - coverage)
        mismatches = []
        common = coverage & expected.keys()
        # Bis EOF lesen, damit zipfile neben SHA-256 auch den CRC jedes Eintrags prüft.
        for name in sorted(coverage):
            with bundle.open(files[name]) as stream:
                digest = hashlib.sha256()
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            if name in common and digest.hexdigest() != expected[name]:
                mismatches.append(name)

    ok = not (missing or absent or mismatches)
    return {
        "status": "ARCHIVE_INTEGRITY_VERIFIED" if ok else "ARCHIVE_INTEGRITY_MISMATCH",
        "manifest": manifest,
        "verified_members": len(common) - len(mismatches),
        "unlisted_members": missing,
        "missing_members": absent,
        "hash_mismatches": mismatches,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--manifest", default="MANIFEST.json", help="Exact ZIP-root-relative manifest path")
    parser.add_argument("--checksums", default="SHA256SUMS.txt", help="Exact ZIP-root-relative checksum list path")
    parser.add_argument("--checksum-base", default="", help="ZIP directory used as base for checksum entries")
    args = parser.parse_args()
    try:
        report = verify(args.archive, args.manifest, args.checksums, args.checksum_base)
    except (OSError, ValueError, BadZipFile, RuntimeError, NotImplementedError) as error:
        parser.exit(2, f"{error}\n")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "ARCHIVE_INTEGRITY_VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
