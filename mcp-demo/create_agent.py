"""
create_agent.py — Create a prompt agent with MCP (Model Context Protocol) tool.

The agent connects to a remote MCP server (e.g., GitHub) and can use
tools exposed by that server. This demonstrates how agents integrate
with external tool ecosystems via the open MCP standard.

This script:
1. Configures an MCPTool pointing to a remote MCP server
2. Creates an agent with that tool enabled
3. The agent can then invoke MCP server tools with approval

Prerequisites:
  1. From repo root: pip install -r requirements.txt
  2. az login
  3. Copy .env.sample to .env in this folder and fill in your values
  4. Set up a project connection in Foundry portal for your MCP server auth
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
AGENT_NAME = os.environ.get("AGENT_NAME", "MCP-Agent")
MODEL_DEPLOYMENT = os.environ.get("MODEL_DEPLOYMENT", "model-router")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "https://api.githubcopilot.com/mcp")
MCP_SERVER_LABEL = os.environ.get("MCP_SERVER_LABEL", "github")
MCP_CONNECTION_NAME = os.environ.get("MCP_CONNECTION_NAME", "my-github-mcp-connection")

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
# 4. Define and create the agent with MCP tool
# ---------------------------------------------------------------------------
from azure.ai.projects.models import PromptAgentDefinition, MCPTool

tool = MCPTool(
    server_label=MCP_SERVER_LABEL,
    server_url=MCP_SERVER_URL,
    require_approval="always",  # For demo purposes, require approval for every tool call
    project_connection_id=MCP_CONNECTION_NAME,
)

agent = project.agents.create_version(
    agent_name=AGENT_NAME,
    definition=PromptAgentDefinition(
        model=MODEL_DEPLOYMENT,
        instructions=(
            "You are a helpful assistant connected to external tools via MCP. "
            "Use the available MCP tools when the user asks about their GitHub "
            "profile, repositories, issues, or other GitHub-related information. "
            "Always explain what tool you're about to use before invoking it."
        ),
        tools=[tool],
    ),
)

# ---------------------------------------------------------------------------
# 5. Confirm success
# ---------------------------------------------------------------------------
print(f"✓ Agent \"{agent.name}\" created")
print(f"  Model: {MODEL_DEPLOYMENT}")
print(f"  Tools: MCP ({MCP_SERVER_LABEL})")
print(f"  Approval: always (you review each tool call)")
_tee.console_only(f"  Connection: {MCP_CONNECTION_NAME}")
_tee.console_only(f"  Endpoint: {PROJECT_ENDPOINT}")
print()
