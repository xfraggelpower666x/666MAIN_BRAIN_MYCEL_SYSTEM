"""L.Y.V.R.A. Electron candidate worker; media tools remain original authority.
JSON-lines stdout protocol; only requested operations; no shell usage.
"""
import json, os, sys, threading, traceback, shutil, hashlib, re
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT=Path(__file__).resolve().parent.parent/'L.Y.V.R.A._MP3_MANAGER'
sys.path.insert(0, str(ROOT))
from media_tools import inspect_media, export_media

CANCEL=threading.Event()
OUTPUT_LOCK=threading.Lock()

def emit(kind, **kwargs):
    with OUTPUT_LOCK:
        sys.stdout.write(json.dumps({'type':kind,**kwargs}, ensure_ascii=False)+'\n')
        sys.stdout.flush()

def watch_cancel():
    for line in sys.stdin:
        if line.strip() == 'CANCEL':
            CANCEL.set();return

def tools():
    base=Path(sys.executable).resolve().parent
    dirs=[ROOT/'tools',ROOT/'bin',Path(__file__).resolve().parent/'tools',base]
    result=[]
    for tool in ('ffmpeg','ffprobe'):
        candidates=[p/(tool+'.exe') for p in dirs]+[p/tool for p in dirs]
        found=next((str(x) for x in candidates if x.is_file()), None) or shutil.which(tool)
        if not found:raise RuntimeError(f'{tool} fehlt: Kein System- oder Projektwerkzeug vorhanden')
        result.append(found)
    return result

def safe_publish(src,dst):
    """Exclusive copy works across FAT/exFAT and avoids overwriting existing output."""
    src,dst=Path(src),Path(dst)
    fd=None
    created=False
    try:
        fd=os.open(str(dst), os.O_CREAT|os.O_EXCL|os.O_WRONLY|getattr(os,'O_BINARY',0), 0o666)
        created=True
        with os.fdopen(fd,'wb') as handle,open(src,'rb') as inp:
            fd=None
            while True:
                if CANCEL.is_set(): raise InterruptedError('Abgebrochen')
                block=inp.read(1024*1024)
                if not block:break
                handle.write(block)
            handle.flush();os.fsync(handle.fileno())
    except BaseException:
        if fd is not None:os.close(fd)
        if created:
            try:dst.unlink(missing_ok=True)
            except OSError:pass
        raise

def metadata(path):
    try:
        from mutagen.id3 import ID3, ID3NoHeaderError
        try: tags=ID3(path)
        except ID3NoHeaderError:tags=ID3()
        out={}
        for key in ('TIT2','TPE1','TPE2','TALB','TCON','TCOM','TDRC','TRCK','TPOS'):
            value=tags.get(key)
            out[key]=str(value.text[0]) if value is not None and value.text else ''
        out['cover']=bool(tags.getall('APIC'))
        return out
    except ImportError:return {'warning':'mutagen fehlt'}

def metadata_copy(source, target, fields):
    """Create a separately named ID3-edited MP3; never alter source or overwrite destination."""
    from mutagen.id3 import ID3, ID3NoHeaderError, TIT2, TPE1, TPE2, TALB, TCON, TCOM, TDRC, TRCK, TPOS
    from mutagen.mp3 import MP3
    mapping={'TIT2':TIT2,'TPE1':TPE1,'TPE2':TPE2,'TALB':TALB,
             'TCON':TCON,'TCOM':TCOM,'TDRC':TDRC,'TRCK':TRCK,'TPOS':TPOS}
    if not isinstance(fields,dict) or not fields or set(fields)-set(mapping):
        raise ValueError('Ungültige ID3-Feldauswahl')
    if source.suffix.lower()!='.mp3' or target.suffix.lower()!='.mp3':
        raise ValueError('ID3-Bearbeitung nur für MP3')
    if source.resolve()==target.resolve() or os.path.lexists(target):
        raise FileExistsError('Original/Zieldatei ist geschützt')
    if not target.parent.is_dir():raise FileNotFoundError('Zielordner fehlt')
    with TemporaryDirectory(prefix='lyvra-id3-',dir=str(target.parent)) as tmp:
        stage=Path(tmp)/'edit.mp3'
        shutil.copyfile(source,stage)
        if CANCEL.is_set():raise InterruptedError('Abgebrochen')
        audio=MP3(str(stage))  # fail closed for invalid input
        try: tags=ID3(str(stage))
        except ID3NoHeaderError:tags=ID3()
        for key,value in fields.items():
            if not isinstance(value,str) or len(value)>2048 or '\x00' in value:
                raise ValueError('Ungültiger ID3-Wert')
            tags.delall(key)
            if value.strip():tags.add(mapping[key](encoding=3,text=[value.strip()]))
        tags.save(str(stage),v2_version=3)
        verify=ID3(str(stage))
        for key,value in fields.items():
            item=verify.get(key)
            actual=str(item.text[0]) if item is not None and item.text else ''
            if actual!=value.strip():raise RuntimeError('ID3-Readback fehlgeschlagen: '+key)
        MP3(str(stage))  # ensure file is still decodable by mutagen
        if CANCEL.is_set():raise InterruptedError('Abgebrochen')
        safe_publish(stage,target)
    return {'destination':str(target),'bytes':target.stat().st_size,
            'tags':metadata(str(target)),'source_preserved':True,'verified':'ID3_READBACK_PASS'}

def rename_preview(name):
    stem=Path(name).stem
    stem=re.sub(r'\s*\[\d+m\d+s\s*-\s*\d+m\d+s\]','',stem,flags=re.I)
    stem=re.sub(r'\s*\((\d+)\)$',r' \1',stem).strip()
    return stem + Path(name).suffix

def main(request):
    action=request.get('action')
    if action=='check':
        ff,fp=tools()
        emit('result',data={'ffmpeg':ff,'ffprobe':fp,'engine':'original media_tools.py','scope':'Electron migration candidate'})
        return
    if action=='inspect':
        ff,fp=tools()
        path=Path(request['source']).resolve(strict=True)
        info=inspect_media(fp,path,CANCEL)
        emit('result',data={'source':str(path),'size':path.stat().st_size,'format':info.get('format',{}),'streams':info.get('streams',[]),'tags':metadata(path) if path.suffix.lower()=='.mp3' else {},'rename_preview':rename_preview(path.name)})
        return
    if action=='metadata_copy':
        source=Path(request['source']).resolve(strict=True)
        target=Path(request['destination']).absolute()
        emit('phase',message='ID3-Kopie und Readback')
        result=metadata_copy(source,target,request.get('fields'))
        emit('result',data=result)
        return
    if action=='export':
        ff,fp=tools()
        source=Path(request['source']).resolve(strict=True)
        target=Path(request['destination']).absolute()
        if not target.parent.is_dir():raise FileNotFoundError('Zielordner fehlt')
        if os.path.lexists(target):raise FileExistsError('Zieldatei existiert')
        stream=int(request.get('stream',0))
        images=[str(Path(i).resolve(strict=True)) for i in request.get('images',[])]
        if len(images)>12:raise ValueError('Maximal 12 Bilder')
        def progress(value,elapsed,position):
            emit('progress',fraction=(round(float(value),4) if value is not None else None),elapsed=round(elapsed,2),position=round(position,2))
        def phase(msg):emit('phase',message=msg)
        export_media(ff,fp,source,stream,target,CANCEL,progress,safe_publish,images=images,fade=bool(request.get('fade',True)),size=(int(request.get('width',1280)),int(request.get('height',720))),phase=phase)
        emit('result',data={'destination':str(target),'bytes':target.stat().st_size,'status':'TECHNICAL_DECODE_PASS','perceptual_quality':'NOT_TESTED'})
        return
    raise ValueError('Aktion nicht erlaubt')

if __name__=='__main__':
    try:
        msg=json.loads(sys.stdin.readline())
        threading.Thread(target=watch_cancel,daemon=True).start()
        main(msg)
    except (Exception,KeyboardInterrupt) as exc:
        emit('error',message=str(exc),error_type=exc.__class__.__name__)
        sys.exit(1)
