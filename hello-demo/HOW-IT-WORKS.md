# How It Works: Hello Demo

## Architecture

```
┌─────────────┐         ┌──────────────────────┐
│  Your       │         │  Microsoft Foundry    │
│  Terminal   │         │                       │
│             │         │  ┌─────────────────┐  │
│  chat.py ───┼────────►│  │  Prompt Agent   │  │
│             │◄────────┼──│  (Hello-Agent)  │  │
│             │         │  └────────┬────────┘  │
│             │         │           │           │
│             │         │  ┌────────▼────────┐  │
│             │         │  │  model-router   │  │
│             │         │  │  (picks model)  │  │
│             │         │  └─────────────────┘  │
└─────────────┘         └──────────────────────┘
```

## Flow (step by step)

```
1. create_agent.py
   │
   ├─ Load .env (endpoint, model, agent name)
   ├─ Authenticate with DefaultAzureCredential
   ├─ Create AIProjectClient
   └─ Call project.agents.create_version()
       → Registers agent definition in Foundry
       → Returns agent ID and version

2. chat.py
   │
   ├─ Load .env, authenticate, create client
   ├─ openai.conversations.create()
   │   → Creates a server-side session (maintains history)
   │
   └─ Loop:
       ├─ Read user input
       ├─ openai.responses.create(input, conversation, agent_reference)
       │   → Sends message to agent within conversation
       │   → Agent uses conversation history for context
       │   → Returns response with model name
       ├─ Print response
       └─ On "exit": delete agent, break
```

## Code Flow

### create_agent.py

```python
# Register a prompt agent with a system instruction
agent = project.agents.create_version(
    agent_name=AGENT_NAME,
    definition=PromptAgentDefinition(
        model=MODEL_DEPLOYMENT,
        instructions="You are a helpful, friendly assistant...",
    ),
)
```

### chat.py

```python
# Create a server-side conversation (stores history)
conversation = openai.conversations.create()

# Send a message — agent sees full conversation history
response = openai.responses.create(
    input=user_input,
    conversation=conversation.id,
    extra_body={"agent_reference": {"name": AGENT_NAME, "type": "agent_reference"}},
)
print(response.output_text)
```

## Key Concepts

### Conversations
A conversation is a **server-side session** that stores message history.
The agent sees all previous messages automatically — you don't need to
resend the full chat history on each turn.

### Agent Versions
`create_version()` creates a new version each time. If the agent name
already exists, it gets a new version number. The latest version is
used by default when referenced by name.

### Model Router
When `MODEL_DEPLOYMENT=model-router`, Azure automatically picks the best
available model for each request. The `response.model` field tells you
which model actually responded.
