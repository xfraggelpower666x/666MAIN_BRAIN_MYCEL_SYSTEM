#!/usr/bin/env python3
"""Read-only toolchain and project diagnosis. Python 3.9+ standard library."""
import argparse, json, os, pathlib, platform, shutil, subprocess, sys, datetime

def probe(binary, args=None):
    path = shutil.which(binary)
    if not path:
        return {"found": False, "path": None, "version": None}
    try:
        p = subprocess.run([path] + (args or ['--version']), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=8)
        return {"found": True, "path": path, "version": p.stdout.strip()[:350], "exit_code": p.returncode}
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"found": True, "path": path, "error": str(e)}

def diagnose(root):
    cfg = json.loads((root / 'project.config.json').read_text(encoding='utf-8'))
    project = (root / cfg['project_directory']).resolve()
    entry = (project / cfg['python_entry']).resolve()
    if not entry.is_relative_to(project):
        raise ValueError('python_entry escapes project directory')
    req = (project / cfg['requirements_file']).resolve()
    if not req.is_relative_to(project):
        raise ValueError('requirements_file escapes project directory')
    return {
        'timestamp_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'platform': platform.platform(),
        'config': {'project': str(project), 'entry': str(entry), 'entry_exists': entry.is_file(), 'requirements_exists': req.is_file()},
        'toolchain': {name: probe(cmd, args) for name, cmd, args in [
            ('python', 'python', ['--version']), ('python_launcher', 'py', ['--version']),
            ('node', 'node', ['--version']), ('npm', 'npm', ['--version']),
            ('winget', 'winget', ['--version']), ('git', 'git', ['--version']),
            ('github_cli', 'gh', ['--version']), ('cmake', 'cmake', ['--version']),
            ('msbuild', 'msbuild', ['-version']), ('cl', 'cl', ['/Bv']),
            ('dotnet', 'dotnet', ['--version']), ('7zip', '7z', []),
            ('electron_global', 'electron', ['--version'])]}
    }

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(pathlib.Path(__file__).resolve().parents[1]));p.add_argument('--output');a=p.parse_args()
    result=diagnose(pathlib.Path(a.root).resolve())
    contents=json.dumps(result,indent=2,ensure_ascii=False)
    print(contents)
    if a.output:
        target=pathlib.Path(a.output);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(contents+'\n',encoding='utf-8')

if __name__=='__main__':main()
