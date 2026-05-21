# Demo Script: Hosted Demo

## Setup (before audience arrives)

1. Open terminal at `c:\Work\repos\foundry-agent-lab`
2. Run `az login` once
3. Verify: `az account show` (should show your subscription)
4. Ensure `.env` has your Azure OpenAI endpoint and model deployment
5. Install dependencies: `pip install -r hosted-demo/requirements.txt`

## Talking Points

### Opening (30 sec)
> "So far every demo ran agents in Foundry's cloud.
> This one flips it — we host the agent ourselves, using the Responses protocol.
> Same streaming, same multi-turn conversations, but running on YOUR infrastructure."

### Show the code (1 min)
- Open `main.py` — point out:
  - `ResponsesAgentServerHost` — the agent server framework
  - `@app.response_handler` — how you define the handler
  - `context.get_history()` — conversation state via `previous_response_id`
  - `_openai_client.responses.create(stream=True)` — streaming from Azure OpenAI
  - `TextResponse` — yields tokens back to the caller as SSE events
- Open `agent.yaml` — point out:
  - `kind: hosted` — declares this is a hosted agent
  - `protocols: responses` — uses the Responses protocol

### Run it locally (2 min)
```cmd
8-hosted-demo
```

> "The agent starts on port 8088. Let's test it with Agent Inspector."

### Test in Agent Inspector
1. Open Command Palette → **AI Toolkit: Open Agent Inspector**
2. Connect to `http://localhost:8088`

#### Turn 1 — Start conversation
```
Hello, my name is Alice!
```

#### Turn 2 — Test multi-turn memory
```
What is my name?
```

> "It remembers Alice — the platform chains responses via `previous_response_id` automatically."

### Deploy to the cloud (2 min)
1. Open Command Palette → **Microsoft Foundry: Deploy Hosted Agent**
2. Walk through the prompts (agent name, Dockerfile, registry, resource size)

> "That's it — the same code, same protocol, now running in Foundry's container hosting.
> No Kubernetes, no Docker Compose, no ingress configuration."

### Key observation to call out
> "Unlike Demos 0–7 where Foundry runs the agent logic for us, here WE own the
> agent code and deployment. The protocol stays the same — callers can't tell
> the difference."

## If something goes wrong

| Problem | Fix |
|---------|-----|
| Port 8088 already in use | Kill the previous process or change the port |
| `ModuleNotFoundError` | Run `pip install -r hosted-demo/requirements.txt` |
| Azure OpenAI 401 | Re-run `az login` or check RBAC roles |
| `model-router` unsupported error | Use a specific deployment like `gpt-4.1-mini` |
| Deploy command not found | Install the AI Toolkit / Foundry extension |

## Duration
~4-5 minutes total (local only), ~7-8 minutes with cloud deployment
