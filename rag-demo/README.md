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
| `create_agent.py` | Uploads every file directly in `data/`, creates one vector store, registers agent |
| `chat.py` | Chat loop (file search is server-side) |
| `data/employee-handbook.md` | Sample document (Contoso Electronics HR handbook) |
| `data/Foundry-Overview.pdf` | Foundry reference document |
| `data/Demo_Excel_File.xlsx` | Workbook exported as UTF-8 text for file search |
| `.vector_store_id` | Shared vector store ID, used by cleanup |
| `.vector_store_files.json` | Shared vector store ID and each document's source, uploaded name, file ID, and indexing status |
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

Install dependencies from the repository root with
`python -m pip install -r requirements.txt`, then run
`python rag-demo/create_agent.py`.

The script automatically discovers every file directly in `data/` and uploads
them in filename order into one shared vector store. Subdirectories are not
traversed. An empty or missing data folder causes an error before a store is created.
Excel (`.xlsx`, case-insensitive) is exported in memory to tab-separated `.txt`, including every
worksheet's name and rows; the original workbook is unchanged. Formula cells
retain their formula expressions rather than calculating results. Charts, images,
and formatting are not included.

Add or remove files in `data/` to change the knowledge base; no code edits are
needed. Other files are uploaded unchanged and must use a format supported by
Foundry file search, such as .md, .txt, .pdf, .docx, or .json. Unsupported files
cause an upload or indexing error rather than being silently skipped.

The generated `.vector_store_files.json` records each uploaded file ID separately
from the shared vector store ID. IDs are saved as uploads finish, including failed
indexing statuses, so partial progress remains available if a later step fails.
The agent is registered only after all discovered documents finish indexing successfully.
Running the script again creates a new store and replaces the local ID files;
use the reset script first if you want to remove the previous store.
