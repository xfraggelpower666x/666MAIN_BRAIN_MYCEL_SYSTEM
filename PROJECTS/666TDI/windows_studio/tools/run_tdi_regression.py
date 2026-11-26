from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parents[1]
from verify_native_binding import verify
print(verify(root))
for cwd, args in [(root,["-m","unittest","discover","-s","tests","-v"]),(root.parent/"source",["-m","unittest","discover","-s","tests","-v"])]:
    if not cwd.is_dir():raise SystemExit("NATIVE_SOURCE_MISSING")
    subprocess.run([sys.executable,*args],cwd=cwd,check=True)
subprocess.run(["node","--test",str(root/"tests/settings_store.test.cjs")],cwd=root,check=True)
