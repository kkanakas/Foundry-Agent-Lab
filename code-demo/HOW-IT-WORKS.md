# How It Works: Code Demo

## Architecture

```
┌───────────────────┐    ┌─────────────┐    ┌──────────────────────────────┐
│  Browser          │    │  Gradio     │    │  Azure AI Foundry             │
│  (localhost:7860) │◄──►│  Server     │    │                               │
│                   │    │  (chat.py)  │    │  ┌─────────────────┐          │
│  Chat UI          │    │      │      │    │  │  Code-Agent     │          │
│  - input box      │    │      │      │    │  └────────┬────────┘          │
│  - responses      │    │      ▼      │    │           │                   │
│  - examples       │    │  responses  │    │           ▼ (agent decides)   │
│                   │    │  .create()──┼───►│  ┌─────────────────────┐      │
│                   │    │      ◄──────┼────│  │  Code Interpreter   │      │
│                   │    │             │    │  │  (sandboxed Python) │      │
│                   │    │             │    │  │  - writes code      │      │
│                   │    │             │    │  │  - executes it      │      │
│                   │    │             │    │  │  - returns output   │      │
│                   │    │             │    │  └─────────────────────┘      │
└───────────────────┘    └─────────────┘    └──────────────────────────────┘
```

## Flow (step by step)

```
1. create_agent.py
   │
   └─ tools=[CodeInterpreterTool()]
       → Agent can now write and run Python in a sandbox

2. chat.py (Gradio web server)
   │
   ├─ Creates conversation
   ├─ Launches Gradio on localhost:7860
   │
   └─ For each user message:
       ├─ User: "Calculate the first 20 Fibonacci numbers"
       │
       ├─ openai.responses.create(input=user_message)
       │   → Agent decides: "I need to compute this"
       │   → Agent writes Python code:
       │     ```python
       │     fib = [0, 1]
       │     for i in range(18):
       │         fib.append(fib[-1] + fib[-2])
       │     print(fib)
       │     ```
       │   → Foundry executes code in sandbox
       │   → Agent formats result into natural language
       │   → Returns: complete answer with code shown
       │
       └─ Display in browser (formatted markdown)
```

## Code Flow

### create_agent.py

```python
# Enable server-side code execution in a sandbox
agent = project.agents.create_version(
    agent_name=AGENT_NAME,
    definition=PromptAgentDefinition(model=MODEL_DEPLOYMENT, tools=[CodeInterpreterTool()], ...),
)
```

### chat.py — extracting code blocks and generated files

```python
for item in response.output:
    if item.type == "code_interpreter_call":
        parts.append(f"```python\n{item.code}\n```")       # Show the code it ran
    elif item.type == "message":
        for content in item.content:
            parts.append(content.text)
            # Download generated images from sandbox
            for ann in content.annotations:
                if ann.type == "container_file_citation":
                    file_data = openai.containers.files.content.retrieve(
                        file_id=ann.file_id, container_id=ann.container_id
                    )
```

## Key Concepts

### Why Code Interpreter?
The model is great at language but unreliable at math. With code interpreter:
- "What's 1847 × 293?" → writes `print(1847 * 293)` → exact answer
- "Standard deviation of [...]" → uses numpy → precise result
- "Plot a chart" → uses matplotlib → generates image

### Sandboxed Execution
The code runs in Foundry's isolated environment:
- No access to your files or network
- Pre-installed packages: numpy, pandas, matplotlib, etc.
- Execution timeout (safe from infinite loops)
- Results returned as text or files

### Gradio vs Tkinter vs CLI
| | CLI | Tkinter | Gradio |
|---|-----|---------|--------|
| Dependencies | None | None (built-in) | `pip install gradio` |
| Code complexity | Lowest | Medium | Low |
| Visual quality | Basic | Functional | Polished |
| Markdown/code rendering | No | No | Yes ✓ |
| Image display | No | Possible | Yes ✓ |
| Sharing | Local only | Local only | Shareable link |

For code interpreter output (formatted code + potential images), Gradio wins.
