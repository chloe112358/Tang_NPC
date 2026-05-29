import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

from dotenv import load_dotenv

from tang_dialogue_test import FALLBACK_REPLY, generate_npc_reply_for_branch


load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent
FINAL_HTML = ROOT_DIR / "final.html"
STATIC_DIR = ROOT_DIR / "static"
MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", "500"))

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}


class DialogueHandler(BaseHTTPRequestHandler):
    server_version = "TangDialogueHTTP/1.0"

    def do_OPTIONS(self):
        self._send_headers(204, "application/json")

    def do_GET(self):
        path = unquote(self.path.split("?", 1)[0])
        if path in ("/", "/final.html"):
            self._send_file(FINAL_HTML, "text/html; charset=utf-8")
            return

        if path.startswith("/static/"):
            self._send_static_file(path)
            return

        if path == "/api/dialogue":
            self._send_json(200, {
                "status": "ok",
                "message": "Use POST /api/dialogue from the game page.",
            })
            return

        if path.startswith("/api/"):
            self._send_json(404, {"error": "not_found"})
            return

        self._send_file(FINAL_HTML, "text/html; charset=utf-8")

    def do_POST(self):
        path = unquote(self.path.split("?", 1)[0])
        if path != "/api/dialogue":
            self._send_json(404, {"error": "not_found"})
            return

        try:
            payload = self._read_json_body()
            branch = str(payload.get("branch", "")).strip()
            turn = int(payload.get("turn", 0))
            user_input = str(
                payload.get("user_input")
                or payload.get("userInput")
                or ""
            ).strip()

            if not branch or turn not in (1, 2, 3):
                self._send_json(400, {"error": "invalid_branch_or_turn"})
                return

            if not user_input:
                self._send_json(400, {"error": "empty_user_input"})
                return

            if len(user_input) > MAX_INPUT_LENGTH:
                self._send_json(400, {"error": "user_input_too_long"})
                return

            npc_response = generate_npc_reply_for_branch(branch, turn, user_input)
            self._send_json(200, {
                "npc_response": npc_response,
                "is_fallback": False,
            })
        except Exception as exc:
            self.log_error("dialogue fallback: %s: %s", type(exc).__name__, exc)
            self._send_json(200, {
                "npc_response": FALLBACK_REPLY,
                "is_fallback": True,
            })

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw_body = self.rfile.read(length)
        return json.loads(raw_body.decode("utf-8"))

    def _send_file(self, path, content_type, extra_headers=None):
        if not path.exists():
            self._send_json(404, {"error": "file_not_found"})
            return

        body = path.read_bytes()
        self._send_headers(200, content_type, len(body), extra_headers)
        self.wfile.write(body)

    def _send_static_file(self, request_path):
        relative_path = request_path.lstrip("/").replace("/", os.sep)
        requested_path = (ROOT_DIR / relative_path).resolve()
        static_root = STATIC_DIR.resolve()

        if not _is_relative_to(requested_path, static_root):
            self._send_json(404, {"error": "not_found"})
            return

        content_type = CONTENT_TYPES.get(
            requested_path.suffix.lower(),
            "application/octet-stream",
        )
        self._send_file(
            requested_path,
            content_type,
            {"Cache-Control": "public, max-age=31536000, immutable"},
        )

    def _send_json(self, status_code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send_headers(status_code, "application/json; charset=utf-8", len(body))
        self.wfile.write(body)

    def _send_headers(
        self,
        status_code,
        content_type,
        content_length=0,
        extra_headers=None,
    ):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        if content_length:
            self.send_header("Content-Length", str(content_length))
        for header, value in (extra_headers or {}).items():
            self.send_header(header, value)
        self.end_headers()


def main():
    port = int(os.getenv("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), DialogueHandler)
    print(f"Serving final.html at http://localhost:{port}")
    server.serve_forever()


def _is_relative_to(path, parent):
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    main()
