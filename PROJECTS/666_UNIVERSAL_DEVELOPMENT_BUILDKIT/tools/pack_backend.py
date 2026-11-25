#!/usr/bin/env python3
"""Build bundled Windows backend with PyInstaller, fail closed on config escape."""
import json, pathlib, subprocess, sys
root=pathlib.Path(__file__).resolve().parents[1]
cfg=json.loads((root/'project.config.json').read_text(encoding='utf-8'))
project=(root/cfg['project_directory']).resolve()
entry=(project/cfg['python_entry']).resolve()
if not entry.is_relative_to(project) or not entry.is_file():raise SystemExit('INVALID ENTRY')
out=root/'dist-backend';out.mkdir(exist_ok=True)
cmd=[sys.executable,'-m','PyInstaller','--noconfirm','--clean','--onedir','--name','backend','--distpath',str(out),'--workpath',str(root/'.pyinstaller-build'),'--specpath',str(root/'.pyinstaller-spec'),str(entry)]
print('Building backend:',entry,flush=True)
subprocess.run(cmd,cwd=str(project),check=True)
exe=out/'backend'/'backend.exe'
if not exe.is_file():raise SystemExit('BUILD_BLOCKED: packaged backend.exe missing')
print('BACKEND_ARTIFACT:',exe)
