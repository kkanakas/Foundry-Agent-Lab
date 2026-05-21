# How It Works: RAG Demo

## Architecture

```
┌─────────────┐         ┌──────────────────────────────────────────┐
│  Your       │         │  Azure AI Foundry                         │
│  Terminal   │         │                                           │
│             │         │  ┌─────────────────┐                      │
│  chat.py ───┼────────►│  │   RAG-Agent     │                      │
│             │         │  └────────┬────────┘                      │
│             │         │           │                               │
│             │         │           ▼ (agent decides to search)     │
│             │         │  ┌─────────────────────────┐              │
│             │         │  │  File Search (built-in) │              │
│             │         │  │                         │              │
│             │         │  │  ┌───────────────────┐  │              │
│             │         │  │  │  Vector Store     │  │              │
│             │         │  │  │  ┌─────────────┐  │  │              │
│             │         │  │  │  │ employee-   │  │  │              │
│             │         │  │  │  │ handbook.md │  │  │              │
│             │         │  │  │  └─────────────┘  │  │              │
│             │         │  │  └───────────────────┘  │              │
│             │         │  └────────────┬────────────┘              │
│             │         │               │                           │
│             │         │               ▼                           │
│         ◄───┼─────────┼── answer grounded in document content     │
└─────────────┘         └──────────────────────────────────────────┘
```

## Setup Flow (create_agent.py)

```
1. Upload document
   │
   ├─ project.agents.files.upload("employee-handbook.md")
   │   → File stored in Foundry, returns file_id
   │
   ├─ project.agents.vector_stores.create(file_ids=[file_id])
   │   → Document is chunked into segments
   │   → Each chunk is embedded (converted to a vector)
   │   → Vectors are indexed for semantic search
   │   → Returns vector_store_id
   │
   └─ project.agents.create_version(tools=[FileSearchTool(vector_store_ids=[vs_id])])
       → Agent now has access to search the vector store
```

## Query Flow (chat.py)

```
User: "How many PTO days do new employees get?"
  │
  ▼
Agent receives question
  │
  ▼
File Search activates (server-side):
  ├─ Embeds the question as a vector
  ├─ Searches vector store for similar chunks
  ├─ Retrieves: "New employees: 15 days PTO per year"
  │
  ▼
Agent reads retrieved chunks
  │
  ▼
Agent generates answer GROUNDED in the chunks:
  "New employees at Contoso Electronics receive 15 days
   of PTO per year. After 3 years, this increases to 20 days."
```

## Code Flow

### create_agent.py — upload document and attach vector store

```python
# Create a vector store and upload a document
vector_store = openai.vector_stores.create(name="employee-handbook-store")
openai.vector_stores.files.upload_and_poll(vector_store_id=vector_store.id, file=file_handle)

# Attach to agent — file search happens server-side
agent = project.agents.create_version(
    agent_name=AGENT_NAME,
    definition=PromptAgentDefinition(
        model=MODEL_DEPLOYMENT,
        tools=[FileSearchTool(vector_store_ids=[vector_store.id])],
        ...
    ),
)
```

### chat.py

```python
# Same simple call as Demo 0 — file search is fully server-side
response = openai.responses.create(input=user_input, conversation=conversation.id, ...)
print(response.output_text)  # Answer grounded in document content
```

## Key Concepts

### What is RAG?
**R**etrieval **A**ugmented **G**eneration:
1. **Retrieve** — find relevant document chunks
2. **Augment** — add them to the model's context
3. **Generate** — produce an answer based on those chunks

### Why RAG instead of fine-tuning?
- **Fresh data**: Update documents anytime, no retraining
- **Verifiable**: You can check what source was used
- **Scoped**: Agent only knows what you give it
- **Cost**: No expensive training runs

### Vector Stores
Documents are split into chunks (~500 tokens each), converted to
numerical vectors, and stored in an index. When a question comes in,
it's also converted to a vector, and the most similar chunks are
retrieved. This is "semantic search" — it finds relevant content
even if the exact words don't match.

### Grounding = No Hallucination
Because we instructed the agent to ONLY use document content, it won't
make up answers. If the info isn't in the handbook, it says "I don't
have that information." That's the power of RAG for enterprise use.
