# Demo 1: Tools Demo (Function Calling)

An agent that can call a real weather API — demonstrating function calling (tool use).

## Quick Start

```cmd
az login                            (once per session)
1-tools-demo            (from repo root)
```

## Files

| File | Purpose |
|------|---------|
| `create_agent.py` | Registers agent WITH a `get_weather` function tool |
| `chat.py` | Chat loop that handles the tool-calling handshake |
| `demo.bat` | Activates venv, runs both scripts in sequence |
| `reset.bat` | Deletes the agent (use if demo crashes) |

## What's New (vs Demo 0)

- **FunctionTool definition** — tells the model what it can call
- **Tool-calling loop** — detects function_call in response, executes locally, sends result back
- **Live API call** — `wttr.in` weather API (free, no key needed)
- **Console trace** — prints 🔧 when the tool fires so audience sees it happen

## What This Demonstrates

- Defining tools with `FunctionTool` and JSON Schema parameters
- The tool-calling handshake (model requests → app executes → model continues)
- Using `FunctionCallOutput` to return results to the agent
- Real-time data the model can't fake (proves tool was used)

## Configuration

All config comes from `..\.env`:

| Variable | Purpose | Default |
|----------|---------|---------|
| `PROJECT_ENDPOINT` | Your Foundry project endpoint | (required) |
| `AGENT_NAME` | Name for the agent | `Weather-Agent` |
| `MODEL_DEPLOYMENT` | Model to use | `model-router` |
