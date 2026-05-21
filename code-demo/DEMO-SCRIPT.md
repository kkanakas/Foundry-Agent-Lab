# Demo Script: Code Demo

## Setup (before audience arrives)

1. Open cmd at the repo root (`foundry-agent-lab`)
2. Run `az login` once
3. Verify gradio is installed: `pip show gradio`

## Talking Points

### Opening (30 sec)
> "Code Interpreter lets the agent WRITE and RUN Python code.
> It's another built-in tool — one line to enable. And this time,
> we're using a web UI powered by Gradio instead of a terminal."

### Show the code (1.5 min)
- Open `create_agent.py` — point out:
  - `tools=[CodeInterpreterTool()]` — one line, like web search
  - "The code runs in a sandboxed environment on Azure, not on my machine"
- Open `chat.py` — point out:
  - `gr.ChatInterface(fn=chat)` — entire web UI in one call
  - "Gradio handles the HTML, CSS, WebSocket... we just define the function"
  - "Compare: tkinter was 50+ lines. Gradio is 10 lines for a better UI."

### Run it (4 min)
```cmd
4-code-demo
```
Browser opens automatically.

### Suggested prompts (use the examples or type)
1. "What's 1847 × 293?" (simple math — proves it runs code, not guesses)
2. "Calculate the first 20 Fibonacci numbers and show them in a table." (code + formatting)
3. "What's the standard deviation of [23, 45, 12, 67, 34, 89, 56]?" (numpy)
4. "Create a bar chart comparing the populations of the top 5 most populous countries." (matplotlib)

### Key observations to call out
> "Notice it shows the CODE it wrote — you can verify it's correct.
> This isn't the model doing arithmetic in its head. It wrote Python
> and actually ran it."

> "For the chart question — it generates a matplotlib plot. The model
> knows the approximate populations and visualizes them."

> "We went from terminal to a web app by changing ~10 lines.
> Same agent, different presentation — just like Demo 2 (desktop)."

### Stop
Press `Ctrl+C` in the terminal. Agent persists until you `exit` or run `reset.bat`.

## If something goes wrong

**Gradio not installed**: `pip install gradio`

**Port 7860 in use**: Close other Gradio instances or add `demo.launch(server_port=7861)`

**Agent leftover**:
```cmd
code-demo\reset.bat
```

## Duration
~5 minutes total
