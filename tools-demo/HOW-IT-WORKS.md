# How It Works: Tools Demo

## Architecture

```
┌─────────────┐         ┌───────────────────────┐       ┌─────────────┐
│  Your       │         │  Azure AI Foundry     │       │  wttr.in    │
│  Terminal   │         │                       │       │  Weather API│
│             │         │  ┌─────────────────┐  │       │             │
│  chat.py ───┼────────►│  │  Weather-Agent  │  │       │             │
│         ◄───┼─────────┼──│  + get_weather  │  │       │             │
│             │         │  └────────┬────────┘  │       │             │
│             │         │           │           │       │             │
│  execute    │         │  "call get_weather"   │       │             │
│  locally ───┼─────────┼───────────────────────┼──────►│             │
│         ◄───┼─────────┼───────────────────────┼──────◄│             │
│             │         │                       │       │             │
│  send result┼────────►│  agent formats reply  │       │             │
│         ◄───┼─────────┼── final answer        │       │             │
└─────────────┘         └───────────────────────┘       └─────────────┘
```

## Flow (step by step)

```
1. create_agent.py
   │
   ├─ Same as Demo 0, PLUS:
   └─ tools=[FunctionTool(name="get_weather", parameters={...}, strict=True)]
       → Agent now knows it CAN call get_weather
       → Model decides WHEN to call it based on user's question

2. chat.py — the tool-calling loop
   │
   ├─ User: "What's the weather in Seattle?"
   │
   ├─ openai.responses.create(input=user_message)
   │   → Model returns: function_call(name="get_weather", args={"city":"Seattle"})
   │   → This is NOT a final answer — it's a REQUEST to run the function
   │
   ├─ Our code detects item.type == "function_call"
   │   ├─ Extracts: name="get_weather", args={"city": "Seattle"}
   │   ├─ Calls: requests.get("https://wttr.in/Seattle?format=j1")
   │   ├─ Prints: 🔧 Tool called: get_weather("Seattle")
   │   └─ Builds: FunctionCallOutput(call_id=..., output=json_result)
   │
   ├─ openai.responses.create(input=[FunctionCallOutput(...)])
   │   → Sends the weather data BACK to the agent
   │   → Agent now has real data to work with
   │   → Returns: final text response with weather info
   │
   └─ Print: "Agent: It's 56°F and partly cloudy in Seattle."
```

## Code Flow

### create_agent.py

```python
# Declare a function tool with a strict JSON schema
func_tool = FunctionTool(
    name="get_weather",
    description="Get the current weather for a given city.",
    parameters={"type": "object", "properties": {"city": {"type": "string"}}, ...},
    strict=True,
)
agent = project.agents.create_version(
    agent_name=AGENT_NAME,
    definition=PromptAgentDefinition(model=MODEL_DEPLOYMENT, tools=[func_tool], ...),
)
```

### chat.py — tool-calling loop

```python
response = openai.responses.create(input=user_input, conversation=conversation.id, ...)

# Loop while the model wants to call tools
while any(item.type == "function_call" for item in response.output):
    input_list = []
    for item in response.output:
        if item.type == "function_call":
            result = TOOL_FUNCTIONS[item.name](**json.loads(item.arguments))
            input_list.append(FunctionCallOutput(call_id=item.call_id, output=json.dumps(result)))

    # Send results back — agent formats the final answer
    response = openai.responses.create(input=input_list, conversation=conversation.id, ...)
```

## Key Concepts

### Function Calling is a Handshake
The model doesn't call APIs directly. Instead:
1. Model says "I want to call get_weather with these args"
2. YOUR code executes the function (you control what runs)
3. You send the result back
4. Model uses the result to form a natural-language answer

### Why This Matters
- **Security**: You control what code runs (no arbitrary execution)
- **Flexibility**: The function can do anything (API call, DB query, file read)
- **Verifiability**: The 🔧 trace proves the tool fired (not hallucinated)

### strict=True
With `strict=True`, the model is guaranteed to produce valid JSON matching
your schema. No need to handle malformed arguments.

### The Model Can't Fake This
Ask "What's the weather?" — the model would normally refuse or hallucinate.
With the tool, it returns real, current data that changes every hour.
