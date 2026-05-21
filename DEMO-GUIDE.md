# Demo Guide — Best Practices for Presenting

How to get the most out of this demo set, whether you have 10 minutes
or a full hour.

---

## Before You Start

### One-time prep (the day before)

1. Run through every demo you plan to show, start to finish
2. Verify `az login` works and your subscription is active
3. Confirm the model deployment is responding (run Demo 0 once)
4. If showing Demo 5, check that the vector store creates without errors
5. Close unrelated browser tabs, notifications, and chat apps

### Right before the audience

1. Open **one** cmd window at the repo root (`foundry-agent-lab`)
2. Run `az login` — do NOT wait for the audience to watch this
3. Have each demo folder's `DEMO-SCRIPT.md` open in a side tab for reference
4. Set terminal font size large enough for the back row (16 pt+)
5. Optional: open the source files you plan to walk through in VS Code

---

## Recommended Demo Order

Always present in numeric order. Each demo builds on vocabulary and
concepts introduced by the previous one.

| Demo | Include when… | Skip when… |
|------|---------------|------------|
| 0 — Hello | Always. Sets the mental model. | Never skip this. |
| 1 — Tools | Always. Function calling is the #1 enterprise use case. | Never skip this. |
| 2 — Desktop | You want to show the agent isn't tied to a terminal | Short on time and Demo 4 covers the UI point |
| 3 — Web Search | You want to show built-in tools with zero client code | Audience already understands built-in tools |
| 4 — Code | You want a "wow" moment with live code + web UI | Audience is non-technical and won't appreciate code |
| 5 — RAG | You want to show enterprise grounding / no hallucination | You have no time left (this is the longest setup) |
| 6 — MCP | You want to show open ecosystem / human-in-the-loop approval | No MCP connection configured or audience is non-technical |
| 7 — Toolbox | You want to show centralized governance / curated tool subsets | No toolbox configured or audience doesn't need enterprise story |
| 8 — Hosted | You want to show self-hosting / bring-your-own-server / deployment to Foundry containers | Audience doesn't need to understand hosting options |

### Suggested combos

| Time budget | Demos | Flow |
|-------------|-------|------|
| 10 min | 0 → 1 | Core concepts: agent + tool calling |
| 20 min | 0 → 1 → 5 | Core + enterprise RAG story |
| 30 min | 0 → 1 → 3 → 5 | Built-in vs function tools + RAG |
| 45 min | 0 → 1 → 3 → 5 → 6 | Tools progression: custom → built-in → ecosystem |
| 60 min | 0 → 1 → 2 → 3 → 4 → 5 | Full arc with all UX modes |
| 75 min | 0 → 1 → 2 → 3 → 4 → 5 → 6 | Everything including MCP |
| 90 min | 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 | Full arc + enterprise toolbox governance |
| 105 min | 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 | Full arc + self-hosted deployment |

---

## Presentation Tips

### Pacing

- **Show code first, then run.** Audiences retain more when they see
  the 10 lines of code before the magic happens.
- **Pause after the first agent response.** Let it land. Then explain
  what happened behind the scenes.
- **Use the suggested prompts in each DEMO-SCRIPT.md.** They are
  sequenced to build on each other and highlight specific capabilities.
- **Ask "what should I ask it?"** mid-demo to involve the audience —
  but have a backup prompt ready in case of silence.

### Narration

- Point out what **didn't** happen as much as what did:
  - Demo 1: "The tool did NOT fire for the Hamlet question."
  - Demo 5: "It refused to answer the stock price question — it's grounded."
- Use the transition between demos to reinforce the progression:
  - 0→1: "Same agent, but now it can DO things."
  - 1→2: "Same agent, different window."
  - 2→3: "Now the tool runs on the SERVER, not our code."
  - 3→4: "Server-side tool again, but now it writes and runs code."
  - 4→5: "Instead of the web, it searches YOUR documents."
  - 5→6: "Now instead of Azure's tools, we connect to ANY tool server via MCP."
  - 6→7: "Same MCP tools, but now curated and governed centrally in a Toolbox."
  - 7→8: "Now instead of Foundry running our agent, WE host it — same protocol, our infrastructure."

### Technical depth

- **For developers:** show `create_agent.py` and `chat.py` side by side.
  Highlight that each demo adds only a few lines.
- **For decision-makers:** minimize code, maximize the chat experience.
  Focus on what the agent can do, not how it's wired.
- **For mixed audiences:** show code briefly ("here's the 10 lines"),
  then spend time on the live interaction.

---

## Logging for Artifacts

Append `log` to any demo command to capture the full session:

```cmd
0-hello-demo log
1-tools-demo log
```

Each creates a `chat-log.txt` inside the demo folder. Use these for:
- Pasting into slide decks as "live demo" screenshots
- Post-demo write-ups and documentation
- Sharing transcripts with attendees who missed the session

---

## Recovery

Things will go wrong in live demos. Here's how to recover fast.

| Problem | Fix |
|---------|-----|
| Agent already exists (name conflict) | `<folder>\reset.bat` then re-run |
| Azure auth expired mid-demo | `az login` in the same terminal, re-run |
| Weather API slow (Demo 1) | Say "real APIs have real latency" — wait 10 sec |
| Gradio port in use (Demo 4) | `Ctrl+C`, wait 5 sec, re-run |
| Vector store creation slow (Demo 5) | Normal on first run — takes 15-30 sec |
| Python error on launch | Check `.env` exists in that demo folder |
| Hosted agent port 8088 in use | Kill the previous `python main.py` process |
| Audience asks about cost | "Model-router picks the cheapest capable model. These demos cost fractions of a cent per run." |

### The nuclear option

If everything breaks, reset all demos:

```cmd
for %d in (hello-demo tools-demo desktop-demo websearch-demo code-demo rag-demo mcp-demo toolbox-demo) do %d\reset.bat
```

Then start fresh from Demo 0.

---

## Key Messages to Land

Regardless of which demos you show, drive home these points:

1. **Agents are simple** — each one is ~20 lines of Python, not a framework
2. **Tools make agents useful** — function calling is how agents interact with the real world
3. **Built-in tools save work** — web search, code interpreter, and file search are one line each
4. **The UX is your choice** — same agent works in terminal, desktop, or web
5. **Grounding prevents hallucination** — RAG lets you trust the agent's answers
6. **MCP opens the ecosystem** — connect to any tool server using an open standard, with human-in-the-loop approval
7. **Toolbox enables governance** — platform teams curate which tools agents get, versioned and centrally managed
8. **Self-hosting gives control** — bring your own server, same protocol, deploy anywhere (your infra or Foundry containers)
9. **Azure handles the hard parts** — conversation memory, tool execution, vector search are all server-side
