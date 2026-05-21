"""
create_agent.py — Create a Foundry Toolbox (centrally managed tool collection).

A Toolbox is a versioned collection of tools exposed through a single
MCP-compatible endpoint.  This script creates (or updates) a toolbox
version with Web Search + GitHub MCP tools.

The toolbox is consumed by chat.py which connects to the toolbox's MCP
endpoint using the Microsoft Agent Framework pattern (bearer-token auth).

Prerequisites:
  1. From repo root: pip install -r requirements.txt
  2. az login
  3. Copy .env.sample to .env in this folder and fill in your values
  4. Have a project connection configured for any MCP servers in the toolbox
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
TOOLBOX_NAME = os.environ.get("TOOLBOX_NAME", "demo-toolbox")
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
# 4. Create a Toolbox version with two curated MCP tool groups
# ---------------------------------------------------------------------------
from azure.ai.projects.models import MCPTool

print(f"Creating toolbox version: {TOOLBOX_NAME}")
print(f"  Tools: github-issues + github-repos (curated subsets)")

toolbox_version = project.beta.toolboxes.create_version(
    name=TOOLBOX_NAME,
    description="Demo toolbox with curated GitHub tools (issues + repos)",
    tools=[
        # Group 1: Issue management tools
        MCPTool(
            server_label="github-issues",
            server_url=MCP_SERVER_URL,
            require_approval="always",
            project_connection_id=MCP_CONNECTION_NAME,
            allowed_tools=[
                "github___list_issues",
                "github___issue_read",
                "github___issue_write",
                "github___search_issues",
                "github___add_issue_comment",
                "github___get_label",
            ],
        ),
        # Group 2: Repository browsing tools
        MCPTool(
            server_label="github-repos",
            server_url=MCP_SERVER_URL,
            require_approval="always",
            project_connection_id=MCP_CONNECTION_NAME,
            allowed_tools=[
                "github___search_repositories",
                "github___get_file_contents",
                "github___list_branches",
                "github___list_commits",
                "github___search_code",
                "github___list_tags",
            ],
        ),
    ],
)

print(f"✓ Toolbox \"{toolbox_version.name}\" version {toolbox_version.version} created")

# ---------------------------------------------------------------------------
# 5. Print the toolbox MCP endpoint (used by chat.py)
# ---------------------------------------------------------------------------
TOOLBOX_MCP_ENDPOINT = (
    f"{PROJECT_ENDPOINT}/toolboxes/{TOOLBOX_NAME}/mcp?api-version=v1"
)

_tee.console_only(f"  Toolbox MCP endpoint: {TOOLBOX_MCP_ENDPOINT}")
print()
print("Next step: run chat.py to interact with the toolbox tools.")
print()
