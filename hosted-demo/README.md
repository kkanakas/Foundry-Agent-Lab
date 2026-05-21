# Multi-turn Chat Agent (Responses Protocol)

This sample demonstrates a multi-turn chat agent using the `azure-ai-agentserver-responses` SDK with **real-time streaming** from Azure OpenAI and conversation history via `previous_response_id`.

## Features

- **Azure OpenAI streaming**: Responses are streamed from Azure OpenAI in real-time — tokens arrive as `response.output_text.delta` SSE events
- **Conversation history**: Uses `context.get_history_async()` to retrieve previous conversation turns
- **Context chaining**: Links responses via `previous_response_id` parameter
- **DefaultAzureCredential**: Supports multiple authentication methods (Azure CLI, Managed Identity, etc.)

> **Conversation State**: This sample uses the Responses protocol's built-in server-side conversation state store. Conversation context is automatically managed by the platform via `previous_response_id` — no application-side session storage is needed.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL (e.g., `https://your-resource.openai.azure.com/`) | Yes |
| `AZURE_AI_MODEL_DEPLOYMENT_NAME` | Model deployment name (default: `gpt-4.1`) | No |

This template includes a `.env` file in the project folder. Open `.env` and replace the placeholder values for the variables above before running the sample. If you start the agent from a terminal, load those values into your shell or export them manually before running `python main.py`.

## How It Works

1. The client sends a request with `input` text
2. For follow-up turns, the client includes `previous_response_id` pointing to the last response
3. The agent calls `context.get_history_async()` to hydrate conversation history
4. Azure OpenAI is called with `stream=True` and tokens are forwarded as SSE events

## Run Locally

### Install dependencies

```bash
# Install dependencies
pip install -r requirements.txt
```

### Set environment variables

Update the `.env` file with your Azure OpenAI endpoint and model deployment name.

```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4.1
```

### Start the agent

> **Tip:** Make sure the correct Python interpreter is selected in VS Code (Command Palette: **Python: Select Interpreter** or run command `python.setInterpreter`) so that debugging uses the right environment.

After installing dependencies, press **F5** in VS Code to start the agent and test it directly.

To start from the terminal instead:

```bash
python main.py
```

The agent starts on `http://localhost:8088/`. Open Agent Inspector (Command Palette: **AI Toolkit: Open Agent Inspector**) to connect and interact with the server.

## Testing

### 1. Test with curl

#### Turn 1 — Initial message

```bash
curl -N -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello, my name is Alice!", "stream": true}'
```

Save the `id` from the response for the next turn.

#### Turn 2 — Follow-up message

```bash
curl -N -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{"input": "What is my name?", "stream": true, "previous_response_id": "<RESPONSE_1_ID>"}'
```

The agent will recall that your name is Alice from the conversation history.

### 2. Test in Agent Inspector

Once the agent is running, open **Agent Inspector** in VS Code to interactively send messages and view responses.

#### Turn 1 — Start conversation

Type the following message in Inspector:

```
Hello, my name is Alice!
```

#### Turn 2 — Ask about context

Send a follow-up message in the same session:

```
What is my name?
```

The agent will recall that your name is Alice from the conversation history.

## Deploying to Microsoft Foundry

To deploy your agent to Microsoft Foundry:

1. Open the Command Palette (`Ctrl+Shift+P`).
2. Run **Microsoft Foundry: Deploy Hosted Agent**.
3. The extension reads `agent.yaml` and auto-populates what it can. You may be prompted for:
   - **Agent name** -- the name registered with the hosting service.
   - **Dockerfile** -- auto-detected from workspace root, or select manually.
   - **Container registry** -- defaults to auto-created; optionally provide your own ACR.
   - **Resource size** -- CPU and memory allocation:

     | Option                        | CPU  | Memory |
     | ----------------------------- | ---- | ------ |
     | 0.25 CPU cores, 0.5 Gi memory | 0.25 | 0.5 Gi |
     | 0.5 CPU cores, 1 Gi memory    | 0.5  | 1.0 Gi |
     | 1 CPU cores, 2 Gi memory      | 1.0  | 2.0 Gi |
     | 2 CPU cores, 4 Gi memory      | 2.0  | 4.0 Gi |

4. The extension builds the container image in ACR, creates the agent version, and assigns required RBAC roles automatically.

### Azure OpenAI Permission Denied (401)

The identity running the agent does not have the required RBAC roles on the Azure AI Foundry project. Assign the following roles:

- **Cognitive Services OpenAI User**
- **Azure AI User**

Use the Azure CLI to assign them:

```
az role assignment create \
  --assignee <principal-id> \
  --role "Cognitive Services OpenAI User" \
  --scope /subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.CognitiveServices/accounts/<ai-services-account-name>

az role assignment create \
  --assignee <principal-id> \
  --role "Azure AI User" \
  --scope /subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.CognitiveServices/accounts/<ai-services-account-name>
```

> **Note:** It may take a few minutes for role assignments to propagate. Retry the request after waiting.
