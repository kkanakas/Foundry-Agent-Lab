"""
chat.py — Interactive CLI chat consuming a Foundry Toolbox via MCP.

Follows the Microsoft Agent Framework pattern:
  - Connects to the toolbox's MCP endpoint with bearer-token auth
  - Discovers tools dynamically from the toolbox
  - Uses the OpenAI Responses API for the chat loop
  - Proxies tool calls through the MCP connection

This demonstrates the enterprise pattern: tools are curated centrally in
a Toolbox and consumed by any agent runtime with proper auth.

Prerequisites:
  1. From repo root: pip install -r requirements.txt
  2. az login
  3. Copy .env.sample to .env in this folder and fill in your values
  4. Run create_agent.py at least once to create the toolbox
"""

import asyncio
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
MODEL_DEPLOYMENT = os.environ.get("MODEL_DEPLOYMENT", "model-router")
TOOLBOX_NAME = os.environ.get("TOOLBOX_NAME", "demo-toolbox")

if not PROJECT_ENDPOINT:
    print("ERROR: PROJECT_ENDPOINT is not set.")
    print("Copy .env.sample to .env in this folder and fill in your Foundry project endpoint.")
    sys.exit(1)

TOOLBOX_MCP_ENDPOINT = (
    f"{PROJECT_ENDPOINT}/toolboxes/{TOOLBOX_NAME}/mcp?api-version=v1"
)

# ---------------------------------------------------------------------------
# 2. Authenticate with Azure (MAF pattern: bearer token for toolbox endpoint)
# ---------------------------------------------------------------------------
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.ai.projects import AIProjectClient
import httpx

credential = DefaultAzureCredential()
token_provider = get_bearer_token_provider(credential, "https://ai.azure.com/.default")

project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)
openai = project.get_openai_client()


# Custom httpx auth that injects bearer token (from MAF docs)
class _ToolboxAuth(httpx.Auth):
    def __init__(self, provider):
        self._provider = provider

    def auth_flow(self, request):
        token = self._provider()
        request.headers["Authorization"] = f"Bearer {token}"
        yield request


# ---------------------------------------------------------------------------
# 3. Connect to toolbox MCP endpoint and discover tools
# ---------------------------------------------------------------------------
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def connect_and_chat():
    """Main async loop: connect to toolbox, discover tools, run chat."""

    print("Connecting to toolbox MCP endpoint...")
    _tee.console_only(f"  URL: {TOOLBOX_MCP_ENDPOINT}")

    # Build authenticated headers for the MCP connection
    token = token_provider()
    headers = {
        "Authorization": f"Bearer {token}",
        "Foundry-Features": "Toolboxes=V1Preview",
    }

    async with streamablehttp_client(
        url=TOOLBOX_MCP_ENDPOINT,
        headers=headers,
    ) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Discover tools from the toolbox (filtered to curated subsets)
            ALLOWED_TOOLS = {
                # Issue management
                "github___list_issues",
                "github___issue_read",
                "github___issue_write",
                "github___search_issues",
                "github___add_issue_comment",
                "github___get_label",
                # Repository browsing
                "github___search_repositories",
                "github___get_file_contents",
                "github___list_branches",
                "github___list_commits",
                "github___search_code",
                "github___list_tags",
            }

            tools_result = await session.list_tools()
            all_tools = tools_result.tools
            mcp_tools = [t for t in all_tools if t.name in ALLOWED_TOOLS]

            print(f"✓ Connected! {len(all_tools)} tools on server, {len(mcp_tools)} curated:")
            for t in mcp_tools:
                print(f"    • {t.name}: {t.description or '(no description)'}")

            # Convert MCP tools to OpenAI function-call schema
            openai_tools = []
            for t in mcp_tools:
                openai_tools.append({
                    "type": "function",
                    "name": t.name,
                    "description": t.description or t.name,
                    "parameters": t.inputSchema if t.inputSchema else {"type": "object", "properties": {}},
                })

            # ---------------------------------------------------------------
            # 4. Interactive chat loop
            # ---------------------------------------------------------------
            print()
            print("=" * 60)
            print("  Toolbox Demo — Centralized Tool Governance")
            print("=" * 60)
            print()
            print(f"  Toolbox: {TOOLBOX_NAME}")
            print(f"  Model:   {MODEL_DEPLOYMENT}")
            print(f"  Tools:   {len(mcp_tools)} curated (issues + repos)")
            print()
            print("  Try: \"Search for issues labeled bug in microsoft/vscode\"")
            print("       \"List repos for microsoft on GitHub\"")
            print("  Type 'exit' or 'quit' to end the session.")
            print()
            print("-" * 60)

            instructions = (
                "You are a helpful assistant with access to a centralized toolbox. "
                "The toolbox provides GitHub tools via MCP. "
                "Use these tools for repository queries, code search, issues, "
                "pull requests, and user lookups. Always explain what tool you "
                "plan to use before invoking it."
            )
            conversation_input = []

            while True:
                try:
                    user_input = input("\nYou: ").strip()
                except (KeyboardInterrupt, EOFError):
                    print("\n\nGoodbye!")
                    break

                if user_input.lower() in ("exit", "quit", "q"):
                    print("Goodbye!")
                    break

                if not user_input:
                    continue

                conversation_input.append({
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": user_input}],
                })

                # Call the model with toolbox tools
                try:
                    response = openai.responses.create(
                        model=MODEL_DEPLOYMENT,
                        instructions=instructions,
                        input=conversation_input,
                        tools=openai_tools,
                    )

                    # Process tool calls in a loop until we get a text response
                    max_rounds = 3
                    round_count = 0
                    prev_result_preview = None  # track last result for repeat detection
                    while response.output and any(
                        getattr(item, "type", None) == "function_call"
                        for item in response.output
                    ):
                        round_count += 1
                        if round_count > max_rounds:
                            print("\n  [Max tool rounds reached — stopping]")
                            break
                        tool_outputs = []

                        for item in response.output:
                            if getattr(item, "type", None) != "function_call":
                                continue

                            tool_name = item.name
                            arguments = json.loads(item.arguments) if item.arguments else {}

                            print(f"\n🔧 Tool call: {tool_name}")
                            print(f"   Args: {json.dumps(arguments, indent=2)}")

                            # Ask user for approval
                            answer = input("   Approve? (y/N): ").strip().lower()
                            if answer != "y":
                                print("   ✗ Denied")
                                tool_outputs.append({
                                    "type": "function_call_output",
                                    "call_id": item.call_id,
                                    "output": json.dumps({"error": "Tool call denied by user"}),
                                })
                                continue

                            print("   ✓ Approved — calling toolbox...")

                            # Execute tool via MCP session
                            try:
                                result = await session.call_tool(tool_name, arguments)
                                # Extract text content from MCP result
                                output_text = ""
                                for content in result.content:
                                    if hasattr(content, "text"):
                                        output_text += content.text
                                    else:
                                        output_text += str(content)

                                tool_outputs.append({
                                    "type": "function_call_output",
                                    "call_id": item.call_id,
                                    "output": output_text[:10000],  # truncate if huge
                                })
                                print(f"   ✓ Got result ({len(output_text)} chars)")
                                # Show preview so user can see what came back
                                preview = output_text[:200].replace("\n", " ")
                                print(f"   Preview: {preview}{'...' if len(output_text) > 200 else ''}")
                            except Exception as tool_err:
                                tool_outputs.append({
                                    "type": "function_call_output",
                                    "call_id": item.call_id,
                                    "output": json.dumps({"error": str(tool_err)}),
                                })
                                print(f"   ✗ Error: {tool_err}")

                        # Detect repeated identical results (model stuck in a loop)
                        current_preview = "".join(
                            o["output"][:200] for o in tool_outputs
                        )
                        if prev_result_preview and current_preview == prev_result_preview:
                            print("\n  [Same result repeated — stopping loop]")
                            # Send outputs back with no tools to get a summary
                            response = openai.responses.create(
                                model=MODEL_DEPLOYMENT,
                                instructions=instructions + " Summarize what you found so far. Do not call any more tools.",
                                input=conversation_input + list(response.output) + tool_outputs,
                                tools=[],
                            )
                            break
                        prev_result_preview = current_preview

                        # Send tool outputs back to the model
                        response = openai.responses.create(
                            model=MODEL_DEPLOYMENT,
                            instructions=instructions,
                            input=conversation_input + list(response.output) + tool_outputs,
                            tools=openai_tools,
                        )

                    # Print final text response
                    output_text = response.output_text
                    if not output_text:
                        # If the loop broke at max_rounds, response may have
                        # unresolved function_calls. Flush them to get text.
                        has_orphans = any(
                            getattr(item, "type", None) == "function_call"
                            for item in response.output
                        )
                        if has_orphans:
                            # Provide stub outputs and ask model to summarize
                            stub_outputs = []
                            for item in response.output:
                                if getattr(item, "type", None) == "function_call":
                                    stub_outputs.append({
                                        "type": "function_call_output",
                                        "call_id": item.call_id,
                                        "output": json.dumps({"error": "Tool limit reached, please summarize what you have so far."}),
                                    })
                            response = openai.responses.create(
                                model=MODEL_DEPLOYMENT,
                                instructions=instructions + " Summarize what you found so far. Do not call any more tools.",
                                input=conversation_input + list(response.output) + stub_outputs,
                                tools=[],
                            )
                            output_text = response.output_text or "(Could not produce summary)"
                        else:
                            output_text = "(No text response — tools may have returned insufficient data)"
                    print(f"\nAgent: {output_text}")
                    print(f"  [model: {response.model}]")

                    # Track conversation by appending the model's output items
                    conversation_input.extend(response.output)

                except Exception as e:
                    print(f"\n[Error] {e}")
                    print("  Check auth, toolbox status, or try again.")


# ---------------------------------------------------------------------------
# 5. Run the async chat
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(connect_and_chat())
