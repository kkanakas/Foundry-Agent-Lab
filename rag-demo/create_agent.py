"""
create_agent.py — Create a prompt agent with file search (RAG).

The agent can search through uploaded documents to answer questions
grounded in YOUR data. This demonstrates Retrieval Augmented Generation.

This script:
1. Uploads every file directly in data/, exporting Excel workbooks as text
2. Creates a vector store containing all discovered documents
3. Creates an agent with FileSearchTool pointing to that vector store

Prerequisites:
  1. From repo root: pip install -r requirements.txt
  2. az login
  3. Copy .env.sample to .env in this folder and fill in your values
"""

import csv
import json
import os
import sys
from io import StringIO
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))
import _tee  # noqa: E402 - activates LOG_FILE output capture

from dotenv import load_dotenv
from openpyxl import load_workbook
from pathlib import Path


def workbook_text(document: Path) -> bytes:
    """Export worksheet names and cell values without changing the workbook."""
    workbook = load_workbook(document, read_only=True, data_only=False)
    try:
        text = StringIO()
        writer = csv.writer(text, delimiter="\t")
        for sheet in workbook.worksheets:
            writer.writerow([f"Worksheet: {sheet.title}"])
            writer.writerows(sheet.iter_rows(values_only=True))
            writer.writerow([])
        return text.getvalue().encode("utf-8")
    finally:
        workbook.close()


# ---------------------------------------------------------------------------
# 1. Load environment variables
# ---------------------------------------------------------------------------
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path, override=True)

PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
AGENT_NAME = os.environ.get("AGENT_NAME", "RAG-Agent")
MODEL_DEPLOYMENT = os.environ.get("MODEL_DEPLOYMENT", "model-router")

if not PROJECT_ENDPOINT:
    print("ERROR: PROJECT_ENDPOINT is not set.")
    print("Copy .env.sample to .env in this folder and fill in your Foundry project endpoint.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 2. Authenticate with Azure
# ---------------------------------------------------------------------------
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()

# ---------------------------------------------------------------------------
# 3. Create the AI Project client and OpenAI client
# ---------------------------------------------------------------------------
from azure.ai.projects import AIProjectClient

project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=credential,
)
openai = project.get_openai_client()

# ---------------------------------------------------------------------------
# 4. Upload documents and create vector store
# ---------------------------------------------------------------------------
data_dir = Path(__file__).resolve().parent / "data"
documents = sorted(document for document in data_dir.iterdir() if document.is_file())
if not documents:
    raise FileNotFoundError(f"No documents found in: {data_dir}")

print("Creating vector store...")
vector_store = openai.vector_stores.create(name="employee-handbook-store, Foundry details and Excel data")

vs_id_file = Path(__file__).resolve().parent / ".vector_store_id"
vs_id_file.write_text(vector_store.id, encoding="utf-8")
manifest_file = Path(__file__).resolve().parent / ".vector_store_files.json"
document_records: list[dict[str, str]] = []
manifest = {"vector_store_id": vector_store.id, "documents": document_records}
manifest_file.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

for document in documents:
    print(f"Uploading {document.name}...")
    if document.suffix.lower() == ".xlsx":
        # File search needs a text export rather than the binary Excel workbook.
        uploaded_name = document.stem + ".txt"
        vector_store_file = openai.vector_stores.files.upload_and_poll(
            vector_store_id=vector_store.id,
            file=(uploaded_name, workbook_text(document), "text/plain"),
        )
    else:
        uploaded_name = document.name
        with document.open("rb") as file_handle:
            vector_store_file = openai.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store.id,
                file=file_handle,
            )
    document_records.append({
        "source": document.name,
        "uploaded_name": uploaded_name,
        "file_id": vector_store_file.id,
        "status": vector_store_file.status,
    })
    manifest_file.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if vector_store_file.status != "completed":
        raise RuntimeError(
            f"Indexing failed for {document.name}: "
            f"status={vector_store_file.status}, error={vector_store_file.last_error}"
        )
    print(f"  ✓ Indexed {document.name} (file ID: {vector_store_file.id})")
print(f"  ✓ Vector store created: {vector_store.id}")

# ---------------------------------------------------------------------------
# 5. Create agent with file search tool
# ---------------------------------------------------------------------------
from azure.ai.projects.models import PromptAgentDefinition, FileSearchTool

agent = project.agents.create_version(
    agent_name=AGENT_NAME,
    definition=PromptAgentDefinition(
        model=MODEL_DEPLOYMENT,
        instructions=(
            "You are an HR assistant, Sales Analyst and a Foundry expert for Contoso Electronics. "
            "Answer employee questions using ONLY the information in the uploaded documents. "
            "If the answer isn't in the documents, say so clearly. "
            "Always be specific — cite numbers, dates, and policies exactly."
        ),
        tools=[FileSearchTool(vector_store_ids=[vector_store.id])],
    ),
)

# ---------------------------------------------------------------------------
# 6. Confirm success
# ---------------------------------------------------------------------------
print(f"\n✓ Agent \"{agent.name}\" created")
print(f"  Model: {MODEL_DEPLOYMENT}")
print(f"  Tools: file_search (vector store: {vector_store.id})")
print(f"  Documents: {', '.join(document.name for document in documents)}")
print(f"  Document IDs saved to: {manifest_file.name}")
_tee.console_only(f"  Endpoint: {PROJECT_ENDPOINT}")
print()
