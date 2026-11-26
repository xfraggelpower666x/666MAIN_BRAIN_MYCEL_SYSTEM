#!/usr/bin/env python3
"""Build bundled Windows backend with PyInstaller; fail closed."""
import json, pathlib, subprocess, sys, os
root=pathlib.Path(__file__).resolve().parents[1]
cfg=json.loads((root/'project.config.json').read_text(encoding='utf-8'))
project=(root/cfg['project_directory']).resolve()
entry=(project/cfg['python_entry']).resolve()
if not project.is_relative_to(root) or not entry.is_relative_to(project) or not entry.is_file():raise SystemExit('INVALID ENTRY')
from verify_native_binding import verify
verify(root)
native=(root.parent/'source').resolve()
if not (native/'engine'/'daemon_cli.py').is_file():raise SystemExit('NATIVE_SOURCE_MISSING')
out=root/'dist-backend'
cmd=[sys.executable,'-m','PyInstaller','--noconfirm','--clean','--onedir','--name','backend','--distpath',str(out),'--workpath',str(root/'.pyinstaller-build'),'--specpath',str(root/'.pyinstaller-spec')]
def add(source,target):
    if not source.exists():raise SystemExit('BUNDLE_DEPENDENCY_MISSING:'+str(source))
    cmd.extend(['--add-data',str(source)+os.pathsep+target])
for folder in ('engine','registry'):
    add(native/folder,'native_source/'+folder)
cmd.extend(['--paths',str(native),'--collect-all','numpy','--collect-all','soundfile'])
for name in ('CURRENT_POINTER.json','native/musical_intelligence','windows_studio/NATIVE_BINDING.json','identity/CHARACTER.json','triggers/TRIGGER_REGISTRY.json','livecircle/CURRENT_STATE.json','rehydration/parity.py','plugin/release-binding.json'):
    source=root.parent/name
    target='native_bundle/'+(name if source.is_dir() else str(pathlib.PurePosixPath(name).parent))
    add(source,target)
cmd.append(str(entry))
subprocess.run(cmd,cwd=str(project),check=True)
exe=out/'backend'/'backend.exe'
if not exe.is_file():raise SystemExit('BUILD_BLOCKED: packaged backend.exe missing')
print('BACKEND_ARTIFACT:',exe)
