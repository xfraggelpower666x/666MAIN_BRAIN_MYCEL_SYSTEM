"""R02.9: lesende Host-Abnahme, keine Veröffentlichung oder Freigabe."""
import argparse, hashlib, json, os, re, subprocess, sys, urllib.request
from pathlib import Path
REPO='xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM'
HEX=re.compile(r'[0-9a-f]{40}\Z')

def verify_bytes(data, sha, sha256):
    if hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()!=sha or hashlib.sha256(data).hexdigest()!=sha256:
        raise ValueError('Binärintegrität verletzt')
    return {'sha':sha,'sha256':sha256,'bytes':len(data)}

def provider_probe(sha, sha256, opener=urllib.request.urlopen):
    if not HEX.fullmatch(sha) or not re.fullmatch('[0-9a-f]{64}',sha256):
        raise ValueError('Ungültiger Hash')
    # Öffentlicher GitHub-Blob, keine Zugangsdaten oder fremden URLs.
    req=urllib.request.Request(f'https://api.github.com/repos/{REPO}/git/blobs/{sha}',headers={'Accept':'application/vnd.github.raw+json','User-Agent':'LYVRA-R029'})
    with opener(req,timeout=20) as response:
        data=response.read(1024*1024+1)
    if len(data)>1024*1024: raise ValueError('Probe zu groß')
    return verify_bytes(data,sha,sha256)

def execute(args, cwd, timeout=180):
    try:
        p=subprocess.run(args,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
        return {'status':'PASS' if p.returncode==0 else 'FAIL','exit':p.returncode,'output_sha256':hashlib.sha256(p.stdout).hexdigest()}
    except (OSError,subprocess.TimeoutExpired) as exc:
        return {'status':'BLOCKED','reason':type(exc).__name__}

def acceptance(root, windows_build=False):
    root=Path(root).resolve()
    result={}
    result['dependencies']=execute([sys.executable,'-c','import mutagen,numpy,scipy,soundfile,pywt,pyloudnorm,sounddevice'],root)
    result['adapter_contracts']=execute(['node','--test',*map(str,sorted((root/'tests').glob('*.test.cjs')))],root) if list((root/'tests').glob('*.test.cjs')) else {'status':'BLOCKED','reason':'Tests fehlen'}
    result['bulk']=execute([sys.executable,'-m','unittest','discover','-s',str(root/'tools/bulk'),'-p','test_*.py'],root)
    result['windows_build']={'status':'PENDING','reason':'Windows und explizite Build-Freigabe erforderlich'}
    if windows_build and os.name=='nt':
        result['windows_build']=execute(['cmd.exe','/d','/c','npx --no-install electron-builder --win --dir --publish never'],root,900)
    # Paket-Build ist keine GUI-Abnahme und keine DSP-End-to-End-Abnahme.
    result['windows_gui']={'status':'PENDING'}
    result['restoration_dsp']={'status':'PENDING'}
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--windows-build',action='store_true');p.add_argument('--probe-sha');p.add_argument('--probe-sha256');a=p.parse_args()
    r=acceptance(a.root,a.windows_build)
    if a.probe_sha or a.probe_sha256:
        try:r['provider_binary']={'status':'PASS',**provider_probe(a.probe_sha or '',a.probe_sha256 or '')}
        except Exception as e:r['provider_binary']={'status':'BLOCKED','reason':type(e).__name__}
    else:r['provider_binary']={'status':'PENDING'}
    print(json.dumps(r,indent=2));sys.exit(0 if all(v['status']=='PASS' for v in r.values()) else 2)
