# How It Works: Hosted Demo

## Architecture

```
┌──────────────┐         ┌──────────────────────────┐         ┌──────────────────┐
│  Client      │         │  Your Agent Server       │         │  Azure OpenAI    │
│  (curl /     │  POST   │  (main.py on :8088)      │  HTTPS  │                  │
│  Inspector)  │────────►│                          │────────►│  gpt-4.1-mini    │
│              │◄────────│  ResponsesAgentServerHost│◄────────│  (streaming)     │
│              │   SSE   │                          │         │                  │
└──────────────┘         └──────────────────────────┘         └──────────────────┘
                                    │
                                    │ In-memory store
                                    │ (previous_response_id)
                                    ▼
                          ┌──────────────────┐
                          │  Conversation    │
                          │  History Store   │
                          └──────────────────┘
```

## Flow (step by step)

```
1. Client sends POST /responses
   │
   ├─ Body: { "input": "Hello!", "stream": true }
   └─ For follow-ups: includes "previous_response_id"

2. ResponsesAgentServerHost receives the request
   │
   ├─ Creates a ResponseContext
   ├─ Stores the input in the in-memory response store
   └─ Calls @app.response_handler

3. handle_create() runs
   │
   ├─ context.get_history() — fetches past turns via previous_response_id
   ├─ context.get_input_text() — gets the current user message
   ├─ _build_input() — assembles the full conversation into input items
   └─ Calls Azure OpenAI Responses API with stream=True

4. Streaming response
   │
   ├─ Azure OpenAI yields tokens as response.output_text.delta events
   ├─ TextResponse forwards each token as an SSE event to the client
   └─ On completion, the response is stored with an ID for chaining
```

## Code Flow

### main.py

```python
# Initialize the agent server with history support
app = ResponsesAgentServerHost(
    options=ResponsesServerOptions(default_fetch_history_count=20))

# Handle incoming requests
@app.response_handler
async def handle_create(request, context, cancellation_signal):
    async def stream_openai():
        history = await context.get_history()
        current_input = await context.get_input_text()
        input_items = _build_input(current_input, history)

        openai_stream = _openai_client.responses.create(
            model=AZURE_AI_MODEL_DEPLOYMENT_NAME,
            instructions=_SYSTEM_PROMPT,
            input=input_items,
            stream=True,
        )
        for event in openai_stream:
            if event.type == "response.output_text.delta":
                yield event.delta

    return TextResponse(context, request, text=stream_openai())
```

### agent.yaml

```yaml
kind: hosted
protocols:
  - protocol: responses
    version: 1.0.0
```

## Key Concepts

### Responses Protocol
The Responses protocol is the standard wire format for hosted agents in
Microsoft Foundry. It defines how clients send messages (`POST /responses`)
and receive streaming replies (SSE events). The protocol supports
multi-turn conversations via `previous_response_id` chaining.

### Self-Hosted vs. Platform-Hosted
In Demos 0–7, the agent logic runs inside Foundry's platform. Here, YOU
own the server — the same protocol is served from your own container.
This gives full control over dependencies, custom logic, and deployment
target (your AKS, Container Apps, or Foundry's container hosting).

### Conversation State (Server-Side)
The `ResponsesAgentServerHost` includes an in-memory response store.
Each response gets a unique ID; follow-up requests reference it via
`previous_response_id`. The host resolves the chain and passes full
history to your handler via `context.get_history()`.

### Streaming
Tokens flow from Azure OpenAI → your handler → the client with no
buffering. The client sees tokens appear in real time as SSE events
of type `response.output_text.delta`.

### Deployment to Foundry
Running `Microsoft Foundry: Deploy Hosted Agent` in VS Code:
1. Builds a container image from your Dockerfile
2. Pushes it to Azure Container Registry
3. Registers the agent version in Foundry
4. Assigns RBAC roles for Azure OpenAI access

The deployed agent is reachable through Foundry's standard agent
endpoint — callers use the same Responses protocol regardless of
whether the agent runs locally or in the cloud.
