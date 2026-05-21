# How It Works: MCP Demo

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Your CLI  │────▶│  Azure Foundry   │────▶│  Remote MCP     │
│  (chat.py)  │◀────│  Agent Service   │◀────│  Server (GitHub)│
└─────────────┘     └──────────────────┘     └─────────────────┘
       │                                              │
       │  approval_request ◀──────────────────────────┘
       │  approval_response ──────────────────────────▶
       │
```

## What is MCP?

Model Context Protocol (MCP) is an open standard that defines how applications
provide tools and contextual data to large language models. Think of it as a
universal plug for connecting AI agents to external services.

Instead of building custom function tools for every service, you connect to an
MCP server that already exposes tools in a standard format.

## The Approval Pattern

Unlike Demo 1 (function calling) where tools execute automatically, MCP tools
use a **human-in-the-loop** approval flow:

1. **Agent decides** to call an MCP tool (based on your question)
2. **Service returns** an `mcp_approval_request` instead of executing
3. **You review** the tool name and arguments
4. **You approve or deny** — your decision is sent back
5. **Tool executes** (if approved) and agent uses the result

This is critical for production because MCP tools can:
- Read private data (your repos, issues, profile)
- Write/modify data (create issues, push code)
- Access external services (billing, infrastructure)

## Code Flow

### create_agent.py

```python
# MCPTool declaration — connects to a remote MCP server
tool = MCPTool(
    server_label="github",              # Unique label for this server
    server_url="https://api.githubcopilot.com/mcp",  # Server endpoint
    require_approval="always",          # Always ask before executing
    project_connection_id="...",        # Auth stored in Foundry
)
```

### chat.py

```python
# 1. Send message — agent may request tool approval
response = openai.responses.create(
    input=user_input,
    conversation=conversation.id,
    extra_body={"agent_reference": {"name": AGENT_NAME, ...}},
)

# 2. Check for approval requests
for item in response.output:
    if item.type == "mcp_approval_request":
        approval_list.append(McpApprovalResponse(
            approve=True, approval_request_id=item.id
        ))

# 3. Send approval back (same conversation, no previous_response_id)
response = openai.responses.create(
    input=approval_list,
    conversation=conversation.id,
    extra_body={"agent_reference": ...},
)
```

## Key Differences from Function Calling (Demo 1)

| Aspect | Demo 1 (FunctionTool) | Demo 6 (MCPTool) |
|--------|----------------------|------------------|
| Tool execution | Client-side (your code) | Server-side (remote MCP server) |
| Tool definition | You write the schema + code | MCP server exposes tools |
| Approval | None (auto-execute) | Human-in-the-loop |
| Ecosystem | Custom per-agent | Open standard, shared across agents |
| Auth | Your code handles it | Project connection in Foundry |

## Authentication

MCP server credentials are stored as a **project connection** in Foundry:
- You never put tokens in code or .env files
- Foundry handles token injection at runtime
- Supports API keys, bearer tokens, and OAuth

## Approval Modes

```python
require_approval="always"              # Every call needs approval
require_approval="never"               # Auto-approve all calls
require_approval={"never": ["get_user_profile"]}  # Auto-approve specific tools
require_approval={"always": ["create_issue"]}     # Only require for risky tools
```

## Why MCP Matters

1. **Universal standard** — one integration pattern works for any MCP server
2. **Ecosystem growth** — hundreds of MCP servers already exist (GitHub, Slack, DBs, etc.)
3. **Security** — approval flow prevents unauthorized actions
4. **Separation of concerns** — tool logic lives on the server, not in your agent code
