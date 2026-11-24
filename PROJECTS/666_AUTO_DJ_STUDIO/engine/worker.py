"""Electron-launched Python audio renderer. Existing outputs remain untouched."""
import argparse,json,math,os,random,subprocess,sys,tempfile
from pathlib import Path
from playlist import export_m3u
from legacy_planner import catalog,balanced_blocks,smart_shuffle
from legacy_media import metadata_profile,metadata_ffmpeg_args,CoverRotation
from master_export import export_stream_ready

PROFILES={'stream':['-af','loudnorm=I=-14:TP=-1.5:LRA=11'],'dj':['-af','loudnorm=I=-10:TP=-1.0:LRA=9'],'custom':[]}
EXT={'.mp3','.wav','.flac','.ogg','.m4a','.aac','.aiff','.wma'}

def destination(src,root):
    """Backward-compatible R04 path selection (does not reserve the file)."""
    src=Path(src);root=Path(root)
    for index in range(100000):
        candidate=root/(src.stem+(f'_{index}' if index else '')+'.mp3')
        if not candidate.exists():return candidate
    raise RuntimeError('Output collision limit')

def emit(**kwargs): print(json.dumps(kwargs,ensure_ascii=False),flush=True)

def validate(data):
    files=[Path(p).resolve() for p in data.get('files',[])]
    output=Path(data.get('output','')).resolve()
    if not files or not output.is_dir() or any(not p.is_file() or p.suffix.lower() not in EXT for p in files):
        raise ValueError('Missing files or invalid output folder')
    profile=data.get('profile','stream')
    bitrate=int(data.get('bitrate',256))
    if profile not in PROFILES or bitrate not in (256,320):raise ValueError('Invalid profile or bitrate')
    return files,output,profile,bitrate

def duration(path,ffprobe):
    result=subprocess.run([ffprobe,'-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(path)],capture_output=True,timeout=90,check=True)
    value=float(result.stdout.decode(errors='replace').strip())
    if not math.isfinite(value) or value<=0:raise ValueError('Invalid audio duration')
    return value

def render(src,root,profile,bitrate,ffmpeg,meta=None,cover=None):
    fd,tempname=tempfile.mkstemp(prefix='autodj_',suffix='.mp3',dir=root)
    os.close(fd);temp=Path(tempname)
    dest=None;reserved=False
    try:
        command=[ffmpeg,'-hide_banner','-nostdin','-loglevel','error','-y','-i',str(src)]
        if cover is not None:
            command+=['-i',str(cover),'-map','0:a:0','-map','1:v:0','-c:v','mjpeg',
                      '-id3v2_version','3','-metadata:s:v','title=Cover','-metadata:s:v','comment=Front Cover']
        else:
            command+=['-map','0:a:0']
        command+=PROFILES[profile]+['-codec:a','libmp3lame','-b:a',str(bitrate)+'k']
        command+=metadata_ffmpeg_args(meta,src.stem)
        command += [str(temp)]
        result=subprocess.run(command,capture_output=True,timeout=7200)
        if result.returncode or temp.stat().st_size==0:raise RuntimeError(result.stderr.decode(errors='replace')[-1000:])
        for index in range(10000):
            dest=root/(src.stem+(f'_{index}' if index else '')+'.mp3')
            try:
                with dest.open('xb') as out:
                    reserved=True
                    with temp.open('rb') as source:
                        while chunk:=source.read(1024*1024):out.write(chunk)
                    out.flush();os.fsync(out.fileno())
                return dest
            except FileExistsError:continue
        raise RuntimeError('No free output filename')
    except BaseException:
        if reserved and dest is not None:dest.unlink(missing_ok=True)
        raise
    finally:temp.unlink(missing_ok=True)

def plan(files,job,ffprobe):
    mode=str(job.get('split_mode','MINUTES')).upper()
    minutes=int(job.get('target_minutes',180));tracks=int(job.get('target_tracks',40))
    if mode not in ('MINUTES','TRACKS','HYBRID') or not (1<=minutes<=10080) or not (1<=tracks<=10000):raise ValueError('Invalid block plan')
    groups=catalog([(p,duration(p,ffprobe)) for p in files],random.Random())
    return [(block.index,smart_shuffle(block.items,job.get('hardcore') is True)) for block in balanced_blocks(groups,mode,minutes,tracks)]

def process(job,ffmpeg,ffprobe):
    files,root,profile,bitrate=validate(job)
    blocks=plan(files,job,ffprobe) if job.get('block_mode') is True else [(None,files)]
    successful=0;failed=0
    metadata_path=job.get('metadata_profile_path')
    meta=metadata_profile(job,metadata_path)
    cover_rotation=None
    if job.get('rotate_covers') is True:
        folder=job.get('cover_dir')
        if not folder or not Path(folder).is_dir():raise ValueError('Select a valid cover directory')
        cover_rotation=CoverRotation(folder)
        if not cover_rotation._covers:raise ValueError('No supported covers in selected folder')
    completed_blocks=[]
    for index,members in blocks:
        directory=root
        if index is not None:
            for suffix in range(10000):
                directory=root/(f'BLOCK_{index:03d}'+(f'_{suffix}' if suffix else ''))
                try:directory.mkdir(exist_ok=False);break
                except FileExistsError:continue
            else:raise RuntimeError('No unique block directory')
        created=[]
        for member in members:
            src=member.path if index is not None else member
            try:
                file=render(src,directory,profile,bitrate,ffmpeg,meta,cover_rotation.next() if cover_rotation else None)
                created.append(file);successful+=1
                emit(done=successful+failed,total=len(files),message=f'OK: {src.name} -> {file.name}',block=index)
            except Exception as error:
                failed+=1;emit(done=successful+failed,total=len(files),message=f'ERROR {src.name}: {error}',block=index)
        if job.get('export_m3u') and created:
            try:emit(message='M3U: '+str(export_m3u(directory,created)),block=index)
            except Exception as error:failed+=1;emit(message='M3U ERROR: '+str(error),block=index)
        if index is not None and created:
            completed_blocks.append(directory)
    if job.get('export_stream_ready') is True:
        if job.get('block_mode') is not True:raise ValueError('STREAM_READY requires Block Mode')
        if failed or successful!=len(files):
            emit(message='STREAM_READY skipped: incomplete render; previous export preserved')
            return 2
        output,previous=export_stream_ready(root,completed_blocks)
        emit(message='STREAM_READY: '+str(output),previous=str(previous) if previous else None)
    return 0 if failed==0 and successful==len(files) else 2

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input-json',default='-');parser.add_argument('--ffmpeg',default='ffmpeg');parser.add_argument('--ffprobe',default='ffprobe');args=parser.parse_args()
    try:
        data=json.load(sys.stdin) if args.input_json=='-' else json.loads(Path(args.input_json).read_text(encoding='utf-8'))
        return process(data,args.ffmpeg,args.ffprobe)
    except Exception as error:emit(message='FATAL: '+str(error));return 1
if __name__=='__main__':sys.exit(main())
