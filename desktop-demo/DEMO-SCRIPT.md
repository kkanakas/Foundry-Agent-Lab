# Demo Script: Desktop Demo

## Setup (before audience arrives)

1. Open cmd at the repo root (`foundry-agent-lab`)
2. Run `az login` once
3. Make sure your display is visible to the audience (projector/screen share)

## Talking Points

### Opening (30 sec)
> "Same agent as before, but now with a desktop window.
> Zero extra dependencies — tkinter is built into Python.
> About 50 lines of UI code on top of what we already had."

### Show the code (1 min)
- Open `chat.py` — point out:
  - `ChatWindow` class — ScrolledText + Entry + Button
  - `threading.Thread` — keeps window responsive
  - `root.after(0, ...)` — safely updates UI from background thread
  - `on_close()` — deletes agent when window closes
- "The agent code is identical to Demo 0 — we just changed the presentation."

### Run it (2 min)
```cmd
2-desktop-demo
```

A window pops up. Chat in it.

### Suggested prompts
1. "Hello! What can you help me with?" (basic test)
2. "Tell me a joke." (shows agent personality)
3. "Explain it to me like I'm five." (multi-turn context)

### Key observations to call out
> "The window stays responsive while waiting for a reply — that's the
> threading at work. No spinning cursor."

> "Type 'exit' and it closes cleanly — agent gets deleted just like the
> CLI version."

### Close
Type `exit` or click the X button.

## If something goes wrong

**Window doesn't appear**: Make sure you're not in a headless/remote session.

**Agent leftover from previous run**:
```cmd
desktop-demo\reset.bat
```

## Duration
~3 minutes total
