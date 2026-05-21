"""
chat.py — Interactive CLI chat with web search.

Unlike function calling (Demo 1), web search is a BUILT-IN tool.
Foundry handles the search server-side — no tool-calling loop needed
in our code. The response comes back with citations included.

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
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Load configuration
# ---------------------------------------------------------------------------
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path, override=True)

PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
AGENT_NAME = os.environ.get("AGENT_NAME", "Search-Agent")

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
# 4. Interactive chat loop (no tool loop needed — web search is server-side)
# ---------------------------------------------------------------------------
print("=" * 60)
print("  WebSearch Demo — Built-in Web Search Demo")
print("=" * 60)
print()
print(f"  Agent: {AGENT_NAME}")
print(f"  Tools: web_search (server-side, no client code needed)")
_tee.console_only(f"  Conversation ID: {conversation.id}")
print()
print("  Try: \"What happened in tech news today?\"")
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
    # Send message — web search happens automatically server-side
    # -----------------------------------------------------------------
    try:
        response = openai.responses.create(
            input=user_input,
            conversation=conversation.id,
            extra_body={"agent_reference": {"name": AGENT_NAME, "type": "agent_reference"}},
        )

        # Print the response text
        print(f"\nAgent: {response.output_text}")

        # Extract and display URL citations from annotations
        for item in response.output:
            if getattr(item, "type", None) == "message":
                for content in getattr(item, "content", []) or []:
                    if getattr(content, "type", None) == "output_text":
                        for ann in getattr(content, "annotations", []) or []:
                            if getattr(ann, "type", None) == "url_citation":
                                url = getattr(ann, "url", "")
                                title = getattr(ann, "title", "")
                                if url:
                                    label = f"({title})" if title else ""
                                    print(f"  🔗 {url}{label}")

        print()
        print(f"  [model: {response.model}]")

    except Exception as e:
        print(f"\n[Error] {e}")
        print("  Make sure you've run create_agent.py and your agent is active.")
