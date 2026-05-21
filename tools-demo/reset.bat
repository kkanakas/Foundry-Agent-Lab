@echo off
set "PY=%~dp0..\.venv\Scripts\python.exe"
echo Deleting agent "Weather-Agent"...
"%PY%" -c "import os; from pathlib import Path; from dotenv import load_dotenv; load_dotenv(Path('%~dp0.env'), override=True); from azure.identity import DefaultAzureCredential; from azure.ai.projects import AIProjectClient; p=AIProjectClient(endpoint=os.environ['PROJECT_ENDPOINT'],credential=DefaultAzureCredential()); p.agents.delete(agent_name=os.environ.get('AGENT_NAME','Weather-Agent')); print('Done.')" 2>nul
if %ERRORLEVEL% neq 0 echo No agent to delete (already clean).
echo Reset complete.
