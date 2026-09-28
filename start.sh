#!/bin/sh
set -eu
project_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$project_dir"
[ -f .env ] || { echo 'Missing ignored .env runtime configuration' >&2; exit 2; }
set -a
. ./.env
set +a
: "${BACKEND_PORT:?BACKEND_PORT is required}"
: "${FRONTEND_PORT:?FRONTEND_PORT is required}"
[ "$BACKEND_PORT" != "$FRONTEND_PORT" ] || { echo 'API and UI ports must be distinct' >&2; exit 2; }
for assigned_port in "$BACKEND_PORT" "$FRONTEND_PORT"; do
  if lsof -nP -iTCP:"$assigned_port" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Port $assigned_port is already occupied" >&2
    exit 2
  fi
done
python_bin=
for candidate in "${PYTHON_BIN:-}" python3 /opt/homebrew/bin/python3 /usr/local/bin/python3; do
  [ -n "$candidate" ] || continue
  resolved=$(command -v "$candidate" 2>/dev/null || true)
  [ -n "$resolved" ] || continue
  if "$resolved" -c 'import hashlib,sys; raise SystemExit(0 if sys.version_info >= (3, 11) and hasattr(hashlib, "scrypt") else 1)' 2>/dev/null; then
    python_bin=$resolved
    break
  fi
done
[ -n "$python_bin" ] || { echo 'Python 3.11 or newer with hashlib.scrypt is required' >&2; exit 2; }
"$python_bin" runtime/runtime_server.py api &
api_pid=$!
"$python_bin" runtime/runtime_server.py ui &
ui_pid=$!
cleanup() {
  trap - EXIT INT TERM
  kill "$api_pid" "$ui_pid" 2>/dev/null || true
  wait "$api_pid" 2>/dev/null || true
  wait "$ui_pid" 2>/dev/null || true
}
trap cleanup EXIT INT TERM
attempt=0
while [ "$attempt" -lt 45 ]; do
  if curl -fsS "http://127.0.0.1:$BACKEND_PORT/api/health" >/dev/null 2>&1 && curl -fsS "http://127.0.0.1:$FRONTEND_PORT/login" >/dev/null 2>&1; then
    echo "Recipe Manager ready: API $BACKEND_PORT, UI $FRONTEND_PORT"
    wait "$api_pid"
    exit $?
  fi
  kill -0 "$api_pid" 2>/dev/null || exit 1
  kill -0 "$ui_pid" 2>/dev/null || exit 1
  attempt=$((attempt + 1))
  sleep 1
done
echo 'Recipe Manager readiness timed out' >&2
exit 1
