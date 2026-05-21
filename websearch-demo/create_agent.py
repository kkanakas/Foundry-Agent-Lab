"""
create_agent.py — Create a prompt agent with web search capability.

The agent can search the web for real-time information and return
answers with inline citations. This is a built-in tool — Foundry
handles execution server-side (no client-side tool loop needed).

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
AGENT_NAME = os.environ.get("AGENT_NAME", "Search-Agent")
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
# 4. Define and create the agent with web search
# ---------------------------------------------------------------------------
from azure.ai.projects.models import PromptAgentDefinition, WebSearchTool

agent = project.agents.create_version(
    agent_name=AGENT_NAME,
    definition=PromptAgentDefinition(
        model=MODEL_DEPLOYMENT,
        instructions=(
            "You are a helpful research assistant with web search access. "
            "When users ask about current events, recent news, or factual questions "
            "that benefit from up-to-date information, search the web. "
            "Always cite your sources. For general knowledge questions, answer directly."
        ),
        tools=[WebSearchTool()],
    ),
)

# ---------------------------------------------------------------------------
# 5. Confirm success
# ---------------------------------------------------------------------------
print(f"✓ Agent \"{agent.name}\" created")
print(f"  Model: {MODEL_DEPLOYMENT}")
print(f"  Tools: web_search (built-in, server-side)")
_tee.console_only(f"  Endpoint: {PROJECT_ENDPOINT}")
print()
