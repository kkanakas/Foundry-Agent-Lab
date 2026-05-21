"""
chat.py — Interactive CLI chat with function calling (tool use).

This script handles the tool-calling loop: when the agent decides to call
a function, we execute it locally and send the result back. The terminal
shows each tool invocation so the audience can see it happening in real time.

Prerequisites:
  1. From repo root: pip install -r requirements.txt
  2. az login
  3. Copy .env.sample to .env in this folder and fill in your values
  4. Run create_agent.py at least once to register the agent
"""

import json
import os
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))
import _tee  # noqa: E402 - activates LOG_FILE output capture

import requests
from dotenv import load_dotenv
from pathlib import Path
from openai.types.responses.response_input_param import FunctionCallOutput

# ---------------------------------------------------------------------------
# 1. Load configuration
# ---------------------------------------------------------------------------
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path, override=True)

PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
AGENT_NAME = os.environ.get("AGENT_NAME", "Weather-Agent")

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
# 3. Tool implementations
# ---------------------------------------------------------------------------
def get_weather(city: str) -> dict:
    """Fetch current weather from wttr.in (free, no API key needed)."""
    print(f"  🔧 Tool called: get_weather(\"{city}\")")
    try:
        resp = requests.get(
            f"https://wttr.in/{city}?format=j1",
            timeout=10,
            headers={"User-Agent": "azure-agent-demo"}
        )
        resp.raise_for_status()
        data = resp.json()
        current = data["current_condition"][0]
        result = {
            "city": city,
            "temperature_c": current["temp_C"],
            "temperature_f": current["temp_F"],
            "condition": current["weatherDesc"][0]["value"],
            "humidity": current["humidity"] + "%",
            "wind_kph": current["windspeedKmph"],
        }
        print(f"  🔧 Result: {result['temperature_f']}°F, {result['condition']}")
        return result
    except Exception as e:
        print(f"  🔧 Error: {e}")
        return {"error": f"Could not fetch weather for {city}: {e}"}


# Map of function names to implementations
TOOL_FUNCTIONS = {
    "get_weather": get_weather,
}

# ---------------------------------------------------------------------------
# 4. Create a conversation
# ---------------------------------------------------------------------------
conversation = openai.conversations.create()

# ---------------------------------------------------------------------------
# 5. Interactive chat loop with tool-calling support
# ---------------------------------------------------------------------------
print("=" * 60)
print("  Tools Demo — Function Calling Demo")
print("=" * 60)
print()
print(f"  Agent: {AGENT_NAME}")
print(f"  Tools: get_weather")
_tee.console_only(f"  Conversation ID: {conversation.id}")
print()
print("  Try: \"What's the weather in Seattle?\"")
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
    # Send message and handle tool-calling loop
    # -----------------------------------------------------------------
    try:
        response = openai.responses.create(
            input=user_input,
            conversation=conversation.id,
            extra_body={"agent_reference": {"name": AGENT_NAME, "type": "agent_reference"}},
        )

        # Tool-calling loop: keep processing until we get a text response
        while response.output and any(
            item.type == "function_call" for item in response.output
        ):
            input_list = []
            for item in response.output:
                if item.type == "function_call":
                    func_name = item.name
                    func_args = json.loads(item.arguments)

                    # Execute the tool
                    if func_name in TOOL_FUNCTIONS:
                        result = TOOL_FUNCTIONS[func_name](**func_args)
                    else:
                        result = {"error": f"Unknown function: {func_name}"}

                    input_list.append(
                        FunctionCallOutput(
                            type="function_call_output",
                            call_id=item.call_id,
                            output=json.dumps(result),
                        )
                    )

            # Submit function results and get the final response
            response = openai.responses.create(
                input=input_list,
                conversation=conversation.id,
                extra_body={"agent_reference": {"name": AGENT_NAME, "type": "agent_reference"}},
            )

        # Print the final text response
        print(f"\nAgent: {response.output_text}")
        print(f"  [model: {response.model}]")

    except Exception as e:
        print(f"\n[Error] {e}")
        print("  Make sure you've run create_agent.py and your agent is active.")
