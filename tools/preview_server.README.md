# Preview server (port 3001 readiness)

The Unvanquished repository in this workspace is a **CMake/C++ gamelogic** project and does not expose an HTTP service by default.

However, the container preview environment expects the backend container to become ready by **binding TCP port 3001**.

## Start

```sh
python3 tools/preview_server.py
```

## Configuration

Uses standard environment variables:

- `HOST` (default `0.0.0.0`)
- `PORT` (default `3001`)

## Endpoints

- `GET /health` → `200 ok`
- `GET /` → informational message
