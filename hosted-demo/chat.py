"""
chat.py — Interactive CLI chat with the hosted agent server.

This script connects to the locally running hosted agent (on port 8088)
and provides the same interactive chat experience as the other demos.
It chains responses via previous_response_id for multi-turn conversations.

Prerequisites:
  1. Start the agent server: python main.py (or run demo.bat)
  2. The agent should be listening on http://localhost:8088
"""

import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))
import _tee  # noqa: E402 - activates LOG_FILE output capture

import requests

AGENT_URL = "http://localhost:8088/responses"

# ---------------------------------------------------------------------------
# Interactive chat loop
# ---------------------------------------------------------------------------
print("=" * 60)
print("  Hosted Demo — Self-Hosted Agent (Responses Protocol)")
print("=" * 60)
print()
print(f"  Server: {AGENT_URL}")
print()
print("  Type your message and press Enter to chat.")
print("  Type 'exit' or 'quit' to end the session.")
print()
print("-" * 60)

previous_response_id = None

while True:
    # Prompt for user input
    try:
        user_input = input("\nYou: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\nGoodbye!")
        break

    # Check for exit commands
    if user_input.lower() in ("exit", "quit", "q"):
        print("Goodbye!")
        break

    # Skip empty input
    if not user_input:
        continue

    # -----------------------------------------------------------------
    # Send the message to the hosted agent
    # -----------------------------------------------------------------
    payload = {"input": user_input, "stream": False}
    if previous_response_id:
        payload["previous_response_id"] = previous_response_id

    try:
        resp = requests.post(AGENT_URL, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        # Extract the response text
        output_text = ""
        for item in data.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    output_text += content.get("text", "")

        # Chain for next turn
        previous_response_id = data.get("id")

        print(f"\nAgent: {output_text}")

    except requests.ConnectionError:
        print("\n[Error] Cannot connect to the agent server.")
        print("  Make sure the server is running: python main.py")
    except requests.Timeout:
        print("\n[Error] Request timed out.")
    except Exception as e:
        print(f"\n[Error] {e}")
