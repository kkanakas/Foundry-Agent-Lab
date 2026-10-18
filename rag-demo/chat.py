"""
chat.py — Interactive CLI chat grounded in your documents (RAG).

The agent searches through uploaded files to answer questions.
It only answers based on what's in the documents — no hallucination.

Prerequisites:
  1. From repo root: pip install -r requirements.txt
  2. az login
  3. Copy .env.sample to .env in this folder and fill in your values
  4. Run create_agent.py at least once to upload docs and register the agent
"""

import os
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))
import _tee  # noqa: E402 - activates LOG_FILE output capture

from dotenv import load_dotenv
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Load configuration
# ---------------------------------------------------------------------------
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path, override=True)

PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
AGENT_NAME = os.environ.get("AGENT_NAME", "RAG-Agent")

if not PROJECT_ENDPOINT:
    print("ERROR: PROJECT_ENDPOINT is not set.")
    print("Copy .env.sample to .env in this folder and fill in your Foundry project endpoint.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 2. Authenticate and create clients
# ---------------------------------------------------------------------------
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

credential = DefaultAzureCredential()
project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)
openai = project.get_openai_client()

# ---------------------------------------------------------------------------
# 3. Create a conversation
# ---------------------------------------------------------------------------
conversation = openai.conversations.create()

# ---------------------------------------------------------------------------
# 4. Interactive chat loop
# ---------------------------------------------------------------------------
print("=" * 60)
print("  RAG Demo — File Search / RAG Demo")
print("=" * 60)
print()
print(f"  Agent: {AGENT_NAME}")
print(f"  Tools: file_search (Contoso Employee Handbook and Foundry Overview)")
_tee.console_only(f"  Conversation ID: {conversation.id}")
print()
print("  Try: \"How many PTO days do new employees get? or What is Foundry?\"")
print("  Type 'exit' or 'quit' to end the session.")
print()
print("-" * 60)

while True:
    try:
        user_input = input("\nYou: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\nGoodbye!")
        break

    if user_input.lower() in ("exit", "quit", "q"):
        try:
            project.agents.delete(agent_name=AGENT_NAME)
            print(f"\n✓ Agent \"{AGENT_NAME}\" deleted.")
        except Exception as e:
            print(f"\n[Warning] Could not delete agent: {e}")
        print("Goodbye!")
        break

    if not user_input:
        continue

    # -----------------------------------------------------------------
    # Send message — file search happens automatically server-side
    # -----------------------------------------------------------------
    try:
        response = openai.responses.create(
            input=user_input,
            conversation=conversation.id,
            extra_body={"agent_reference": {"name": AGENT_NAME, "type": "agent_reference"}},
        )

        print(f"\nAgent: {response.output_text}")
        print(f"  [model: {response.model}]")

    except Exception as e:
        print(f"\n[Error] {e}")
        print("  Make sure you've run create_agent.py and your agent is active.")
