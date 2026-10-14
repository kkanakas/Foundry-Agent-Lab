#!/usr/bin/env zsh
set -euo pipefail
SCRIPT_DIR="${0:A:h}"
PY="$SCRIPT_DIR/../.venv/bin/python"

if [[ ! -x "$PY" ]]; then
    printf 'Missing virtual environment. Run python3 -m venv .venv and install requirements.txt from the repository root.\n' >&2
    exit 1
fi

printf 'Cleaning up RAG-Agent resources...\n'
if ! "$PY" - "$SCRIPT_DIR" 2>/dev/null <<'PYTHON'
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

script_dir = Path(sys.argv[1])
load_dotenv(script_dir / ".env", override=True)
project = AIProjectClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=DefaultAzureCredential())
openai = project.get_openai_client()
name = os.environ.get("AGENT_NAME", "RAG-Agent")
try:
    project.agents.delete(agent_name=name)
    print(f'Agent "{name}" deleted.')
except Exception:
    print("No agent to delete.")

vector_store_file = script_dir / ".vector_store_id"
if vector_store_file.exists():
    vector_store_id = vector_store_file.read_text().strip()
    try:
        openai.vector_stores.delete(vector_store_id)
        print(f"Vector store {vector_store_id} deleted.")
        vector_store_file.unlink()
    except Exception:
        print("Could not delete vector store.")
PYTHON
then
    printf 'Could not complete RAG cleanup.\n'
fi
printf 'Reset complete.\n'