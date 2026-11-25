"""Adapter zur unveränderten Windows Restoration Engine; exklusive Ausgabe."""
import sys,json,pathlib,tempfile,shutil,os
from dataclasses import replace
def emit(**data): print(json.dumps(data),flush=True)
def main():
    req=json.load(sys.stdin)
    sys.path.insert(0,req['engine'])
    from audio_input import read_audio
    from realtime import RealtimeRestoration,export_audio
    from reference_engine import Controls
    source,sr=read_audio(req['source'])
    engine=RealtimeRestoration(source,sr,drift=False)
    target=pathlib.Path(req['destination'])
    with tempfile.TemporaryDirectory(dir=target.parent) as d:
        stage=pathlib.Path(d)/'render.wav'
        export_audio(engine,stage,replace(Controls(),mode=req['mode']),lambda x:emit(type='progress',fraction=float(x)))
        created=False
        try:
            with target.open('xb') as out:
                created=True
                with stage.open('rb') as inp: shutil.copyfileobj(inp,out)
                out.flush();os.fsync(out.fileno())
        except BaseException:
            if created:target.unlink(missing_ok=True)
            raise
    emit(type='result',destination=str(target))
if __name__=='__main__':
    try:main()
    except Exception as e:emit(type='error',message=str(e));sys.exit(1)
