# Demo Script: Hello Demo

## Setup (before audience arrives)

1. Open cmd at the repo root (`foundry-agent-lab`)
2. Run `az login` once
3. Verify: `az account show` (should show your subscription)

## Talking Points

### Opening (30 sec)
> "This is the simplest possible AI agent — just a prompt agent that chats.
> Two files: one to create it, one to talk to it."

### Show the code (1 min)
- Open `create_agent.py` — point out:
  - `PromptAgentDefinition` (model + instructions)
  - `create_version()` — registers in Foundry
- Open `chat.py` — point out:
  - `conversations.create()` — server-side session
  - `responses.create()` with `agent_reference` — routes to our agent
  - Multi-turn: conversation remembers context

### Run it (2 min)
```cmd
0-hello-demo
```

### Suggested prompts
1. "What is the capital of France?" (simple test)
2. "Tell me 3 fun facts about it." (tests multi-turn — "it" = France)
3. "Summarize what we talked about." (proves conversation history works)

### Key observation to call out
> "Notice the follow-up 'Tell me about it' works without saying 'France' again.
> That's the server-side conversation — the agent remembers."

### Point out the model
> "See `[model: gpt-5.4-mini...]` — that's model-router picking the best
> available model automatically."

### Exit
Type `exit` — note the agent gets deleted (clean demo).

## If something goes wrong
```cmd
hello-demo\reset.bat
```
Then re-run the demo.

## Duration
~3-4 minutes total
