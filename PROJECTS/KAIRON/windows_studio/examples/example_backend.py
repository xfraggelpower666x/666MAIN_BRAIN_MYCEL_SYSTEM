"""Optional example only. Does not overwrite the host project's original entrypoint."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            body=b'{"ok":true}'; content='application/json'
        elif self.path == '/':
            body=b'<html><body style="background:#101019;color:#ff68bd;font:24px Segoe UI;padding:6rem"><h1>Python + Electron</h1><p>Example backend is running.</p></body></html>'
            content='text/html; charset=utf-8'
        else:
            self.send_error(404);return
        self.send_response(200);self.send_header('Content-Type',content);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
if __name__=='__main__':
    ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
