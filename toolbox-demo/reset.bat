@echo off
set "PY=%~dp0..\.venv\Scripts\python.exe"
echo Deleting agent "Toolbox-Agent" and toolbox "demo-toolbox"...
"%PY%" -c "import os; from pathlib import Path; from dotenv import load_dotenv; load_dotenv(Path('%~dp0.env'), override=True); from azure.identity import DefaultAzureCredential; from azure.ai.projects import AIProjectClient; p=AIProjectClient(endpoint=os.environ['PROJECT_ENDPOINT'],credential=DefaultAzureCredential()); p.agents.delete(agent_name=os.environ.get('AGENT_NAME','Toolbox-Agent')); print('Agent deleted.')" 2>nul
if %ERRORLEVEL% neq 0 echo No agent to delete (already clean).
echo Reset complete.
