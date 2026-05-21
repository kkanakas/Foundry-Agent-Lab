# Demo 4: Code Demo (Code Interpreter + Gradio Web UI)

An agent that writes and runs Python code in a sandboxed environment,
presented through a Gradio web chat interface.

## Quick Start

```cmd
az login                            (once per session)
4-code-demo             (from repo root)
```

A browser tab opens automatically with the chat UI.

## Files

| File | Purpose |
|------|---------|
| `create_agent.py` | Registers agent with `CodeInterpreterTool()` |
| `chat.py` | Gradio web chat interface |
| `demo.bat` | Activates venv, creates agent, launches web UI |
| `reset.bat` | Deletes the agent if demo crashes |

## What's New (vs Demo 3)

- **Code Interpreter** — another built-in tool (like web search, one line)
- **Gradio web UI** — polished chat in the browser (~10 lines of UI code)
- **Sandboxed execution** — agent writes AND runs code server-side
- **Visual output** — web UI can render formatted results

## What This Demonstrates

- Code Interpreter as a built-in tool (`CodeInterpreterTool()`)
- Agent writing and executing Python autonomously
- Gradio as a lightweight web UI alternative
- Data analysis, calculations, and visualization capabilities

## Configuration

| Variable | Purpose | Default |
|----------|---------|---------|
| `PROJECT_ENDPOINT` | Your Foundry project endpoint | (required) |
| `AGENT_NAME` | Name for the agent | `Code-Agent` |
| `MODEL_DEPLOYMENT` | Model to use | `model-router` |

## Stopping the Demo

Close the browser tab and press `Ctrl+C` in the terminal.
