"""
create_agent.py — Create a prompt agent with code interpreter.

The agent can write and run Python code in a sandboxed environment.
Useful for data analysis, math, charts, and file processing.
Like web search, this is a built-in tool — Foundry executes the code.

Prerequisites:
  1. From repo root: pip install -r requirements.txt
  2. az login
  3. Copy .env.sample to .env in this folder and fill in your values
"""

import os
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))
import _tee  # noqa: E402 - activates LOG_FILE output capture

from dotenv import load_dotenv
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Load environment variables
# ---------------------------------------------------------------------------
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path, override=True)

PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
AGENT_NAME = os.environ.get("AGENT_NAME", "Code-Agent")
MODEL_DEPLOYMENT = os.environ.get("MODEL_DEPLOYMENT", "model-router")

if not PROJECT_ENDPOINT:
    print("ERROR: PROJECT_ENDPOINT is not set.")
    print("Copy .env.sample to .env in this folder and fill in your Foundry project endpoint.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 2. Authenticate with Azure
# ---------------------------------------------------------------------------
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()

# ---------------------------------------------------------------------------
# 3. Create the AI Project client
# ---------------------------------------------------------------------------
from azure.ai.projects import AIProjectClient

project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=credential,
)

# ---------------------------------------------------------------------------
# 4. Define and create the agent with code interpreter
# ---------------------------------------------------------------------------
from azure.ai.projects.models import PromptAgentDefinition, CodeInterpreterTool

agent = project.agents.create_version(
    agent_name=AGENT_NAME,
    definition=PromptAgentDefinition(
        model=MODEL_DEPLOYMENT,
        instructions=(
            "You are a data analyst assistant with Python code execution capability. "
            "When users ask for calculations, data analysis, or visualizations, "
            "write and run Python code to produce accurate results. "
            "Show your code and explain your approach. "
            "For charts, use matplotlib and save to a file."
        ),
        tools=[CodeInterpreterTool()],
    ),
)

# ---------------------------------------------------------------------------
# 5. Confirm success
# ---------------------------------------------------------------------------
print(f"✓ Agent \"{agent.name}\" created")
print(f"  Model: {MODEL_DEPLOYMENT}")
print(f"  Tools: code_interpreter (built-in, sandboxed Python)")
_tee.console_only(f"  Endpoint: {PROJECT_ENDPOINT}")
print()
