# Copyright (c) Microsoft. All rights reserved.

"""Multi-turn chat agent using azure-ai-agentserver-responses with Azure OpenAI.

Streams responses from Azure OpenAI Responses API in real-time and manages
multi-turn conversations via the Responses protocol's built-in server-side
state store.

Conversation state: This sample does NOT use any in-memory session state.
Conversation context is automatically managed by the platform via
``previous_response_id`` and ``context.get_history()`` — no
application-side session storage is needed.

Required environment variables:
    AZURE_OPENAI_ENDPOINT: Azure OpenAI endpoint (e.g., https://your-resource.openai.azure.com/)
    AZURE_AI_MODEL_DEPLOYMENT_NAME: Model deployment name (e.g., gpt-4o)

Uses DefaultAzureCredential for authentication - works with:
- Azure CLI login (az login)
- Managed Identity in Azure
- Environment variables (AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET)

Usage::

    # Set environment variables
    export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
    export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o"

    # Start the agent
    python main.py

    # Turn 1 — start conversation
    curl -N -X POST http://localhost:8088/responses \\
        -H "Content-Type: application/json" \\
        -d '{"model": "chat", "input": "What is Azure AI Foundry?", "stream": true}'

    # Turn 2 — chain via previous_response_id
    curl -N -X POST http://localhost:8088/responses \\
        -H "Content-Type: application/json" \\
        -d '{"model": "chat", "input": "Tell me more about hosted agents", "previous_response_id": "<ID>", "stream": true}'
"""

import asyncio
import os

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
    TextResponse,
)
from azure.ai.agentserver.responses.models import (
    MessageContentInputTextContent,
    MessageContentOutputTextContent,
)

import logging
logging.getLogger("azure.ai.agentserver").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

from dotenv import load_dotenv
load_dotenv(override=False)  # Load environment variables from .env file, but don't override existing ones

# Azure OpenAI configuration
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
AZURE_AI_MODEL_DEPLOYMENT_NAME = os.environ.get(
    "AZURE_AI_MODEL_DEPLOYMENT_NAME", "")

# Initialize Azure OpenAI client with DefaultAzureCredential
_credential = DefaultAzureCredential()
_token_provider = get_bearer_token_provider(
    _credential, "https://ai.azure.com/.default")

_openai_client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    azure_ad_token_provider=_token_provider,
    api_version="2025-03-01-preview",
)

app = ResponsesAgentServerHost(
    options=ResponsesServerOptions(default_fetch_history_count=20))

_SYSTEM_PROMPT = "You are a helpful AI assistant. Be concise and informative."


def _build_input(current_input: str, history: list) -> list[dict]:
    """Build Responses API input items from conversation history."""
    input_items = []

    # Add conversation history
    for item in history:
        if hasattr(item, 'content') and item.content:
            for content in item.content:
                if isinstance(content, MessageContentOutputTextContent) and content.text:
                    input_items.append(
                        {"role": "assistant", "content": content.text})
                elif isinstance(content, MessageContentInputTextContent) and content.text:
                    input_items.append(
                        {"role": "user", "content": content.text})

    # Add current user input
    input_items.append({"role": "user", "content": current_input})

    return input_items


@app.response_handler
async def handle_create(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Handle streaming response with Azure OpenAI Responses API and conversation history."""

    async def stream_openai():
        """Yield tokens from Azure OpenAI as an async iterable."""
        # Fetch conversation history (resolved via previous_response_id)
        history = await context.get_history()
        current_input = await context.get_input_text() or "Hello!"
        input_items = _build_input(current_input, history)

        try:
            loop = asyncio.get_event_loop()
            openai_stream = await loop.run_in_executor(
                None,
                lambda: _openai_client.responses.create(
                    model=AZURE_AI_MODEL_DEPLOYMENT_NAME,
                    instructions=_SYSTEM_PROMPT,
                    input=input_items,
                    stream=True,
                )
            )

            for event in openai_stream:
                if cancellation_signal.is_set():
                    return
                if event.type == "response.output_text.delta":
                    yield event.delta
        except Exception as e:
            yield f"\n\n[Error calling Azure OpenAI: {str(e)}]"

    return TextResponse(context, request, text=stream_openai())


if __name__ == "__main__":
    if not AZURE_OPENAI_ENDPOINT:
        print(
            "Warning: AZURE_OPENAI_ENDPOINT not set. Set it to your Azure OpenAI endpoint.")
    if not AZURE_AI_MODEL_DEPLOYMENT_NAME:
        print("Warning: AZURE_AI_MODEL_DEPLOYMENT_NAME not set. Set it to your model deployment name.")
    app.run()
