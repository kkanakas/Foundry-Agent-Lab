"""
create_agent.py — Create a prompt agent with function calling (tool use).

This agent has access to a get_weather tool. When a user asks about the
weather, the agent will call the function, and our code executes it locally.

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
AGENT_NAME = os.environ.get("AGENT_NAME", "Weather-Agent")
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
# 4. Define and create the agent with tools
# ---------------------------------------------------------------------------
from azure.ai.projects.models import PromptAgentDefinition, Tool, FunctionTool

# Define the function tool schema that tells the model what it can call.
# The model decides WHEN to call it based on the user's question.
func_tool = FunctionTool(
    name="get_weather",
    description="Get the current weather for a given city. Returns temperature, condition, and humidity.",
    parameters={
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The city name (e.g., 'Seattle', 'London', 'Tokyo')"
            }
        },
        "required": ["city"],
        "additionalProperties": False,
    },
    strict=True,
)

tools: list[Tool] = [func_tool]

agent = project.agents.create_version(
    agent_name=AGENT_NAME,
    definition=PromptAgentDefinition(
        model=MODEL_DEPLOYMENT,
        instructions=(
            "You are a helpful assistant with access to a weather tool. "
            "When users ask about the weather, use the get_weather function. "
            "Present the weather information in a friendly, readable format. "
            "For non-weather questions, answer normally."
        ),
        tools=tools,
    ),
)

# ---------------------------------------------------------------------------
# 5. Confirm success
# ---------------------------------------------------------------------------
print(f"✓ Agent \"{agent.name}\" created")
print(f"  Model: {MODEL_DEPLOYMENT}")
print(f"  Tools: get_weather")
_tee.console_only(f"  Endpoint: {PROJECT_ENDPOINT}")
print()
