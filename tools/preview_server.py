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
    def _send_text(self, status: int, body: str) -> None:
        body_bytes = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body_bytes)))
        self.end_headers()
        self.wfile.write(body_bytes)

    def do_GET(self) -> None:  # noqa: N802 (http.server naming convention)
        if self.path in ("/health", "/healthz", "/ready", "/readyz"):
            self._send_text(200, "ok\n")
            return

        if self.path == "/":
            self._send_text(
                200,
                "Unvanquished container preview server is running.\n"
                "This repository is a CMake/C++ gamelogic module; no HTTP API is exposed.\n"
                "Use /health for readiness checks.\n",
            )
            return

        self._send_text(404, "not found\n")

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
