"""
chat.py — Interactive CLI chat with MCP tool approval flow.

The agent is connected to a remote MCP server. When it wants to call
an MCP tool, you get an approval request showing the tool name and
arguments. You review and approve/deny before it proceeds.

This demonstrates the human-in-the-loop pattern for MCP tool invocations.

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

from dotenv import load_dotenv
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Load configuration
# ---------------------------------------------------------------------------
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path, override=True)

PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
AGENT_NAME = os.environ.get("AGENT_NAME", "MCP-Agent")
MCP_SERVER_LABEL = os.environ.get("MCP_SERVER_LABEL", "github")

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

from openai.types.responses.response_input_param import McpApprovalResponse

# ---------------------------------------------------------------------------
# 3. Create a conversation
# ---------------------------------------------------------------------------
conversation = openai.conversations.create()

# ---------------------------------------------------------------------------
# 4. Interactive chat loop with MCP approval flow
# ---------------------------------------------------------------------------
print("=" * 60)
print("  MCP Demo — Model Context Protocol Integration")
print("=" * 60)
print()
print(f"  Agent: {AGENT_NAME}")
print(f"  Tools: MCP server ({MCP_SERVER_LABEL})")
print(f"  Approval: required for each tool call")
_tee.console_only(f"  Conversation ID: {conversation.id}")
print()
print("  Try: \"What is my GitHub username?\"")
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
    # Send message to agent
    # -----------------------------------------------------------------
    try:
        response = openai.responses.create(
            input=user_input,
            conversation=conversation.id,
            extra_body={"agent_reference": {"name": AGENT_NAME, "type": "agent_reference"}},
        )

        # Check if the response contains MCP approval requests
        approval_list = []
        has_approvals = False

        for item in response.output:
            if getattr(item, "type", None) == "mcp_approval_request" and item.id:
                has_approvals = True
                server = getattr(item, "server_label", MCP_SERVER_LABEL)
                tool_name = getattr(item, "name", "<unknown>")
                arguments = getattr(item, "arguments", None)

                print(f"\n🔐 MCP tool approval requested:")
                print(f"   Server: {server}")
                print(f"   Tool:   {tool_name}")
                if arguments:
                    print(f"   Args:   {json.dumps(arguments, indent=2, default=str)}")

                # Ask user for approval
                answer = input("   Approve? (y/N): ").strip().lower()
                should_approve = answer == "y"

                approval_list.append(
                    McpApprovalResponse(
                        type="mcp_approval_response",
                        approve=should_approve,
                        approval_request_id=item.id,
                    )
                )

                if should_approve:
                    print("   ✓ Approved")
                else:
                    print("   ✗ Denied")

        # If there were approval requests, send them back
        if has_approvals and approval_list:
            try:
                response = openai.responses.create(
                    input=approval_list,
                    conversation=conversation.id,
                    extra_body={"agent_reference": {"name": AGENT_NAME, "type": "agent_reference"}},
                )
            except Exception as tool_err:
                # Tool execution failed (e.g. MCP server returned an error).
                # The conversation is now stuck — create a fresh one.
                print(f"\n[Tool error] {tool_err}")
                conversation = openai.conversations.create()
                print("  (Starting fresh conversation due to tool failure)")
                continue

        # Print final response
        print(f"\nAgent: {response.output_text}")
        print(f"  [model: {response.model}]")

    except Exception as e:
        print(f"\n[Error] {e}")
        print("  Make sure you've run create_agent.py and your agent is active.")
