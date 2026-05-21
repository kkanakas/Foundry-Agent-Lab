# Demo Script: MCP Demo

## Setup (before audience arrives)

1. Open cmd at the repo root (`foundry-agent-lab`)
2. Run `az login` once
3. Verify you have a project connection configured for the MCP server
4. Optionally test: open the MCP server URL in a browser to confirm it's reachable

## Talking Points

### Opening (30 sec)
> "MCP — Model Context Protocol — is an open standard for connecting AI
> agents to external tool servers. Instead of writing custom function tools,
> you plug into an existing ecosystem. Hundreds of MCP servers already exist."

### Show the code (2 min)
- Open `create_agent.py` — point out:
  - `MCPTool(server_label=..., server_url=..., require_approval="always")`
  - "Three lines to connect to any MCP server in the world"
  - `project_connection_id` — "auth is stored in Foundry, not in our code"
- Open `chat.py` — point out:
  - The approval loop: detect `mcp_approval_request` → show to user → collect decision
  - `McpApprovalResponse` — approve or deny
  - `previous_response_id` — links the approval back to the original request

### Run it (4 min)
```cmd
6-mcp-demo
```

### Suggested prompts (in this order!)
1. "What is my GitHub username?" (triggers a tool call — watch the approval flow)
2. "y" (another tool call — approve to see results)
3. "What's the capital of France?" (no tool needed — proves agent is smart about it)

### Key observations to call out
> "Watch the approval step. The agent TELLS you what tool it wants to call
> and what arguments it's passing. You decide whether to allow it."

> "This is the human-in-the-loop pattern. Critical for production — you don't
> want an agent creating issues or pushing code without your review."

> "Notice on question 3, NO approval was requested. The agent knows it
> doesn't need an external tool for general knowledge."

> "Compare this to Demo 1 — with function calling, WE wrote the tool code.
> With MCP, someone else hosts the tools. We just connect and approve."

### Demonstrate denial (optional, high impact)
4. Ask something that triggers a tool call, then type `n` to deny
> "See? The agent gracefully handles denial. It doesn't crash — it tells
> you it couldn't get the information."

### Exit
Type `exit` — agent gets deleted.

## If something goes wrong

**"Unauthorized" from MCP server**: Your project connection credentials may be
expired. Update the connection in Foundry portal.

**No approval requests appear**: The agent may answer from general knowledge.
Ask something specifically about YOUR GitHub account.

**Agent leftover from previous run**:
```cmd
mcp-demo\reset.bat
```

## Duration
~5-6 minutes total
