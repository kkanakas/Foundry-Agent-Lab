# How It Works: WebSearch Demo

## Architecture

```
┌─────────────┐         ┌──────────────────────────────────┐
│  Your       │         │  Azure AI Foundry                 │
│  Terminal   │         │                                   │
│             │         │  ┌─────────────────┐              │
│  chat.py ───┼────────►│  │  Search-Agent   │              │
│             │         │  └────────┬────────┘              │
│             │         │           │                       │
│             │         │           ▼ (agent decides)       │
│             │         │  ┌─────────────────┐              │
│             │         │  │  Web Search     │──► Internet  │
│             │         │  │  (built-in)     │◄── results   │
│             │         │  └────────┬────────┘              │
│             │         │           │                       │
│             │         │           ▼                       │
│         ◄───┼─────────┼── final answer + citations        │
└─────────────┘         └──────────────────────────────────┘
```

## Comparison: Built-in vs Function Calling

```
FUNCTION CALLING (Demo 1)          WEB SEARCH (Demo 3)
─────────────────────────          ────────────────────
1. Send message                    1. Send message
2. Get function_call response      2. Get final answer (done!)
3. Execute function locally
4. Send result back
5. Get final answer

Your code: ~40 lines of loop       Your code: 0 extra lines
Tool runs: on YOUR machine         Tool runs: on Foundry servers
```

## Flow (step by step)

```
1. create_agent.py
   │
   ├─ Same as Demo 0, PLUS:
   └─ tools=[WebSearchTool()]
       → That's it. One line. Foundry handles the rest.

2. chat.py
   │
   ├─ User: "What's the latest news on AI?"
   │
   ├─ openai.responses.create(input=user_message)
   │   → Agent sees the question
   │   → Agent decides: "I need current info, let me search"
   │   → Foundry executes web search SERVER-SIDE
   │   → Agent reads results, composes answer with citations
   │   → Returns: final text with source references
   │
   └─ Print response (citations included in text)
       → No tool loop. No function execution. Just print.
```

## Code Flow

### create_agent.py

```python
# One line enables server-side web search — no client code needed
agent = project.agents.create_version(
    agent_name=AGENT_NAME,
    definition=PromptAgentDefinition(model=MODEL_DEPLOYMENT, tools=[WebSearchTool()], ...),
)
```

### chat.py — extracting URL citations

```python
response = openai.responses.create(input=user_input, conversation=conversation.id, ...)
print(response.output_text)

# Citations are in annotations on the output message
for item in response.output:
    for content in getattr(item, "content", []) or []:
        for ann in getattr(content, "annotations", []) or []:
            if getattr(ann, "type", None) == "url_citation":
                print(f"  🔗 {ann.url} ({ann.title})")
```

## Key Concepts

### Server-Side vs Client-Side Tools
- **Built-in tools** (web search, code interpreter, file search):
  Foundry runs them. You just enable them. Zero client code.
- **Function tools** (Demo 1):
  YOU run them. You write the execution loop. Full control.

### When the Agent Searches
The agent decides whether to search based on the question:
- "What's 2+2?" → No search (general knowledge)
- "Who won the game last night?" → Searches (needs current info)
- "Summarize the latest AI news" → Searches (needs real-time data)

### Citations
Web search responses include source URLs inline. The agent attributes
where information came from — useful for fact-checking and trust.
