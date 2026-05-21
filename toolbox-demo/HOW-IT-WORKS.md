# How It Works: Toolbox Demo

## Architecture

```
┌─────────────┐     ┌──────────────────────────────────────────────────┐
│   Your CLI  │────▶│  Foundry Toolbox (MCP-compatible endpoint)       │
│  (chat.py)  │◀────│                                                  │
└─────────────┘     │  ┌─────────────────┐  ┌──────────────────────┐  │
       │            │  │ github-issues   │  │ github-repos         │  │
       │  Bearer    │  │ (6 curated)     │  │ (6 curated)          │  │
       │  Token     │  └─────────────────┘  └──────────────────────┘  │
       │  Auth      │                                                  │
       │            │  Versioned · Governed · Centrally Managed        │
       ▼            └──────────────────────────────────────────────────┘
┌──────────────┐
│  OpenAI API  │    chat.py uses the Responses API for reasoning;
│  (Responses) │    tool calls are proxied through the MCP session.
└──────────────┘
```

### Microsoft Agent Framework (MAF) Pattern

This demo follows the **MAF consumption pattern** from the
[Azure docs](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/toolbox?pivots=python#microsoft-agent-framework):

1. **Create toolbox** — `create_agent.py` registers a versioned toolbox
2. **Connect with auth** — `chat.py` opens an MCP session to the toolbox
   endpoint using bearer-token auth (`DefaultAzureCredential` →
   `https://ai.azure.com/.default` scope)
3. **Discover tools** — `session.list_tools()` returns all bundled tools
4. **Chat loop** — model decides which tools to invoke; user approves;
   `session.call_tool()` executes via the MCP connection

## What is a Toolbox?

A **Toolbox** is a managed resource in Microsoft Foundry that bundles multiple
tools into a single, versioned, MCP-compatible endpoint. Think of it as a
"tool registry" with these properties:

- **Centralized** — defined once, consumed by any agent
- **Versioned** — immutable snapshots; promote a version when ready
- **MCP-compatible** — any MCP client or agent can connect
- **Governed** — credential injection, approval policies, and observability
- **Multi-tool** — bundle MCP servers, AI Search, and more behind one facade
- **Curated** — use `allowed_tools` to expose only approved tool subsets

## Why Toolbox? (The Problem It Solves)

Without Toolbox:
```
Agent A ──── wires up ──── GitHub (all 44 tools)
Agent B ──── wires up ──── GitHub (all 44 tools, duplicate)
Agent C ──── wires up ──── GitHub (different subset?)
```

With Toolbox:
```
Platform Team ──── creates ──── Toolbox (6 issue tools + 6 repo tools, curated)
Agent A ──── connects to ──── Toolbox endpoint
Agent B ──── connects to ──── Toolbox endpoint
Agent C ──── connects to ──── Toolbox endpoint
```

## Code Flow

### create_agent.py

```python
# Create a toolbox version with two curated tool groups
toolbox_version = project.beta.toolboxes.create_version(
    name="demo-toolbox",
    description="Demo toolbox with curated GitHub tools (issues + repos)",
    tools=[
        MCPTool(
            server_label="github-issues",
            server_url="https://api.githubcopilot.com/mcp",
            require_approval="always",
            project_connection_id="my-github-mcp-connection",
            allowed_tools=["github___list_issues", "github___issue_read", ...],
        ),
        MCPTool(
            server_label="github-repos",
            server_url="https://api.githubcopilot.com/mcp",
            require_approval="always",
            project_connection_id="my-github-mcp-connection",
            allowed_tools=["github___search_repositories", "github___get_file_contents", ...],
        ),
    ],
)
```

### chat.py (MAF Pattern)

```python
# 1. Get bearer token for toolbox auth
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
token_provider = get_bearer_token_provider(credential, "https://ai.azure.com/.default")

# 2. Connect to toolbox MCP endpoint with auth headers
headers = {
    "Authorization": f"Bearer {token_provider()}",
    "Foundry-Features": "Toolboxes=V1Preview",
}
async with streamablehttp_client(url=TOOLBOX_MCP_ENDPOINT, headers=headers) as (r, w, _):
    async with ClientSession(r, w) as session:
        await session.initialize()

        # 3. Discover tools from the toolbox
        tools = (await session.list_tools()).tools

        # 4. Use OpenAI Responses API with discovered tools
        response = openai.responses.create(
            model="model-router",
            input=messages,
            tools=[...converted from MCP tools...],
        )

        # 5. When model calls a tool, execute via MCP session
        result = await session.call_tool(tool_name, arguments)
```

## Key Differences from Direct MCP (Demo 6)

| Aspect | Demo 6 (Direct MCP) | Demo 7 (Toolbox) |
|--------|---------------------|-------------------|
| Tool wiring | Agent → MCP server directly | Agent → Toolbox endpoint → tools |
| Multi-tool | One MCP server per tool config | Bundle ALL tools in one toolbox |
| Versioning | None (live server) | Immutable versions, promote when ready |
| Governance | Per-agent config | Centralized: define once, use everywhere |
| Credential mgmt | Per-agent connection | Platform-level injection |
| Discovery | Agent must know each server URL | Single endpoint, tools/list returns all |

## Toolbox Versioning

```
Toolbox: "demo-toolbox"
├── v1 (default) ── GitHub Issues (read-only, 6 tools)
├── v2 ── GitHub Issues + Repos (read-only, 12 tools)
└── v3 ── GitHub Issues + Repos + write tools (18 tools)

# Promote v2 to default:
project.beta.toolboxes.update(toolbox_name="demo-toolbox", default_version="v2")
# All agents immediately get v2's tools — no code changes!
```

## Toolbox MCP Endpoint Patterns

| Who | Endpoint | Use case |
|-----|----------|----------|
| Developer | `{project}/toolboxes/{name}/versions/{v}/mcp?api-version=v1` | Test specific version |
| Consumer | `{project}/toolboxes/{name}/mcp?api-version=v1` | Always serves default_version |

## Tool Types Supported

| Tool Type | SDK Class | Notes |
|-----------|-----------|-------|
| Web Search | `WebSearchTool()` | No connection needed |
| MCP Server | `MCPTool(...)` | Needs connection for auth |
| Azure AI Search | `AzureAISearchTool(...)` | Needs index + connection |
| Code Interpreter | `CodeInterpreterTool()` | No connection needed |
| File Search | `FileSearchTool(...)` | Needs vector store ID |
| OpenAPI | `OpenAPITool(...)` | Needs spec + auth config |
| Agent-to-Agent | `A2APreviewTool(...)` | Needs agent URL + connection |

## Enterprise Value

1. **Reusability** — define tools once, all agents consume the same toolbox
2. **Versioning** — stage → test → promote; rollback by changing default_version
3. **Governance** — approval policies, credential isolation, audit trail
4. **Simplicity** — agents connect to one endpoint; platform handles the rest
5. **Open standard** — any MCP-compatible client works (not just Azure agents)
