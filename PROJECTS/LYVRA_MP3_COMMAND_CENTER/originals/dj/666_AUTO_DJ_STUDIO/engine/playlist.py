"""Non-destructive M3U creation with exclusive file reservation."""
from pathlib import Path
import os, tempfile

def safe_playlist_path(root,name='AUTO_DJ_EXPORT'):
    """Compatibility entry point: validate the playlist basename, do not write."""
    root=Path(root).resolve()
    if not name or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in name):
        raise ValueError('Invalid playlist name')
    return root/(name+'.m3u')

def export_m3u(root,tracks,name='AUTO_DJ_EXPORT'):
    root=Path(root).resolve()
    tracks=[Path(p).resolve() for p in tracks]
    if not tracks or not root.is_dir() or any(p.parent!=root or not p.is_file() or p.suffix.lower()!='.mp3' for p in tracks):
        raise ValueError('M3U accepts only completed MP3 files inside output directory')
    if not name or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in name):
        raise ValueError('Invalid playlist name')
    for i in range(10000):
        destination=root/(name+(f'_{i}' if i else '')+'.m3u')
        reserved=False
        try:
            with destination.open('x',encoding='utf-8',newline='\n') as out:
                reserved=True
                out.write('#EXTM3U\n')
                for track in tracks:
                    out.write(track.name.replace('\n',' ').replace('\r',' ')+'\n')
                out.flush();os.fsync(out.fileno())
            return destination
        except FileExistsError:
            continue
        except BaseException:
            if reserved: destination.unlink(missing_ok=True)
            raise
    raise RuntimeError('No free playlist filename')
