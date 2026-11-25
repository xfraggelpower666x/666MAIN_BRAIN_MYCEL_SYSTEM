"""Original R03 STREAM_READY stage/backup/publish semantics, additive to block export.
No old STREAM_READY tree is removed. Failures attempt rollback to the previous export.
"""
from pathlib import Path
import shutil
import uuid


def _guard(root, blocks):
    root=Path(root).resolve()
    checked=[]
    for block in blocks:
        block=Path(block).resolve()
        if block.parent!=root or not block.is_dir() or not block.name.startswith('BLOCK_'):
            raise ValueError('Unsafe block for master export')
        if block in checked:raise ValueError('Duplicate block folder')
        checked.append(block)
    if not checked:raise ValueError('No completed blocks for master export')
    return root,checked

def export_stream_ready(root, blocks):
    root,blocks=_guard(root,blocks)
    stage=root/('_STREAM_READY_STAGE_'+uuid.uuid4().hex)
    output=root/'STREAM_READY'
    previous=None
    stage.mkdir(exist_ok=False)
    lines=['#EXTM3U']
    published=False
    try:
        for block in blocks:
            dest=stage/block.name
            shutil.copytree(block,dest,symlinks=False)
            play=sorted(dest.glob('*.m3u'))
            if play:
                entries=[s.strip() for s in play[0].read_text(encoding='utf-8-sig').splitlines() if s.strip() and not s.startswith('#')]
                for entry in entries:
                    relative=Path(entry)
                    if relative.is_absolute() or '..' in relative.parts or len(relative.parts)!=1:
                        raise ValueError('Unsafe playlist entry in '+block.name)
                    if not (dest/relative).is_file():raise ValueError('Missing master playlist track: '+entry)
                    lines.append((Path(block.name)/relative).as_posix())
            else:
                lines.extend((Path(block.name)/p.name).as_posix() for p in sorted(dest.iterdir()) if p.is_file() and p.suffix.lower() in ('.mp3','.wav'))
        (stage/'master.m3u').write_text('\n'.join(lines)+'\n',encoding='utf-8-sig')
        if output.exists():
            if not output.is_dir():raise ValueError('STREAM_READY is not a directory')
            previous=root/('STREAM_READY_PREVIOUS_'+uuid.uuid4().hex)
            output.rename(previous)
        try:
            stage.rename(output)
            published=True
        except BaseException:
            if previous is not None and not output.exists():previous.rename(output)
            raise
        return output,previous
    finally:
        if not published and stage.exists():shutil.rmtree(stage)
