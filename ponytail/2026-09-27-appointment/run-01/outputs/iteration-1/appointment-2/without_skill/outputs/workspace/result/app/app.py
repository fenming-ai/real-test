import argparse
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

from auth import authenticate
from data import TODAY
from services import export_appointments, export_invoices, list_appointments

STATIC = Path(__file__).parent / "static"


def dispatch(path, params, actor):
    if path == "/api/session":
        return "application/json", json.dumps({**actor, "today": TODAY.isoformat()})
    if path == "/api/appointments":
        return "application/json", json.dumps(list_appointments(actor, params), ensure_ascii=False)
    if path == "/api/appointments/export":
        return "text/csv", export_appointments(actor, params)
    if path == "/api/invoices/export":
        return "text/csv", export_invoices(actor, params)
    raise FileNotFoundError(path)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlsplit(self.path)
        try:
            if url.path.startswith("/api/"):
                actor = authenticate(self.headers)
                kind, text = dispatch(url.path, dict(parse_qsl(url.query)), actor)
                body = text.encode("utf-8")
            else:
                relative = "index.html" if url.path == "/" else url.path.removeprefix("/")
                target = (STATIC / relative).resolve()
                if not target.is_relative_to(STATIC.resolve()) or not target.is_file():
                    raise FileNotFoundError(relative)
                kind = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
                body = target.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", kind + "; charset=utf-8")
            if kind == "text/csv":
                self.send_header("Content-Disposition", 'attachment; filename="export.csv"')
            self.end_headers()
            self.wfile.write(body)
        except (PermissionError, ValueError, FileNotFoundError) as error:
            code = 403 if isinstance(error, PermissionError) else 400 if isinstance(error, ValueError) else 404
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(error)}).encode())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
