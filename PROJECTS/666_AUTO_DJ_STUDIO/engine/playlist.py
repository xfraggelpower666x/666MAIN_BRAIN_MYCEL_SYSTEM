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
    dest = None
    created = False
    fd, temp_path = tempfile.mkstemp(prefix=".autodj_m3u_", suffix=".tmp", dir=root)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as out:
            out.write("#EXTM3U\n")
            for track in resolved:
                out.write(track.name.replace("\n", " ").replace("\r", " ") + "\n")
            out.flush()
            os.fsync(out.fileno())
        # Reserve a unique path exclusively; a concurrent writer's playlist is never deleted.
        for _ in range(10000):
            dest = safe_playlist_path(root, name)
            try:
                with dest.open("xb") as target:
                    created = True
                    with open(temp_path, "rb") as source:
                        while chunk := source.read(65536):
                            target.write(chunk)
                    target.flush()
                    os.fsync(target.fileno())
                return dest
            except FileExistsError:
                if created:
                    raise
                continue
        raise RuntimeError("Playlist filename collision limit")
    except BaseException:
        # Remove only a file that this invocation created.
        if created and dest is not None:
            dest.unlink(missing_ok=True)
        raise
    finally:
        Path(temp_path).unlink(missing_ok=True)
