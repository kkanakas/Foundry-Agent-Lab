"""
chat.py — Desktop (tkinter) chat window for your Azure AI Foundry prompt agent.

This script connects to your Foundry project, creates a conversation, and
provides a simple GUI chat window. The conversation maintains history,
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
import threading
import tkinter as tk
from tkinter import scrolledtext

from dotenv import load_dotenv
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Load configuration
# ---------------------------------------------------------------------------
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path, override=True)

PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
AGENT_NAME = os.environ.get("AGENT_NAME", "Desktop Demo")

if not PROJECT_ENDPOINT:
    print("ERROR: PROJECT_ENDPOINT is not set.")
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
# 4. Tkinter chat window
# ---------------------------------------------------------------------------
class ChatWindow:
    def __init__(self, root):
        root.title(f"Desktop Demo — {AGENT_NAME}")
        root.geometry("600x500")

        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, state=tk.DISABLED, font=("Consolas", 10)
        )
        self.chat_display.pack(padx=10, pady=(10, 5), fill=tk.BOTH, expand=True)

        # Input frame
        input_frame = tk.Frame(root)
        input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)

        self.input_field = tk.Entry(input_frame, font=("Consolas", 10))
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_field.bind("<Return>", self.on_send)
        self.input_field.focus()

        self.send_button = tk.Button(
            input_frame, text="Send", command=self.on_send
        )
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))

        self.append_message("System", f"Connected to agent: {AGENT_NAME}")
        self.append_message("System", "Type your message and press Enter.\n")

    def append_message(self, sender, text):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}: {text}\n\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def on_send(self, event=None):
        user_input = self.input_field.get().strip()
        if not user_input:
            return

        # Check for exit commands
        if user_input.lower() in ("exit", "quit", "q"):
            on_close()
            return

        self.input_field.delete(0, tk.END)
        self.append_message("You", user_input)
        _tee.log_chat("You", user_input)

        # Disable input while waiting for response
        self.input_field.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)

        # Run API call in background thread to keep UI responsive
        threading.Thread(target=self.get_response, args=(user_input,), daemon=True).start()

    def get_response(self, user_input):
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
            reply = response.output_text
            model = response.model
            _tee.log_chat("Agent", f"{reply}\n  [model: {model}]")
            # Schedule UI update on main thread
            root.after(0, self.append_message, "Agent", f"{reply}\n  [model: {model}]")
        except Exception as e:
            root.after(0, self.append_message, "Error", str(e))
        finally:
            root.after(0, self.enable_input)

    def enable_input(self):
        self.input_field.config(state=tk.NORMAL)
        self.send_button.config(state=tk.NORMAL)
        self.input_field.focus()


# ---------------------------------------------------------------------------
# 5. Run
# ---------------------------------------------------------------------------
root = tk.Tk()
app = ChatWindow(root)

def on_close():
    try:
        project.agents.delete(agent_name=AGENT_NAME)
        print(f"✓ Agent \"{AGENT_NAME}\" deleted.")
    except Exception:
        pass
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
