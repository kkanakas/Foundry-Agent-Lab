# Demo Script: Toolbox Demo

## Setup (before audience arrives)

1. Open cmd at the repo root (`foundry-agent-lab`)
2. Run `az login` once
3. Verify you have a project connection configured for the GitHub MCP server
4. Confirm `PROJECT_ENDPOINT` is set in `.env`

## Talking Points

### Opening (30 sec)
> "As you scale AI agents across an organization, teams re-implement the same
> tools independently. Credentials get duplicated, governance is inconsistent.
> Toolbox solves this — define tools once, centrally, and expose them as a
> single MCP-compatible endpoint any agent can consume."

### Show the code (2 min)
- Open `create_agent.py` — point out:
  - `project.beta.toolboxes.create_version(...)` — the new API
  - Two `MCPTool(...)` entries with `allowed_tools` — curated subsets from one server
  - `"github-issues"` group: list, read, write, search issues
  - `"github-repos"` group: search repos, get files, list branches/commits/tags
  - "Same underlying MCP server, but we govern WHICH tools are approved"
- Open `chat.py` — point out:
  - **MAF pattern**: bearer-token auth with `get_bearer_token_provider`
  - `streamablehttp_client` + `ClientSession` — standard MCP client connecting to toolbox
  - `ALLOWED_TOOLS` set — client-side curation (12 tools from 45 on server)
  - `session.call_tool(...)` — executes tools through the toolbox MCP endpoint
  - "The difference from Demo 6: here tools are curated centrally in a Toolbox,
    discovered dynamically, and governed by the platform team"

### Run it (4 min)
```cmd
7-toolbox-demo
```

### Suggested prompts (in this order!)
1. "Search for repositories about agent framework from microsoft" (repo tools)
2. "List the 5 most recent issues in Azure/azure-sdk-for-python" (issue tools)
3. "Get the README.md from microsoft/semantic-kernel" (file contents)

### Key observations to call out
> "We only expose 12 tools to the model, curated from 45 on the server.
> The platform team decides which tools each agent gets access to."

> "Watch the approval step — you see which tool the toolbox is invoking.
> chat.py asks you to approve before calling `session.call_tool()`.
> This is centralized governance in action."

> "The toolbox is versioned. If I update the tools (add AI Search, remove
> an issue tool), I create a new version and promote it when ready.
> chat.py re-discovers tools dynamically via `list_tools()` — no code changes."

> "Compare to Demo 6 — there, the agent connected directly to one MCP server.
> Here, the toolbox AGGREGATES and CURATES tools behind one facade."

### Demonstrate versioning concept (talk-through)
> "In production, you'd have a Platform team managing toolbox versions.
> v1 might expose read-only GitHub tools. v2 adds write access for issues.
> They test v2, then promote it to default. Every consumer using that
> toolbox gets the new tools instantly — no client code changes."

### Exit
Type `exit` — session ends cleanly.

## If something goes wrong

**"Unauthorized" or empty tool list**: Your project connection credentials may be
expired. Update the connection in Foundry portal.

**Toolbox creation fails**: Ensure your project is in a supported region for
toolbox preview. See the docs for region compatibility.

**No approval requests appear**: The agent may answer from general knowledge.
Ask something that specifically requires GitHub data (repos, issues, code).

**Agent leftover from previous run**:
```cmd
toolbox-demo\reset.bat
```

## Duration
~5-6 minutes total
