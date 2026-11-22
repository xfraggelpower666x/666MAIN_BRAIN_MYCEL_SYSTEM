"""M3U export for successful AutoDJ render outputs; additive, non-destructive."""
import os
from pathlib import Path
import tempfile

def safe_playlist_path(root: Path, name: str = "AUTO_DJ_EXPORT") -> Path:
    if not name or any(char not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-" for char in name):
        raise ValueError("Invalid playlist name")
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError("Output directory is missing")
    for number in range(10000):
        dest = root / (name + (("_" + str(number)) if number else "") + ".m3u")
        if not dest.exists():
            return dest
    raise RuntimeError("Playlist filename collision limit")

def export_m3u(root: Path, tracks, name: str = "AUTO_DJ_EXPORT") -> Path:
    root = Path(root).resolve()
    if not tracks:
        raise ValueError("No successful audio exports to list")
    resolved = [Path(p).resolve() for p in tracks]
    if any(p.parent != root or not p.is_file() or p.suffix.lower() != ".mp3" for p in resolved):
        raise ValueError("Playlist entries must be exported MP3 files in output directory")
    dest = safe_playlist_path(root, name)
    fd, temp_path = tempfile.mkstemp(prefix=".autodj_m3u_", suffix=".tmp", dir=root)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as out:
            out.write("#EXTM3U\n")
            for track in resolved:
                out.write(track.name.replace("\n", " ").replace("\r", " ") + "\n")
            out.flush()
            os.fsync(out.fileno())
        # Exclusive creation prevents overwriting existing exports on races.
        with open(temp_path, "rb") as source, open(dest, "xb") as target:
            while chunk := source.read(65536):
                target.write(chunk)
        return dest
    except BaseException:
        # Incomplete playlists are not left as legitimate outputs.
        if dest.exists():
            dest.unlink()
        raise
    finally:
        Path(temp_path).unlink(missing_ok=True)
