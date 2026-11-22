"""666 AutoDJ Studio isolated Python worker. R01: MP3 conversion only, not legacy full parity."""
import argparse,json,os,subprocess,sys,tempfile
from pathlib import Path
PROFILES={"stream":["-af","loudnorm=I=-14:TP=-1.5:LRA=11"],"dj":["-af","loudnorm=I=-10:TP=-1.0:LRA=9"],"custom":[]}
EXT={".mp3",".wav",".flac",".ogg",".m4a",".aac",".aiff",".wma"}
def destination(src,root):
 for n in range(100000):
  p=root/(src.stem+(f"_{n}" if n else "")+".mp3")
  if not p.exists():return p
 raise RuntimeError("Output collision limit")
def validate(data):
 files=[Path(p).resolve() for p in data.get("files",[])]
 root=Path(data.get("output","")).resolve()
 if not files or not root.is_dir() or any(not f.is_file() or f.suffix.lower() not in EXT for f in files):raise ValueError("Invalid files or output folder")
 profile=data.get("profile","stream")
 if profile not in PROFILES:raise ValueError("Invalid profile")
 bitrate=int(data.get("bitrate",256))
 if bitrate not in (256,320):raise ValueError("Invalid bitrate")
 return files,root,profile,bitrate
def emit(**kw):print(json.dumps(kw,ensure_ascii=False),flush=True)
def process(data,ffmpeg):
 files,root,profile,bitrate=validate(data);ok=0
 for i,src in enumerate(files,1):
  dst=destination(src,root)
  fd,name=tempfile.mkstemp(prefix="autodj_",suffix=".mp3",dir=root);os.close(fd);tmp=Path(name)
  try:
   args=[ffmpeg,"-hide_banner","-nostdin","-loglevel","error","-y","-i",str(src),*PROFILES[profile],"-codec:a","libmp3lame","-b:a",str(bitrate)+"k",str(tmp)]
   r=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=7200)
   if r.returncode or tmp.stat().st_size==0:raise RuntimeError(r.stderr.decode(errors="replace")[-900:])
   tmp.replace(dst);ok+=1;emit(done=i,total=len(files),message="OK: "+src.name+" -> "+dst.name)
  except Exception as exc:emit(done=i,total=len(files),message="ERROR: "+src.name+": "+str(exc))
  finally:tmp.unlink(missing_ok=True)
 return 0 if ok==len(files) else 2
def main():
 parser=argparse.ArgumentParser();parser.add_argument("--input-json",default="-");parser.add_argument("--ffmpeg",default="ffmpeg");args=parser.parse_args()
 try:return process(json.load(sys.stdin) if args.input_json=="-" else json.loads(Path(args.input_json).read_text()),args.ffmpeg)
 except Exception as exc:emit(message="FATAL: "+str(exc));return 1
if __name__=="__main__":sys.exit(main())
