"""
create_agent.py — Create (or update) a prompt agent in Azure AI Foundry.

Run this script once to register your agent. After that, use chat.py to
interact with it. You can re-run this script to update the agent's
instructions or model.

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

# ---------------------------------------------------------------------------
# 1. Load environment variables
# ---------------------------------------------------------------------------
from pathlib import Path

_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path, override=True)

PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
AGENT_NAME = os.environ.get("AGENT_NAME", "Desktop Demo")
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
# 4. Define and create the agent
# ---------------------------------------------------------------------------
from azure.ai.projects.models import PromptAgentDefinition

agent = project.agents.create_version(
    agent_name=AGENT_NAME,
    definition=PromptAgentDefinition(
        model=MODEL_DEPLOYMENT,
        instructions=(
            "You are a helpful, friendly assistant. "
            "Answer questions clearly and concisely. "
            "When the user asks a follow-up, use conversation context."
        ),
    ),
)

# ---------------------------------------------------------------------------
# 5. Confirm success
# ---------------------------------------------------------------------------
print(f"✓ Agent \"{agent.name}\" created")
print(f"  Model: {MODEL_DEPLOYMENT}")
_tee.console_only(f"  Endpoint: {PROJECT_ENDPOINT}")
print()
