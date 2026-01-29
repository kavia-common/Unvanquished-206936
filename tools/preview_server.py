#!/usr/bin/env python3
"""
Lightweight preview/readiness HTTP server.

This repository is primarily a CMake/C++ project (Unvanquished gamelogic) and does not
provide an HTTP service by default. The Kavia container preview expects the backend
container to listen on TCP port 3001; when nothing binds this port, the container is
marked as not ready.

This script starts a tiny dependency-free HTTP server that binds to HOST/PORT and
provides:
- GET /health  -> 200 OK (used for readiness checks)
- GET /        -> 200 OK + a short informational message

Environment variables:
- HOST (default: 0.0.0.0)
- PORT (default: 3001)

Run:
  python3 tools/preview_server.py
"""

from __future__ import annotations

import os
from http.server import BaseHTTPRequestHandler, HTTPServer


class _Handler(BaseHTTPRequestHandler):
    def _send_bytes(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, status: int, body: str, content_type: str) -> None:
        self._send_bytes(status, body.encode("utf-8"), content_type)

    def _send_html(self, status: int, html: str) -> None:
        self._send_text(status, html, "text/html; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802 (http.server naming convention)
        if self.path in ("/health", "/healthz", "/ready", "/readyz"):
            self._send_text(200, "ok\n", "text/plain; charset=utf-8")
            return

        # The preview environment often links directly to /docs for backend services.
        # This repository isn't a web API, so we serve a simple HTML landing page
        # at both / and /docs to avoid a blank preview.
        if self.path in ("/", "/docs"):
            self._send_html(
                200,
                """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Unvanquished Preview</title>
    <style>
      body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 2rem; line-height: 1.4; }
      code { background: #f3f3f3; padding: 0.1rem 0.25rem; border-radius: 4px; }
      .card { max-width: 52rem; border: 1px solid #ddd; border-radius: 10px; padding: 1.25rem 1.5rem; }
      h1 { margin-top: 0; }
      ul { margin-bottom: 0; }
    </style>
  </head>
  <body>
    <div class="card">
      <h1>Unvanquished container is running</h1>
      <p>
        This workspace is a <strong>CMake/C++ gamelogic</strong> project and does not expose an HTTP API.
        This page exists so the container preview (port <code>3001</code>) is not blank.
      </p>
      <p>Available endpoints:</p>
      <ul>
        <li><code>GET /health</code> &rarr; readiness probe (<code>200 ok</code>)</li>
      </ul>
    </div>
  </body>
</html>
""",
            )
            return

        self._send_text(404, "not found\n", "text/plain; charset=utf-8")

    def log_message(self, fmt: str, *args) -> None:
        # Keep logs minimal/noisy output down in preview environments.
        return


def main() -> None:
    host = os.environ.get("HOST", "0.0.0.0")
    port_str = os.environ.get("PORT", "3001")
    try:
        port = int(port_str)
    except ValueError:
        raise SystemExit(f"Invalid PORT value: {port_str!r} (expected integer)")

    httpd = HTTPServer((host, port), _Handler)
    # Intentionally prints one line so logs show what is listening.
    print(f"Preview health server listening on http://{host}:{port}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
