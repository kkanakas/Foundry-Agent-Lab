# Demo Script: Tools Demo

## Setup (before audience arrives)

1. Open cmd at the repo root (`foundry-agent-lab`)
2. Run `az login` once
3. Optionally verify weather API works: open `https://wttr.in/Seattle?format=j1` in browser

## Talking Points

### Opening (30 sec)
> "Now we give our agent a superpower — it can call a real weather API.
> The model decides WHEN to use the tool. Our code executes it locally."

### Show the code (2 min)
- Open `create_agent.py` — point out:
  - `FunctionTool(name="get_weather", parameters={...})`
  - "This is a JSON Schema describing what the function accepts"
  - `strict=True` — model must produce valid JSON
- Open `chat.py` — point out:
  - The tool-calling loop: detect → execute → send back
  - `🔧 Tool called:` print line — "this is how you'll SEE it fire"
  - `FunctionCallOutput` — the official way to return results

### Run it (3 min)
```cmd
1-tools-demo
```

### Suggested prompts (in this order!)
1. "Who wrote Hamlet?" (no tool needed — proves agent is smart enough to skip it)
2. "What's the weather in Seattle today?" (triggers the tool — watch the 🔧 line)
3. "How about Tokyo?" (multi-turn + tool — proves context + tools work together)
4. "Compare the two cities' weather." (uses conversation history of both results)

### Key observations to call out
> "Watch the terminal — you'll see 🔧 when the tool fires. The model didn't
> guess the weather. It asked our code to fetch it, and we hit a real API."

> "Notice on question 1, the tool did NOT fire. The model is smart enough
> to know it only needs the tool for weather questions."

> "The result is real — check your phone if you don't believe me!"

### Exit
Type `exit` — agent gets deleted.

## If something goes wrong

**Weather API timeout**: wttr.in is occasionally slow. Wait 10 seconds.
If it keeps failing, the error handler catches it gracefully.

**Agent leftover from previous run**:
```cmd
tools-demo\reset.bat
```

## Duration
~5 minutes total
