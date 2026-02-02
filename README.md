# Azure AI Foundry Agent Service - MCP Tool Sample

This sample demonstrates how to create an AI Agent using Azure AI Foundry Agent Service that integrates with the Microsoft Learn MCP (Model Context Protocol) server to search documentation and code samples.

## Features

- 🤖 Creates an AI Agent with MCP tool capabilities
- 📚 Searches Microsoft Learn documentation
- 💻 Finds code samples in Python, C#, JavaScript, and more
- 🔗 Fetches complete documentation pages
- ✅ Auto-approval mode for seamless tool calls

## Prerequisites

1. **Azure Account** with access to Azure AI Foundry
2. **Azure CLI** installed and authenticated (`az login`)
3. **Python 3.10+** installed
4. **Azure AI Foundry resource** with a deployed model (gpt-4o-mini or gpt-4o)

## Quick Start

### 1. Clone and Setup

```bash
cd ai-foundry-mcp-sample
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and update with your values:

```bash
cp .env.example .env
```

Edit `.env` with your Azure AI Foundry endpoint:

```env
PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/
MODEL_DEPLOYMENT_NAME=gpt-4o-mini
MCP_SERVER_URL=https://learn.microsoft.com/api/mcp
MCP_SERVER_LABEL=microsoft-learn
```

### 3. Run the Sample

```bash
python main.py
```

## How It Works

### MCP (Model Context Protocol)

MCP is an open standard that allows AI models to access external tools. The Microsoft Learn MCP server provides three tools:

| Tool | Description |
|------|-------------|
| `microsoft_docs_search` | Search Microsoft Learn docs, returns up to 10 content chunks |
| `microsoft_code_sample_search` | Find code snippets in specific languages |
| `microsoft_docs_fetch` | Fetch complete markdown content of a docs page |

### Agent Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Your Application                      │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Azure AI Foundry Agent Service              │
│  ┌─────────────────────────────────────────────────────┐ │
│  │                    AI Agent                          │ │
│  │  - Model: gpt-4o-mini                               │ │
│  │  - Tools: MCP (Microsoft Learn)                     │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Microsoft Learn MCP Server                  │
│              https://learn.microsoft.com/api/mcp        │
└─────────────────────────────────────────────────────────┘
```

## Code Example

```python
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import McpTool
from azure.identity import DefaultAzureCredential

# Initialize MCP tool
mcp_tool = McpTool(
    server_label="microsoft-learn",
    server_url="https://learn.microsoft.com/api/mcp",
    allowed_tools=[
        "microsoft_docs_search",
        "microsoft_code_sample_search",
    ],
)

# Create project client
client = AIProjectClient(
    endpoint="https://your-resource.services.ai.azure.com/",
    credential=DefaultAzureCredential(),
)

# Create agent with MCP tool
agent = client.agents.create_agent(
    model="gpt-4o-mini",
    name="docs-assistant",
    instructions="You are a helpful documentation assistant...",
    tools=mcp_tool.definitions,
)
```

## Tool Approval

By default, MCP tool calls require approval. You can configure this:

```python
# Auto-approve all tool calls
mcp_tool.set_approval_mode("never")

# Require approval for all calls (default)
mcp_tool.set_approval_mode("always")
```

## Troubleshooting

### Authentication Errors

Make sure you're logged in with Azure CLI:
```bash
az login
```

### Model Not Found

Ensure you have a model deployed in your Azure AI Foundry resource. Check available models:
```bash
az cognitiveservices account deployment list \
  --name your-ai-foundry-resource \
  --resource-group your-resource-group
```

### MCP Tool Errors

The Microsoft Learn MCP server is public and doesn't require authentication. If you're using other MCP servers, you may need to pass headers:

```python
mcp_tool.update_headers("Authorization", "Bearer your-token")
```

## Resources

- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-foundry/)
- [MCP Tool Reference](https://learn.microsoft.com/azure/ai-foundry/agents/how-to/tools/model-context-protocol)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Azure AI Projects SDK](https://pypi.org/project/azure-ai-projects/)

## License

MIT
