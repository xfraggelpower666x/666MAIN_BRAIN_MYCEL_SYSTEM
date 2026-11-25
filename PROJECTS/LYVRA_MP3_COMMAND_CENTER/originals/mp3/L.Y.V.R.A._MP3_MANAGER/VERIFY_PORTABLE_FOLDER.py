"""Prüft einen erstellten Windows-Portable-Ordner; kein Download, keine Mutation."""
import argparse
import json
import os
import re
from pathlib import Path
import subprocess
import sys

from restoration_overlay import SOURCES

APP = 'L.Y.V.R.A._MP3_MANAGER'

REQUIRED_FILES = (
    APP+'.exe', 'assets/app.ico', 'assets/banner.png', 'assets/logo.png',
    'tools/ffmpeg.exe', 'tools/ffprobe.exe', 'BEDIENUNGSANLEITUNG_DE.md', 'MANUAL_EN.md',
    'L.Y.V.R.A._MP3_MANAGER.bat', 'PORTABLE_VERIFY.ps1',
    'HOST_ABNAHME_WINDOWS.bat', 'HOST_ABNAHME_WINDOWS.ps1',
    *(f'_internal/restoration_lab/{name}' for name in SOURCES),
    '_internal/restoration_lab/assets/RestorationLab.png',
)
ENCODER_ROW = re.compile(r'(?m)^\s*[A-Z.]{6}\s+libmp3lame\s')


def verify(folder, runner=subprocess.run, platform=None):
    folder=Path(folder).resolve()
    errors=[]
    info={'schema':'LYVRA_PORTABLE_FOLDER_VERIFY_V1','folder':str(folder), 'checks':{},'errors':errors}
    is_windows=(platform or sys.platform)=='win32'
    for rel in REQUIRED_FILES:
        target=folder/rel
        ok=target.is_file() and target.stat().st_size>0
        info['checks'][rel]='PASS' if ok else 'MISSING'
        if not ok:errors.append('Fehlend oder leer: '+rel)
    for rel in (APP+'.exe', 'tools/ffmpeg.exe', 'tools/ffprobe.exe'):
        binary = folder/rel
        if binary.is_file():
            with binary.open('rb') as fd: magic=fd.read(2)
            if magic!=b'MZ':errors.append('Windows-Dateisignatur fehlt: '+rel)
    if is_windows:
        # Nur aus dem eigenen Tools-Verzeichnis + Windows-Systempfaden auflösen,
        # so dass PATH-FFmpeg des Entwickler-PCs einen kaputten Portable-Ordner nicht kaschiert.
        windows_root=os.environ.get('SystemRoot',r'C:\Windows')
        base_env={**os.environ,'PATH':str(folder/'tools')+os.pathsep+str(Path(windows_root)/'System32')+os.pathsep+windows_root}
        for name,extra in [('ffmpeg',['-hide_banner','-encoders']),('ffprobe',['-version'])]:
            binary=folder/'tools'/(name+'.exe')
            if not binary.is_file():continue
            try:
                out=runner([str(binary),*extra],capture_output=True,text=True,timeout=20,cwd=str(folder),env=base_env,
                           creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                valid=out.returncode==0 and bool(
                    ENCODER_ROW.search(out.stdout) if name=='ffmpeg' else out.stdout.startswith('ffprobe version '))
                if valid and name=='ffmpeg':
                    smoke=runner([str(binary),'-nostdin','-v','error','-f','lavfi','-i',
                                  'anullsrc=r=44100:cl=stereo','-t','0.1','-c:a','libmp3lame','-f','null','-'],
                                 capture_output=True,text=True,timeout=20,cwd=str(folder),env=base_env,
                                 creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                    valid=smoke.returncode==0
                info['checks'][name+'_runtime']='PASS' if valid else 'FAIL'
                if not valid:errors.append(name+'-Ausführung oder libmp3lame fehlgeschlagen')
            except (OSError,subprocess.TimeoutExpired) as e:
                info['checks'][name+'_runtime']='FAIL'
                errors.append(name+': '+str(e))
    else:
        info['checks']['windows_runtime']='NOT_TESTED_NON_WINDOWS_HOST'
    info['status']='PASS' if not errors and is_windows else ('STATIC_PASS_WINDOWS_PENDING' if not errors else 'FAIL')
    return info

def main():
    cli=argparse.ArgumentParser();cli.add_argument('folder',nargs='?',default=str(Path(__file__).resolve().parent/'dist'/APP))
    cli.add_argument('--json',dest='json_path');args=cli.parse_args()
    report=verify(args.folder)
    for key,value in report['checks'].items():print(f'{key}: {value}')
    for issue in report['errors']:print('ERROR:',issue)
    print('PORTABLE_FOLDER_STATUS:',report['status'])
    if args.json_path:Path(args.json_path).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return 0 if report['status'] in ('PASS','STATIC_PASS_WINDOWS_PENDING') else 1
if __name__=='__main__':sys.exit(main())
