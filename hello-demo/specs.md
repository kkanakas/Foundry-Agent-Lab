# Hello Demo — Specification

An interactive terminal chatbot powered by Microsoft Foundry Agent Service.
Based on the [official quickstart](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-agent?tabs=python).

## Overview

This demo creates a **prompt agent** — a declaratively defined agent that combines
a model from the Foundry model catalog, instructions, and natural language prompts —
then lets you chat with it in an interactive terminal loop.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Terminal (you)                                     │
│                                                     │
│  $ python create_agent.py   ← run once              │
│  $ python chat.py           ← interactive loop      │
└────────────┬────────────────────────────────────────┘
             │  Azure Identity (DefaultAzureCredential)
             ▼
┌─────────────────────────────────────────────────────┐
│  Microsoft Foundry Project                          │
│                                                     │
│  ┌───────────────┐     ┌──────────────────────┐     │
│  │ Prompt Agent  │◄────│ PromptAgentDefinition│     │
│  │ (named, ver.) │     │  • model: gpt-4o-mini│     │
│  └───────┬───────┘     │  • instructions      │     │
│          │             └──────────────────────┘     │
│          ▼                                          │
│  ┌───────────────┐                                  │
│  │ Conversation  │  ← multi-turn history maintained │
│  │ (responses)   │                                  │
│  └───────────────┘                                  │
└─────────────────────────────────────────────────────┘
```

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Prompt Agent** | A named, versioned agent definition stored in Foundry Agent Service. Combines a model + instructions. |
| **PromptAgentDefinition** | The Python object that declares model, instructions, and (optionally) tools for the agent. |
| **Conversation** | A server-side session that maintains message history across multiple turns. |
| **Responses API** | The OpenAI-compatible API used to send user input and receive agent output within a conversation. |
| **DefaultAzureCredential** | Automatically picks up credentials from `az login`, managed identity, or environment variables. |

## Files

Shared files at the repo root (`my-agent-samples/`):

| File | Purpose |
|------|---------|
| `requirements.txt` | Python dependencies (shared across all demos) |
| `.env.sample` | Template for required environment variables |
| `.gitignore` | Ignore `.env`, `__pycache__`, `.venv` |

Demo-specific files (`hello-demo/`):

| File | Purpose |
|------|---------|
| `create_agent.py` | Creates/updates the prompt agent (run once) |
| `chat.py` | Interactive CLI chat loop (the main demo experience) |
| `README.md` | Setup instructions and walkthrough |
| `specs.md` | This specification |

## Demo Flow

### Step 1: Create the agent (run once)

```
$ python create_agent.py
✓ Agent "MyAgent" created (id: asst_abc123, version: 1)
```

### Step 2: Chat interactively

```
$ python chat.py
Connected to Microsoft Foundry. Conversation started.
Type your message (or "exit" to quit).

You: What is the largest ocean?
Agent: The Pacific Ocean is the largest and deepest ocean on Earth,
       covering more than 60 million square miles.

You: How deep is it?
Agent: The Pacific Ocean reaches a maximum depth of about 36,161 feet
       (11,022 meters) at the Mariana Trench.

You: exit
Goodbye!
```

The follow-up question ("How deep is it?") works because the conversation
maintains history — the agent knows "it" refers to the Pacific Ocean.

## Design Decisions

1. **Two scripts** — `create_agent.py` (lifecycle) and `chat.py` (runtime) separate concerns for clarity.
2. **Interactive loop** — feels like a real chatbot; demonstrates multi-turn naturally.
3. **Model: `gpt-4o-mini`** — widely available and cost-effective. Easy to swap.
4. **`python-dotenv`** — loads `.env` automatically so users don't have to export vars manually.
5. **No advanced tools** — no file search, code interpreter, or MCP. Focused on the core prompt agent concept.
6. **Scope excludes** streaming, hosted deployment, and tool use — those are follow-up exercises.

## Prerequisites

- Python 3.9+
- Azure subscription with a Microsoft Foundry project
- A deployed model (e.g., `gpt-4o-mini`) in the Foundry model catalog
- Azure CLI installed and authenticated (`az login`)

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PROJECT_ENDPOINT` | Your Foundry project endpoint URL | `https://myresource.ai.azure.com/api/projects/myproject` |
| `AGENT_NAME` | Name for your agent | `MyAgent` |
