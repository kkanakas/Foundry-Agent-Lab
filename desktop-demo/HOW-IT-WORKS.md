# How It Works: Desktop Demo

## Architecture

```
┌──────────────────────────────┐       ┌──────────────────────┐
│  Desktop Window (tkinter)    │       │  Azure AI Foundry     │
│                              │       │                       │
│  ┌────────────────────────┐  │       │  ┌─────────────────┐  │
│  │  ScrolledText (chat)   │  │       │  │  Prompt Agent   │  │
│  │  - System: Connected   │  │       │  │  (Desktop)      │  │
│  │  - You: Hello!         │  │       │  └────────┬────────┘  │
│  │  - Agent: Hi there!    │  │       │           │           │
│  └────────────────────────┘  │       │  ┌────────▼────────┐  │
│                              │       │  │  model-router   │  │
│  ┌──────────────────┐ ┌───┐  │       │  └─────────────────┘  │
│  │  Entry (input)   │ │Snd│  │       │                       │
│  └──────────────────┘ └───┘  │       │                       │
│         │                    │       │                       │
│         ▼                    │       │                       │
│  ┌─────────────────────┐     │       │                       │
│  │  Background Thread   │────┼──────►│                       │
│  │  (API call)          │◄───┼───────│                       │
│  └──────────┬───────────┘    │       │                       │
│             │ root.after(0)  │       │                       │
│             ▼                │       │                       │
│  UI update (main thread)     │       │                       │
└──────────────────────────────┘       └──────────────────────┘
```

## Flow (step by step)

```
1. create_agent.py
   │
   └─ Identical to Demo 0 (registers a basic prompt agent)

2. chat.py — GUI version
   │
   ├─ Create tkinter root window (600x500)
   ├─ Build UI: ScrolledText + Entry + Button
   ├─ Authenticate + create conversation (same as Demo 0)
   │
   └─ Event loop:
       ├─ User types message, presses Enter or clicks Send
       ├─ on_send():
       │   ├─ Display user message in chat
       │   ├─ Disable input (prevent double-send)
       │   └─ Spawn background thread → get_response()
       │
       ├─ get_response() [background thread]:
       │   ├─ openai.responses.create(...)
       │   └─ root.after(0, append_message) → schedule UI update
       │
       └─ UI update [main thread]:
           ├─ Display agent response
           └─ Re-enable input
```

## Code Flow

### chat.py — background thread pattern

```python
def on_send(self, event=None):
    # Run API call in background thread to keep UI responsive
    threading.Thread(target=self.get_response, args=(user_input,), daemon=True).start()

def get_response(self, user_input):
    response = openai.responses.create(
        input=user_input, conversation=conversation.id, ...
    )
    # Schedule UI update on main thread (tkinter is not thread-safe)
    root.after(0, self.append_message, "Agent", response.output_text)
```

## Key Concepts

### Why Threading?
Tkinter runs on a single thread. If you make an API call on the main thread,
the window freezes until it returns. The background thread keeps the UI
responsive while waiting for Azure.

### root.after(0, callback)
You can't update tkinter widgets from a background thread. `root.after(0, ...)`
schedules the update to run on the main thread's event loop — safe and clean.

### Same Agent, Different UI
The agent itself is identical to Demo 0. Only the presentation layer changed.
This shows that the agent is independent of how you choose to interact with it.
