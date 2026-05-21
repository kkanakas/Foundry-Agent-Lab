"""
chat.py — Interactive CLI chat with your Azure AI Foundry prompt agent.

This script connects to your Foundry project, creates a conversation, and
lets you chat with your agent in a loop. The conversation maintains history,
so follow-up questions work naturally.

Prerequisites:
  1. From repo root: pip install -r requirements.txt
  2. az login
  3. Copy .env.sample to .env in this folder and fill in your values
  4. Run create_agent.py at least once to register the agent
"""

import os
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))
import _tee  # noqa: E402 - activates LOG_FILE output capture

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# 1. Load configuration
# ---------------------------------------------------------------------------
# The .env file lives in this demo folder.

from pathlib import Path

_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path, override=True)

PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
AGENT_NAME = os.environ.get("AGENT_NAME", "Hello-Agent")

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

# The AIProjectClient gives us access to the Foundry project APIs.
project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=credential,
)

# get_openai_client() returns an OpenAI-compatible client that routes
# requests through your Foundry project. This gives us access to the
# conversations and responses APIs.
openai = project.get_openai_client()

# ---------------------------------------------------------------------------
# 3. Create a conversation
# ---------------------------------------------------------------------------
# A conversation is a server-side session that keeps track of message history.
# All messages sent within the same conversation share context, enabling
# multi-turn interactions (follow-up questions, references to earlier answers).
conversation = openai.conversations.create()

# ---------------------------------------------------------------------------
# 4. Interactive chat loop
# ---------------------------------------------------------------------------
print("=" * 60)
print("  Hello Demo — Azure AI Foundry Chat Demo")
print("=" * 60)
print()
print(f"  Agent: {AGENT_NAME}")
_tee.console_only(f"  Conversation ID: {conversation.id}")
print()
print("  Type your message and press Enter to chat.")
print("  Type 'exit' or 'quit' to end the session.")
print()
print("-" * 60)

while True:
    # Prompt for user input
    try:
        user_input = input("\nYou: ").strip()
    except (KeyboardInterrupt, EOFError):
        # Handle Ctrl+C or Ctrl+D gracefully
        print("\n\nGoodbye!")
        break

    # Check for exit commands
    if user_input.lower() in ("exit", "quit", "q"):
        try:
            project.agents.delete(agent_name=AGENT_NAME)
            print(f"\n✓ Agent \"{AGENT_NAME}\" deleted.")
        except Exception as e:
            print(f"\n[Warning] Could not delete agent: {e}")
        print("Goodbye!")
        break

    # Skip empty input
    if not user_input:
        continue

    # -----------------------------------------------------------------
    # Send the message to the agent and get a response
    # -----------------------------------------------------------------
    # openai.responses.create() sends the user's input to the agent
    # within the existing conversation. The agent_reference tells Foundry
    # which named agent should handle this request.
    #
    # Because we reuse the same conversation.id, the agent sees all
    # previous messages and can answer follow-up questions in context.
    try:
        response = openai.responses.create(
            conversation=conversation.id,
            extra_body={
                "agent_reference": {
                    "name": AGENT_NAME,
                    "type": "agent_reference",
                }
            },
            input=user_input,
        )

        # Print the agent's response
        print(f"\nAgent: {response.output_text}")
        print(f"  [model: {response.model}]")

    except Exception as e:
        print(f"\n[Error] {e}")
        print("  Make sure you've run create_agent.py and your agent is active.")
