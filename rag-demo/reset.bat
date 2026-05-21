@echo off
set "PY=%~dp0..\.venv\Scripts\python.exe"
echo Cleaning up RAG-Agent resources...
"%PY%" -c "
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path('%~dp0.env'), override=True)
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
p = AIProjectClient(endpoint=os.environ['PROJECT_ENDPOINT'], credential=DefaultAzureCredential())
openai = p.get_openai_client()
name = os.environ.get('AGENT_NAME', 'RAG-Agent')
try:
    p.agents.delete(agent_name=name)
    print(f'Agent \"{name}\" deleted.')
except: print('No agent to delete.')
vs_file = Path('%~dp0.vector_store_id')
if vs_file.exists():
    vs_id = vs_file.read_text().strip()
    try:
        openai.vector_stores.delete(vs_id)
        print(f'Vector store {vs_id} deleted.')
        vs_file.unlink()
    except: print('Could not delete vector store.')
" 2>nul
echo Reset complete.
