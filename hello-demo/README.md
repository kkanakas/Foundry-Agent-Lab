# Demo 0: Hello Demo (CLI Chat)

The simplest Microsoft Foundry agent — a prompt agent you chat with in the terminal.

## Quick Start

```cmd
az login                        (once per session)
0-hello-demo              (from repo root)
```

## Files

| File | Purpose |
|------|---------|
| `create_agent.py` | Registers the agent in Microsoft Foundry |
| `chat.py` | Interactive terminal chat loop |
| `demo.bat` | Activates venv, runs both scripts in sequence |
| `reset.bat` | Deletes the agent (use if demo crashes) |

## What This Demonstrates

- Creating a prompt agent with `PromptAgentDefinition`
- Azure authentication with `DefaultAzureCredential`
- Multi-turn conversations using server-side conversation state
- The OpenAI-compatible Responses API via `project.get_openai_client()`

## Configuration

All config comes from `..\.env`:

| Variable | Purpose | Default |
|----------|---------|---------|
| `PROJECT_ENDPOINT` | Your Foundry project endpoint | (required) |
| `AGENT_NAME` | Name for the agent | `Hello-Agent` |
| `MODEL_DEPLOYMENT` | Model to use | `model-router` |
