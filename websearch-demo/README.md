# Demo 3: WebSearch Demo (Built-in Web Search)

An agent with real-time web search — the simplest built-in tool. Foundry handles
the search server-side; no tool-calling loop needed in your code.

## Quick Start

```cmd
az login                            (once per session)
3-websearch-demo        (from repo root)
```

## Files

| File | Purpose |
|------|---------|
| `create_agent.py` | Registers agent with `WebSearchTool()` |
| `chat.py` | Chat loop (no tool loop — search is server-side) |
| `demo.bat` | Activates venv, runs both scripts |
| `reset.bat` | Deletes the agent if demo crashes |

## What's New (vs Demo 1)

- **Built-in tool** — one line: `tools=[WebSearchTool()]`
- **No tool-calling loop** — Foundry executes the search, not your code
- **Citations included** — responses reference their sources
- **Key concept**: Built-in tools (server-managed) vs Function tools (client-managed)

## What This Demonstrates

- The difference between built-in tools and function calling
- How little code is needed for server-side tools
- Real-time information retrieval with citations
- The agent deciding WHEN to search vs answer from knowledge

## Configuration

| Variable | Purpose | Default |
|----------|---------|---------|
| `PROJECT_ENDPOINT` | Your Foundry project endpoint | (required) |
| `AGENT_NAME` | Name for the agent | `Search-Agent` |
| `MODEL_DEPLOYMENT` | Model to use | `model-router` |
