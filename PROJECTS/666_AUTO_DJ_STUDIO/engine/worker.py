"""666 AUTO DJ STUDIO — existing single-track processing plus optional block workflow."""
import argparse
import json
import math
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path

from playlist import export_m3u
from legacy_planner import catalog, balanced_blocks, smart_shuffle

PROFILES = {
    "stream": ["-af", "loudnorm=I=-14:TP=-1.5:LRA=11"],
    "dj": ["-af", "loudnorm=I=-10:TP=-1.0:LRA=9"],
    "custom": [],
}
EXT = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".aiff", ".wma"}


def destination(src, root):
    for n in range(100000):
        p = root / (src.stem + (f"_{n}" if n else "") + ".mp3")
        if not p.exists():
            return p
    raise RuntimeError("Output collision limit")


def validate(data):
    files = [Path(p).resolve() for p in data.get("files", [])]
    root = Path(data.get("output", "")).resolve()
    if not files or not root.is_dir() or any(not f.is_file() or f.suffix.lower() not in EXT for f in files):
        raise ValueError("Invalid files or output folder")
    profile = data.get("profile", "stream")
    if profile not in PROFILES:
        raise ValueError("Invalid profile")
    bitrate = int(data.get("bitrate", 256))
    if bitrate not in (256, 320):
        raise ValueError("Invalid bitrate")
    return files, root, profile, bitrate


def emit(**kw):
    print(json.dumps(kw, ensure_ascii=False), flush=True)


def probe_duration(path, ffprobe):
    command = [ffprobe, "-v", "error", "-show_entries", "format=duration",
               "-of", "default=noprint_wrappers=1:nokey=1", str(path)]
    result = subprocess.run(command, capture_output=True, timeout=90, check=True)
    duration = float(result.stdout.decode("utf-8", errors="replace").strip())
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("Invalid duration: " + path.name)
    return duration


def plan_blocks(files, data, ffprobe):
    split_mode = str(data.get("split_mode", "MINUTES")).upper()
    minutes = int(data.get("target_minutes", 180))
    tracks = int(data.get("target_tracks", 40))
    if split_mode not in ("MINUTES", "TRACKS", "HYBRID") or not 1 <= minutes <= 10080 or not 1 <= tracks <= 10000:
        raise ValueError("Invalid AutoDJ block settings")
    seed = data.get("shuffle_seed")
    rng = random.Random(int(seed)) if seed is not None else random.Random()
    entries = []
    for index, src in enumerate(files, 1):
        duration = probe_duration(src, ffprobe)
        entries.append((src, duration))
        emit(done=0, total=len(files), message=f"PROBE {index}/{len(files)}: {src.name}")
    groups = catalog(entries, rng)
    blocks = balanced_blocks(groups, split_mode, minutes, tracks)
    hardcore = data.get("hardcore") is True
    return [(block.index, smart_shuffle(block.items, hardcore)) for block in blocks]


def render_one(src, root, profile, bitrate, ffmpeg):
    # Unique temporary output in the destination directory; originals are never modified.
    dest = destination(src, root)
    fd, temporary_name = tempfile.mkstemp(prefix="autodj_", suffix=".mp3", dir=root)
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        command = [ffmpeg, "-hide_banner", "-nostdin", "-loglevel", "error", "-y",
                   "-i", str(src), *PROFILES[profile], "-codec:a", "libmp3lame",
                   "-b:a", str(bitrate) + "k", str(temporary)]
        result = subprocess.run(command, capture_output=True, timeout=7200)
        if result.returncode or temporary.stat().st_size == 0:
            raise RuntimeError(result.stderr.decode(errors="replace")[-900:])
        # Never overwrite a file already present in the output directory.
        with open(temporary, "rb") as source, dest.open("xb") as target:
            while chunk := source.read(1024 * 1024):
                target.write(chunk)
        return dest
    except BaseException:
        # Any partially written destination belongs to this attempt alone.
        if "target" in locals() and dest.exists():
            dest.unlink(missing_ok=True)
        raise
    finally:
        temporary.unlink(missing_ok=True)


def process(data, ffmpeg, ffprobe=None):
    files, root, profile, bitrate = validate(data)
    block_mode = data.get("block_mode") is True
    if block_mode:
        if not ffprobe:
            raise ValueError("FFprobe is required for block planning")
        planned = plan_blocks(files, data, ffprobe)
    else:
        planned = [(None, files)]
    success = 0
    failures = 0
    overall = len(files)
    for block_index, members in planned:
        block_root = root
        if block_index is not None:
            # Never mix a new render with a previous BLOCK_ directory.
            block_root = root / ("BLOCK_" + str(block_index).zfill(3))
            if block_root.exists():
                for suffix in range(1, 10000):
                    alternate = root / (f"BLOCK_{block_index:03d}_{suffix}")
                    if not alternate.exists():
                        block_root = alternate
                        break
                else:
                    raise RuntimeError("Block directory collision limit")
            block_root.mkdir(parents=False, exist_ok=False)
        exported = []
        for member in members:
            src = member.path if block_mode else member
            try:
                dst = render_one(src, block_root, profile, bitrate, ffmpeg)
                success += 1
                exported.append(dst)
                emit(done=success + failures, total=overall,
                     message=f"OK: {src.name} -> {dst.name}",
                     block=block_index)
            except Exception as exc:
                failures += 1
                emit(done=success + failures, total=overall,
                     message=f"ERROR: {src.name}: {exc}", block=block_index)
        if data.get("export_m3u") and exported:
            try:
                playlist = export_m3u(block_root, exported)
                emit(done=success + failures, total=overall,
                     message="M3U: " + str(playlist), block=block_index)
            except Exception as exc:
                emit(message="M3U ERROR: " + str(exc), block=block_index)
                failures += 1
    return 0 if failures == 0 and success == overall else 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-json", default="-")
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--ffprobe", default="ffprobe")
    args = parser.parse_args()
    try:
        data = json.load(sys.stdin) if args.input_json == "-" else json.loads(Path(args.input_json).read_text())
        return process(data, args.ffmpeg, args.ffprobe)
    except Exception as exc:
        emit(message="FATAL: " + str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
