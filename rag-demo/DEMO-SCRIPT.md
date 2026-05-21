# Demo Script: RAG Demo

## Setup (before audience arrives)

1. Open cmd at the repo root (`foundry-agent-lab`)
2. Run `az login` once
3. Optionally open `rag-demo\data\employee-handbook.md` to show the source

## Talking Points

### Opening (30 sec)
> "This is RAG — Retrieval Augmented Generation. The agent searches
> through YOUR documents before answering. It only says what's in
> the source. No hallucination."

### Show the source document (30 sec)
- Open `data/employee-handbook.md`
- "This is a fake employee handbook for Contoso Electronics. PTO policies,
  benefits, travel rules. The agent will ONLY answer from this."

### Show the code (1.5 min)
- Open `create_agent.py` — point out:
  - `files.upload()` — sends document to Foundry
  - `vector_stores.create()` — chunks, embeds, indexes the doc
  - `FileSearchTool(vector_store_ids=[...])` — connects agent to the store
  - "Three API calls to go from a file on disk to a searchable knowledge base"
- Open `chat.py` — point out:
  - "Same simple loop as web search. File search is also server-side."

### Run it (4 min)
```cmd
5-rag-demo
```

### Suggested prompts (in this order!)
1. "How many PTO days do new employees get?" (factual — in the doc)
2. "What's the 401k match?" (specific numbers — proves grounding)
3. "Can I work from home 5 days a week?" (policy question — answer is "up to 3")
4. "What's the company's stock price?" (NOT in the doc — should refuse)
5. "Summarize the travel policy." (multi-fact extraction)

### Key observations to call out
> "Notice on question 4, the agent said 'I don't have that information.'
> It COULD have guessed or searched the web — but it's grounded. It only
> uses the handbook."

> "The numbers are exact — '15 days', '6% match', '$200/night'.
> It's reading from the document, not generating from memory."

> "This is how enterprises use AI safely: ground it in YOUR data,
> and it can't make things up."

### Exit
Type `exit` — agent deleted. Run `reset.bat` to also delete the vector store.

## If something goes wrong

```cmd
rag-demo\reset.bat
```
This deletes both the agent AND the vector store (full cleanup).

## Duration
~5-6 minutes total
