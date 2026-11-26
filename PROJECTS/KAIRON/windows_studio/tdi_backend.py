"""666TDI native daemon adapter; no second musical authority."""
import os, sys
from pathlib import Path
from http.server import ThreadingHTTPServer
ROOT = Path(sys._MEIPASS).resolve() if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
SOURCE = ROOT / "native_source" if getattr(sys, "frozen", False) else ROOT.parent / "source"
if not SOURCE.is_dir():
    raise SystemExit("NATIVE_SOURCE_MISSING: place windows_studio inside PROJECTS/KAIRON")
from tools.verify_native_binding import verify
BINDING_ROOT = ROOT / "native_bundle" / "windows_studio" if getattr(sys, "frozen", False) else ROOT
BINDING_STATUS = verify(BINDING_ROOT)
sys.path.insert(0, str(SOURCE))
from engine import daemon_cli, portable
portable.ROOT = SOURCE
daemon_cli.STATIC = SOURCE / "engine" / "daemon_static" / "index.html"
# Keep runtime data out of source tree / temporary bundled resources.
portable.DATA = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "666TDI" / "runtime"
class Handler(daemon_cli.Handler):
    def do_GET(self):
        if self.path == "/health":
            if not self._safe_host():
                return self._json(403, {"error": "HOST_NOT_ALLOWED"})
            return self._json(200, {"system_id": "666TDI-001", "status": "READY", "startup_token": os.environ.get("TDI_STARTUP_TOKEN", "")})
        if self.path == "/api/native-binding":
            if not self._safe_host():
                return self._json(403, {"error": "HOST_NOT_ALLOWED"})
            return self._json(200, BINDING_STATUS)
        return super().do_GET()
if __name__ == "__main__":
    with ThreadingHTTPServer(("127.0.0.1", 8766), Handler) as server:
        server.serve_forever()
