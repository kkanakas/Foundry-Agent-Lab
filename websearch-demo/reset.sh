#!/usr/bin/env zsh
set -euo pipefail
SCRIPT_DIR="${0:A:h}"
PY="$SCRIPT_DIR/../.venv/bin/python"

if [[ ! -x "$PY" ]]; then
    printf 'Missing virtual environment. Run python3 -m venv .venv and install requirements.txt from the repository root.\n' >&2
    exit 1
fi

printf 'Deleting agent "Search-Agent"...\n'
if ! "$PY" - "$SCRIPT_DIR" 2>/dev/null <<'PYTHON'
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv(Path(sys.argv[1]) / ".env", override=True)
project = AIProjectClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=DefaultAzureCredential())
project.agents.delete(agent_name=os.environ.get("AGENT_NAME", "Search-Agent"))
print("Done.")
PYTHON
then
    printf 'No agent to delete (already clean).\n'
fi
printf 'Reset complete.\n'