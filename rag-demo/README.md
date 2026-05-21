# Demo 5: RAG Demo (File Search / Retrieval Augmented Generation)

An agent grounded in YOUR documents. It searches uploaded files to answer
questions accurately — no hallucination, only facts from the source.

## Quick Start

```cmd
az login                            (once per session)
5-rag-demo              (from repo root)
```

## Files

| File | Purpose |
|------|---------|
| `create_agent.py` | Uploads document, creates vector store, registers agent |
| `chat.py` | Chat loop (file search is server-side) |
| `data/employee-handbook.md` | Sample document (Contoso Electronics HR handbook) |
| `demo.bat` | Activates venv, runs both scripts |
| `reset.bat` | Deletes agent AND vector store |

## What's New (vs Demos 3-4)

- **File Search** — yet another built-in tool, grounded in YOUR data
- **Vector store** — documents are chunked, embedded, and indexed for search
- **RAG pattern** — Retrieval Augmented Generation: search first, then answer
- **Grounding** — agent only answers from document content, not general knowledge

## What This Demonstrates

- Uploading files and creating vector stores via SDK
- `FileSearchTool` with vector store references
- Agent grounded in private/proprietary data
- The RAG pattern: retrieve relevant chunks → generate accurate answer
- Agent refusing to answer when info isn't in the documents

## Configuration

| Variable | Purpose | Default |
|----------|---------|---------|
| `PROJECT_ENDPOINT` | Your Foundry project endpoint | (required) |
| `AGENT_NAME` | Name for the agent | `RAG-Agent` |
| `MODEL_DEPLOYMENT` | Model to use | `model-router` |

## Customization

Replace `data/employee-handbook.md` with your own documents to build
a custom knowledge base. Supported formats: .md, .txt, .pdf, .docx, .json.
