# Demo Script: WebSearch Demo

## Setup (before audience arrives)

1. Open cmd at the repo root (`foundry-agent-lab`)
2. Run `az login` once

## Talking Points

### Opening (30 sec)
> "Demo 1 showed function calling — we wrote the tool loop ourselves.
> Now I'll show a BUILT-IN tool: web search. One line of code, and the
> agent can search the entire internet."

### Show the code (1 min)
- Open `create_agent.py` — point out:
  - `tools=[WebSearchTool()]` — that's the ENTIRE tool setup
  - "Compare this to Demo 1 where we defined parameters, wrote execution code..."
- Open `chat.py` — point out:
  - "Notice: NO tool-calling loop. No function detection. No sending results back."
  - "The search happens server-side. We just send a message and get an answer."

### Run it (3 min)
```cmd
3-websearch-demo
```

### Suggested prompts (in this order!)
1. "What's the capital of France?" (no search — proves it knows when NOT to search)
2. "What happened in AI news this week?" (triggers search — real-time data)
3. "Tell me more about the first result." (multi-turn + search context)

### Key observations to call out
> "Notice the citations in the response — the agent tells you WHERE it got
> the information. That's trust and verifiability built in."

> "On question 1, it didn't search — it already knows capitals. The agent
> is smart about WHEN to use its tools."

> "Compare the code to Demo 1: we went from ~40 lines of tool handling
> to zero. That's the power of built-in tools."

### Exit
Type `exit` — agent deleted.

## If something goes wrong

```cmd
websearch-demo\reset.bat
```

## Duration
~4 minutes total
