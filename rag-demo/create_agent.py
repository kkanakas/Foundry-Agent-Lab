"""
create_agent.py — Create a prompt agent with file search (RAG).

The agent can search through uploaded documents to answer questions
grounded in YOUR data. This demonstrates Retrieval Augmented Generation.

This script:
1. Uploads a sample document (employee handbook)
2. Creates a vector store from it
3. Creates an agent with FileSearchTool pointing to that vector store

Prerequisites:
  1. From repo root: pip install -r requirements.txt
  2. az login
  3. Copy .env.sample to .env in this folder and fill in your values
"""

import os
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))
import _tee  # noqa: E402 - activates LOG_FILE output capture

from dotenv import load_dotenv
from pathlib import Path

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
# 4. Upload document and create vector store
# ---------------------------------------------------------------------------
print("Creating vector store...")
data_dir = Path(__file__).resolve().parent / "data"

vector_store = openai.vector_stores.create(name="employee-handbook-store")

print("Uploading sample document...")
with (data_dir / "employee-handbook.md").open("rb") as file_handle:
    vector_store_file = openai.vector_stores.files.upload_and_poll(
        vector_store_id=vector_store.id,
        file=file_handle,
    )
print(f"  ✓ File uploaded and indexed (status: {vector_store_file.status})")
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
            "You are an HR assistant for Contoso Electronics. "
            "Answer employee questions using ONLY the information in the uploaded documents. "
            "If the answer isn't in the documents, say so clearly. "
            "Always be specific — cite numbers, dates, and policies exactly."
        ),
        tools=[FileSearchTool(vector_store_ids=[vector_store.id])],
    ),
)

# Save vector store ID for cleanup
vs_id_file = Path(__file__).resolve().parent / ".vector_store_id"
vs_id_file.write_text(vector_store.id)

# ---------------------------------------------------------------------------
# 6. Confirm success
# ---------------------------------------------------------------------------
print(f"\n✓ Agent \"{agent.name}\" created")
print(f"  Model: {MODEL_DEPLOYMENT}")
print(f"  Tools: file_search (vector store: {vector_store.id})")
print(f"  Document: employee-handbook.md")
_tee.console_only(f"  Endpoint: {PROJECT_ENDPOINT}")
print()
