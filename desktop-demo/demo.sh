#!/usr/bin/env zsh
set -euo pipefail
SCRIPT_DIR="${0:A:h}"
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

printf '=== Running create_agent.py ===\n'
"$PY" "$SCRIPT_DIR/create_agent.py"

printf '\n=== Launching desktop chat window ===\n'
exec "$PY" "$SCRIPT_DIR/chat.py"