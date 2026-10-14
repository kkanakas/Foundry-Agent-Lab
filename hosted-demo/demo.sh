#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$SCRIPT_DIR/../.venv/bin/python"

if [[ ! -x "$PY" ]]; then
    printf 'Missing virtual environment. Run python3 -m venv .venv and install requirements.txt from the repository root.\n' >&2
    exit 1
fi

export LOG_FILE=""
if [[ "${1:-}" == "log" ]]; then
    export LOG_FILE="$SCRIPT_DIR/chat-log.txt"
    printf '[Logging to %s]\n' "$LOG_FILE"
fi

"$PY" - <<'PYTHON'
import socket
import sys

with socket.socket() as probe:
    try:
        probe.bind(("127.0.0.1", 8088))
    except OSError:
        sys.exit("Port 8088 is already in use. Stop the existing server before running this demo.")
PYTHON

cleanup() {
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
}

printf '=== Starting hosted agent server ===\n'
"$PY" "$SCRIPT_DIR/main.py" >/dev/null &
SERVER_PID=$!
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

"$PY" - "$SERVER_PID" <<'PYTHON'
import os
import socket
import sys
import time

server_pid = int(sys.argv[1])
deadline = time.monotonic() + 30
while time.monotonic() < deadline:
    try:
        os.kill(server_pid, 0)
    except ProcessLookupError:
        sys.exit("Hosted agent server exited before it was ready.")
    try:
        with socket.create_connection(("127.0.0.1", 8088), timeout=0.5):
            break
    except OSError:
        time.sleep(0.1)
else:
    sys.exit("Hosted agent server did not become ready on port 8088 within 30 seconds.")
PYTHON
kill -0 "$SERVER_PID"
printf 'Server running on http://localhost:8088\n'

printf '\n=== Running chat.py ===\n'
"$PY" "$SCRIPT_DIR/chat.py"