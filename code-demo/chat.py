"""
chat.py — Gradio web UI for the code interpreter agent.

A simple web chat interface that shows the agent's responses including
any code it writes and executes. Gradio provides a polished chat UI
with minimal code.

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

import gradio as gr
from dotenv import load_dotenv
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Load configuration
# ---------------------------------------------------------------------------
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path, override=True)

PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
AGENT_NAME = os.environ.get("AGENT_NAME", "Code-Agent")

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
# 4. Chat function for Gradio

_output_dir = Path(__file__).resolve().parent / "output"
_output_dir.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
def chat(user_message, history):
    """Send message to agent and return response."""
    if not user_message.strip():
        return ""

    _tee.log_chat("You", user_message)

    try:
        response = openai.responses.create(
            input=user_message,
            conversation=conversation.id,
            extra_body={"agent_reference": {"name": AGENT_NAME, "type": "agent_reference"}},
        )

        # Build reply showing code blocks alongside the text output
        parts = []        # text parts (markdown)
        image_paths = []  # local paths to downloaded images

        for item in response.output:
            if getattr(item, "type", None) == "code_interpreter_call":
                code = getattr(item, "code", "") or ""
                if code.strip():
                    parts.append(f"```python\n{code}\n```")
            elif getattr(item, "type", None) == "message":
                for content in getattr(item, "content", []) or []:
                    if getattr(content, "type", None) == "output_text":
                        text = getattr(content, "text", None)
                        if text:
                            parts.append(text)
                        # Download files referenced in annotations
                        for ann in getattr(content, "annotations", []) or []:
                            if getattr(ann, "type", None) == "container_file_citation":
                                file_id = getattr(ann, "file_id", None)
                                container_id = getattr(ann, "container_id", None)
                                filename = getattr(ann, "filename", "output.png")
                                if file_id and container_id:
                                    try:
                                        file_content = openai.containers.files.content.retrieve(
                                            file_id=file_id, container_id=container_id
                                        )
                                        local_path = str(_output_dir / filename)
                                        with open(local_path, "wb") as f:
                                            f.write(file_content.read())
                                        # Only show images inline
                                        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                                            image_paths.append(local_path)
                                        else:
                                            parts.append(f"📁 Saved: `{filename}`")
                                        print(f"  [Downloaded] {filename}")
                                    except Exception as e:
                                        print(f"  [Download failed] {filename}: {e}")

        text_reply = "\n\n".join(parts) if parts else response.output_text
        model_info = f"\n\n---\n*[model: {response.model}]*"
        _tee.log_chat("Agent", text_reply)
        print(f"  [model: {response.model}]")

        # Return response with images if any were downloaded
        if image_paths:
            return {"text": text_reply + model_info, "files": image_paths}
        return text_reply + model_info

    except Exception as e:
        return f"**Error:** {e}\n\nMake sure you've run `create_agent.py` first."

# ---------------------------------------------------------------------------
# 5. Build and launch Gradio interface
# ---------------------------------------------------------------------------
demo = gr.ChatInterface(
    fn=chat,
    title="🐍 Code Interpreter Agent",
    description=(
        f"Agent: **{AGENT_NAME}** | Tool: code_interpreter (sandboxed Python)\n\n"
        "Ask me to do calculations, analyze data, or create visualizations. "
        "I'll write and run Python code to get you accurate results."
    ),
    examples=[
        "Calculate the first 20 Fibonacci numbers and show them in a table.",
        "What's the standard deviation of [23, 45, 12, 67, 34, 89, 56]?",
        "Create a bar chart comparing the populations of the top 5 most populous countries.",
        "Solve this equation: 3x² + 7x - 5 = 0",
    ],
)

if __name__ == "__main__":
    print(f"\n  Agent: {AGENT_NAME}")
    _tee.console_only(f"  Conversation ID: {conversation.id}")
    print(f"  Opening browser...\n")
    demo.launch(inbrowser=True, allowed_paths=[str(_output_dir)])
