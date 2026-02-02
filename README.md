# Azure AI Foundry Agent - Microsoft Agent Framework with MCP

Sample demonstrating AI agents with MCP (Model Context Protocol) tools using the **Microsoft Agent Framework**.

## Features

- Uses the latest **Microsoft Agent Framework** (async-first design)
- Integrates with **Microsoft Learn MCP server** for documentation search
- Runs on **Azure AI Foundry** with managed agents

## Prerequisites

- Python 3.10+
- Azure CLI authenticated (`az login`)
- Azure AI Foundry project with a deployed model (e.g., gpt-4o-mini)
- Azure AI User role on the AI Foundry resource

## Quick Start

```bash
# Clone the repo
git clone https://github.com/nthewara88agent/ai-foundry-mcp-sample.git
cd ai-foundry-mcp-sample

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Azure AI Foundry project endpoint

# Run the sample
python main.py
```

## Configuration

Create a `.env` file with:

```env
PROJECT_ENDPOINT=https://<your-resource>.services.ai.azure.com/api/projects/<your-project>
MODEL_DEPLOYMENT_NAME=gpt-4o-mini
MCP_SERVER_URL=https://learn.microsoft.com/api/mcp
MCP_SERVER_NAME=Microsoft Learn MCP
```

Or use environment variables:
- `AZURE_AI_PROJECT_ENDPOINT` - Your Azure AI Foundry project endpoint
- `AZURE_AI_MODEL_DEPLOYMENT_NAME` - Deployed model name

## How It Works

The sample uses:
- `AzureAIAgentsProvider` - Manages Azure AI Foundry agent lifecycle
- `MCPStreamableHTTPTool` - Connects to MCP servers for tool discovery
- `agent.run()` - Async agent invocation with automatic tool execution

## MCP Tools Available

The Microsoft Learn MCP server provides:
- `microsoft_docs_search` - Search documentation
- `microsoft_code_sample_search` - Find code examples
- `microsoft_docs_fetch` - Fetch full documentation pages

## Resources

- [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/)
- [Azure AI Foundry](https://ai.azure.com)
- [MCP Protocol](https://modelcontextprotocol.io)
