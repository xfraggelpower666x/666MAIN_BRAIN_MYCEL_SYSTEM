"""Projekt-lokaler Dependency Check ohne Aenderung am globalen Python."""
import argparse
import importlib.metadata as meta
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tkinter
import traceback
import time

ROOT=Path(__file__).resolve().parent
VENV=ROOT/'.venv'

def version_tuple(s):
    out=[]
    for x in s.split('.')[:3]:
        n=''.join(c for c in x if c.isdigit())
        out.append(int(n) if n else 0)
    return tuple((out+[0,0,0])[:3])

def require_package(name,minimum,maximum_major=None, module=None):
    try:
        v=meta.version(name)
        if version_tuple(v)<version_tuple(minimum) or (maximum_major and version_tuple(v)[0]>=maximum_major):
            return False, f'{name} {v}: UPDATE NOETIG (erwartet >= {minimum}, < {maximum_major or "unbegrenzt"})'
        # Native extension import check catches broken ABI installs
        __import__(module or name)
        return True, f'{name} {v}: OK'
    except Exception as e:
        return False, f'{name}: FEHLT / DEFEKT ({type(e).__name__}: {e})'

def check_packages(build=False):
    major,minor=sys.version_info[:2]
    pillow_min='13.0' if (major,minor)>=(3,15) else '10.0'
    pillow_max=14
    deps=[('mutagen','1.47',2,'mutagen'),('Pillow',pillow_min,pillow_max,'PIL.Image'),('tkinterdnd2','0.4.3',1,'tkinterdnd2')]
    if build: deps.append(('pyinstaller','6.21' if (major,minor)>=(3,15) else '6.0',7,'PyInstaller'))
    ok=True
    for args in deps:
        valid,msg=require_package(*args);print(msg,flush=True);ok &= valid
    try:
        import tkinter; root=tkinter.Tcl(); print('Tkinter: OK')
    except Exception as e: print(f'Tkinter: NICHT VERFUEGBAR ({e})');ok=False
    return ok

def tool_path(name):
    for p in (ROOT/(name+'.exe'),ROOT/'tools'/(name+'.exe')):
        if p.is_file():return str(p)
    return shutil.which(name)

def check_audio():
    for binary in ('ffmpeg','ffprobe'):
        path=tool_path(binary)
        if not path:
            print(binary+': FEHLT - WAV/MP3-Audiofunktionen nicht verfuegbar');continue
        try:
            r=subprocess.run([path,'-version'],capture_output=True,text=True,timeout=8)
            print(binary+(': OK - ' + r.stdout.splitlines()[0] if r.returncode==0 and r.stdout else ': FEHLER'))
        except Exception as e:print(binary+': FEHLER '+str(e))

def check_mp3_encoder():
    ff=tool_path('ffmpeg')
    if not ff: return False
    try:
        r=subprocess.run([ff,'-hide_banner','-encoders'],capture_output=True,text=True,timeout=12)
        ok=r.returncode==0 and 'libmp3lame' in r.stdout
        print('libmp3lame: '+('OK (integriert in FFmpeg)' if ok else 'FEHLT IN DIESEM FFMPEG-BUILD'))
        return ok
    except Exception as exc:
        print('libmp3lame: PRUEFFEHLLER '+str(exc));return False

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--build-check',action='store_true');parser.add_argument('--build',action='store_true');parser.add_argument('--launch',action='store_true');parser.add_argument('--install',action='store_true');args=parser.parse_args()
    print(f'Python: {sys.version.split()[0]} - {sys.executable}')
    if not ((3,11) <= sys.version_info[:2] <= (3,14) and sys.version_info.releaselevel == 'final'):
        print('PYTHON_VERSION_UNSUPPORTED: stabile Python-Version 3.11 bis 3.14 erforderlich; Alpha/Beta/RC werden blockiert.');return 2
    if args.install:
        req='requirements-build.txt' if (args.build or args.build_check) else 'requirements.txt'
        print('Installiere nur in gewaehlter Projektumgebung: '+sys.prefix)
        cmd=[sys.executable,'-m','pip','install','--upgrade','-r',str(ROOT/req)]
        return subprocess.call(cmd)
    ok=check_packages(args.build or args.build_check)
    check_audio()
    encoder_ok=check_mp3_encoder()
    if not encoder_ok: print('HINWEIS: MP3-Konvertierung benötigt einen FFmpeg-Build mit libmp3lame.')
    if not ok:
        print('DEPENDENCIES_INVALID');return 3
    if args.launch:
        start=time.monotonic()
        print('[GUI] Starte MP3_Manager.pyw ...', flush=True)
        result=subprocess.run([sys.executable,str(ROOT/'MP3_Manager.pyw')],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace')
        if result.stdout: print(result.stdout,flush=True)
        duration=time.monotonic()-start
        print(f'[GUI] Ende nach {duration:.1f} Sekunden, Rueckgabecode {result.returncode}',flush=True)
        if duration<5: print('[DIAGNOSE] Sehr kurzer GUI-Lauf: Details/Traceback oben pruefen.',flush=True)
        return result.returncode
    if args.build:
        # Ein einziger portabler Ordner, nicht eine temporaer extrahierende Onefile-EXE.
        app_name='L.Y.V.R.A._MP3_MANAGER'
        dist=ROOT/'dist'
        portable=dist/app_name
        cmd=[sys.executable,'-m','PyInstaller','--noconfirm','--clean',
             '--onedir','--contents-directory','_internal','--windowed',
             '--distpath',str(dist),'--workpath',str(ROOT/'build'),
             '--specpath',str(ROOT),
             '--icon',str(ROOT/'assets'/'app.ico'),
             '--add-data',str(ROOT/'assets')+os.pathsep+'assets',
             '--add-data',str(ROOT/'BEDIENUNGSANLEITUNG_DE.md')+os.pathsep+'.',
             '--add-data',str(ROOT/'MANUAL_EN.md')+os.pathsep+'.',
             '--collect-all','tkinterdnd2',
             '--name',app_name,str(ROOT/'MP3_Manager.pyw')]
        result=subprocess.call(cmd,cwd=str(ROOT))
        if result:return result
        exe=portable/(app_name+'.exe')
        if not exe.is_file():
            print('BUILD_INVALID: EXE fehlt im portablen Ordner');return 7
        # Alle Arbeitsdateien im selben verschiebbaren Root-Ordner halten.
        shutil.copytree(ROOT/'assets',portable/'assets',dirs_exist_ok=True)
        for doc in ('BEDIENUNGSANLEITUNG_DE.md','MANUAL_EN.md','README.txt',
                    'REPARATUR_AUDIO_TOOLS.bat', 'PORTABLE_VERIFY.bat','PORTABLE_VERIFY.ps1'):
            shutil.copy2(ROOT/doc,portable/doc)
        optional_audio_apps=(
            (ROOT.parent/'Suno-Song-Remaster-main'/'release'/'win-unpacked',
             portable/'external-tools'/'Suno-Song-Remaster-main'),
            (ROOT.parent/'Restoration-Lab-main'/'dist'/'Restoration Lab',
             portable/'external-tools'/'Restoration-Lab-main'),
            (ROOT.parent/'SunoCleanser-0.2.1',
             portable/'external-tools'/'SunoCleanser-0.2.1'),
        )
        for source,destination in optional_audio_apps:
            if source.is_dir():
                shutil.copytree(
                    source,
                    destination,
                    dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('__pycache__','.pytest_cache','.venv','venv'),
                )
                print('OPTIONAL_AUDIO_LAB_BUNDLED:',destination.name)
        mp3gain_project=ROOT.parent/'mp3gain-win-gui-1_3_4-src'
        mp3gain_gui=mp3gain_project/'MP3GainGUI.exe'
        mp3gain_runtime=mp3gain_project/'electron-bridge'/'release'/'win-unpacked'
        mp3gain_destination=portable/'external-tools'/'mp3gain-win-gui-1_3_4-src'
        required_bridge_files=(
            mp3gain_runtime/'mp3gain.exe',
            mp3gain_runtime/'resources'/'app.asar',
            mp3gain_runtime/'resources'/'engine'/'mp3gain-worker.js',
        )
        if mp3gain_gui.is_file() and mp3gain_runtime.is_dir() and all(
            path.is_file() for path in required_bridge_files
        ):
            shutil.copytree(mp3gain_runtime,mp3gain_destination,dirs_exist_ok=True)
            shutil.copy2(mp3gain_gui,mp3gain_destination/'MP3GainGUI.exe')
            print('OPTIONAL_AUDIO_LAB_BUNDLED: mp3gain-win-gui-1_3_4-src')
        else:
            print('OPTIONAL_AUDIO_LAB_NOT_BUNDLED: MP3Gain GUI and complete bridge build required')

        sunscreen_project=ROOT.parent/'sunscreen-main'
        sunscreen_binary=next((candidate for candidate in (
            sunscreen_project/'target'/'release'/'sunscreen.exe',
            sunscreen_project/'target'/'release'/'sunscreen',
            sunscreen_project/'sunscreen.exe',
            sunscreen_project/'sunscreen',
        ) if candidate.is_file()),None)
        if sunscreen_binary:
            sunscreen_destination=(
                portable/'external-tools'/'sunscreen-main'/'target'/'release'/
                sunscreen_binary.name
            )
            sunscreen_destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(sunscreen_binary,sunscreen_destination)
            print('OPTIONAL_AUDIO_LAB_BUNDLED: sunscreen-main')
        else:
            print('OPTIONAL_AUDIO_LAB_NOT_BUNDLED: Sunscreen release binary missing')
        wav2mp3_project=ROOT.parent/'Wav2mp3-master'
        wav2mp3_binary=next((candidate for candidate in (
            wav2mp3_project/'wav2mp3.exe',
            wav2mp3_project/'build'/'windows'/'wav2mp3.exe',
            wav2mp3_project/'build'/'windows'/'wav2mp3',
        ) if candidate.is_file()),None)
        if wav2mp3_binary:
            wav2mp3_destination=(
                portable/'external-tools'/'Wav2mp3-master'/'wav2mp3.exe'
            )
            wav2mp3_destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(wav2mp3_binary,wav2mp3_destination)
            print('OPTIONAL_AUDIO_LAB_BUNDLED: Wav2mp3-master')
        else:
            print('OPTIONAL_AUDIO_LAB_NOT_BUNDLED: wav2mp3 Windows binary missing')
        tools_out=portable/'tools';tools_out.mkdir(parents=True,exist_ok=True)
        missing=[]
        for name in ('ffmpeg','ffprobe'):
            candidate=tool_path(name)
            if candidate and Path(candidate).is_file():
                shutil.copy2(candidate,tools_out/(name+'.exe'))
                print('PORTABLE_TOOL_BUNDLED:',name)
            else:
                missing.append(name)
                print('PORTABLE_TOOL_MISSING:',name)
        (portable/'PORTABLE_STATUS.txt').write_text(
            'Build: onedir\nAudio-Tools: '+('COMPLETE' if not missing else 'MISSING: '+', '.join(missing))+ '\n'
            'Copy this entire folder; never move only the EXE.\n',encoding='utf-8')
        if missing:
            print('PORTABLE_INCOMPLETE: missing audio tools. Installiere sie im Quellprojekt und baue neu,')
            print('oder lege sie in dist/'+app_name+'/tools/ ab. Keine irrefuehrende COMPLETE-Meldung.')
            return 8
        # Externe vollständige Kontrolle des finalen Ordners (kein falscher PASS bei kaputtem Bundle).
        verification=subprocess.run([sys.executable,str(ROOT/'VERIFY_PORTABLE_FOLDER.py'),str(portable)],cwd=str(ROOT))
        if verification.returncode:
            print('PORTABLE_FOLDER_INVALID: Verzeichnispruefung fehlgeschlagen')
            return 9
        print('PORTABLE_FOLDER_READY:',portable)
        return 0
    return 0
if __name__=='__main__':sys.exit(main())
