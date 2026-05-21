# Demo 2: Desktop Demo (Tkinter GUI)

The same basic agent from Demo 0, but with a desktop chat window instead of a terminal.

## Quick Start

```cmd
az login                            (once per session)
2-desktop-demo          (from repo root)
```

## Files

| File | Purpose |
|------|---------|
| `create_agent.py` | Registers the agent in Microsoft Foundry |
| `chat.py` | Tkinter GUI chat window |
| `demo.bat` | Activates venv, runs both scripts in sequence |
| `reset.bat` | Deletes the agent (use if demo crashes) |

## What's New (vs Demo 0)

- **Tkinter GUI** — scrollable chat display, text input, Send button
- **Background threading** — API calls don't freeze the window
- **Exit command** — typing "exit"/"quit" closes window and deletes agent
- **Window close** — clicking X also cleans up the agent

## What This Demonstrates

- Same agent concepts as Demo 0, packaged in a desktop UI
- Threading pattern for keeping UI responsive during API calls
- How little code it takes to go from CLI to GUI (~50 lines of tkinter)
- No extra dependencies — tkinter is built into Python

## Configuration

All config comes from `..\.env`:

| Variable | Purpose | Default |
|----------|---------|---------|
| `PROJECT_ENDPOINT` | Your Foundry project endpoint | (required) |
| `AGENT_NAME` | Name for the agent | `Desktop Demo` |
| `MODEL_DEPLOYMENT` | Model to use | `model-router` |
