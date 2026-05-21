# Demo 7: Toolbox Demo (Centralized Tool Governance)

An agent powered by a **Foundry Toolbox** — a centrally managed, versioned collection of tools exposed through a single MCP-compatible endpoint.

## Quick Start

```cmd
az login                            (once per session)
7-toolbox-demo            (from repo root)
```

## Files

| File | Purpose |
|------|---------|
| `create_agent.py` | Creates a toolbox version (WebSearch + MCP) then an agent that consumes it |
| `chat.py` | Chat loop with tool approval flow (same as MCP demo) |
| `demo.bat` | Activates venv, runs both scripts in sequence |
| `reset.bat` | Deletes the agent (use if demo crashes) |

## What's New (vs Demo 6 — MCP)

- **Toolbox creation** — `project.beta.toolboxes.create_toolbox_version()` bundles multiple tools into one managed resource
- **Single endpoint** — agent connects to ONE toolbox MCP endpoint, not individual tool servers
- **Versioning** — toolbox versions are immutable snapshots; promote a version to default when ready
- **Centralized governance** — tools are defined once, consumed by any agent; credential injection and policy enforcement happen at runtime
- **Multi-tool bundling** — WebSearch + MCP (GitHub) in a single toolbox

## What This Demonstrates

- Creating a toolbox with `WebSearchTool` + `MCPTool` in one version
- The toolbox MCP endpoint pattern: `{project_endpoint}/toolboxes/{name}/mcp?api-version=v1`
- Agent consuming a toolbox through its unified MCP endpoint
- Human-in-the-loop approval for toolbox tool invocations
- Enterprise pattern: define tools centrally, consume anywhere

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────────┐
│   Your CLI  │────▶│  Azure Foundry   │────▶│  Foundry Toolbox        │
│  (chat.py)  │◀────│  Agent Service   │◀────│  (single MCP endpoint)  │
└─────────────┘     └──────────────────┘     │                         │
                                              │  ┌─────────────────┐   │
                                              │  │  Web Search     │   │
                                              │  ├─────────────────┤   │
                                              │  │  MCP (GitHub)   │   │
                                              │  └─────────────────┘   │
                                              └─────────────────────────┘
```

## Configuration

All config comes from `.env` (copy `.env.sample`):

| Variable | Purpose | Default |
|----------|---------|---------|
| `PROJECT_ENDPOINT` | Your Foundry project endpoint | (required) |
| `AGENT_NAME` | Name for the agent | `Toolbox-Agent` |
| `MODEL_DEPLOYMENT` | Model to use | `model-router` |
| `TOOLBOX_NAME` | Name of the toolbox | `demo-toolbox` |
| `MCP_SERVER_URL` | MCP server included in toolbox | `https://api.githubcopilot.com/mcp` |
| `MCP_SERVER_LABEL` | Label for the MCP server | `github` |
| `MCP_CONNECTION_NAME` | Project connection for MCP auth | `my-github-mcp-connection` |
