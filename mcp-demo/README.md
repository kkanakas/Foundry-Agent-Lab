# Demo 6: MCP (Model Context Protocol)

Connect your agent to external tool ecosystems using the open MCP standard.
The agent calls tools hosted on a remote MCP server (e.g., GitHub) with
human-in-the-loop approval for every tool invocation.

## What's new in this demo

| Concept | Description |
|---------|-------------|
| MCPTool | Connects the agent to a remote MCP server endpoint |
| Approval flow | You review and approve/deny each tool call before execution |
| Project connections | Auth credentials stored in Foundry, not in code |
| Open standard | MCP works across tool providers — same pattern for any server |

## Prerequisites

- Completed the [root setup](../README.md#one-time-setup)
- A project connection configured in Foundry portal for your MCP server
  (e.g., a GitHub personal access token stored as a connection)

## Setup

1. Copy `.env.sample` to `.env` and fill in:
   - `PROJECT_ENDPOINT` — your Foundry project endpoint
   - `MCP_SERVER_URL` — the MCP server URL (default: GitHub)
   - `MCP_CONNECTION_NAME` — the project connection ID for auth

2. Create the project connection in Foundry portal:
   - Go to your project → Settings → Connections
   - Add a new connection with your MCP server credentials
   - Note the connection name/ID

## Running

```cmd
6-mcp-demo
```

Or with logging:
```cmd
6-mcp-demo log
```

## How the approval flow works

1. You ask a question (e.g., "What's my GitHub username?")
2. The agent decides to call an MCP tool
3. You see the tool name and arguments
4. You type `y` to approve or `n` to deny
5. If approved, the tool executes and the agent uses the result

This is the **human-in-the-loop** pattern — critical for production agents
that can modify external systems.

## Files

| File | Purpose |
|------|---------|
| `create_agent.py` | Configures MCPTool and creates the agent |
| `chat.py` | Interactive CLI with approval flow |
| `demo.bat` | End-to-end launcher |
| `reset.bat` | Deletes the agent |

## Key code

```python
from azure.ai.projects.models import MCPTool

tool = MCPTool(
    server_label="github",
    server_url="https://api.githubcopilot.com/mcp",
    require_approval="always",
    project_connection_id="my-github-mcp-connection",
)
```

## Cleanup

```cmd
mcp-demo\reset.bat
```
