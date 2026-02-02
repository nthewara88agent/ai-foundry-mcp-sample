#!/usr/bin/env python3
"""
Azure AI Foundry Agent - Microsoft Agent Framework with MCP Tools

This sample demonstrates how to create an AI Agent using the Microsoft Agent Framework
with the Microsoft Learn MCP (Model Context Protocol) server for documentation search.

Requirements:
- agent-framework (pip install agent-framework --pre)
- Azure CLI authentication (run `az login` first)
- Azure AI Foundry project with deployed model

The Agent Framework is the latest Microsoft SDK for building AI agents with:
- Async-first design
- Built-in MCP tool support
- Multiple providers (Azure AI, OpenAI, GitHub Models)
"""

import asyncio
import os

from dotenv import load_dotenv
from agent_framework import MCPStreamableHTTPTool
from agent_framework.azure import AzureAIAgentsProvider
from azure.identity.aio import AzureCliCredential

# Load environment variables
load_dotenv()

# Azure AI Foundry Configuration
PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT") or os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "")
MODEL_DEPLOYMENT = os.environ.get("MODEL_DEPLOYMENT_NAME") or os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")

# MCP Server Configuration
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "https://learn.microsoft.com/api/mcp")
MCP_SERVER_NAME = os.environ.get("MCP_SERVER_NAME", "Microsoft Learn MCP")


async def run_with_mcp_tools():
    """
    Create an Azure AI Agent with Microsoft Learn MCP tools.
    
    The agent uses the AzureAIAgentsProvider which automatically connects to your
    Azure AI Foundry project using Azure CLI credentials.
    """
    print("\n🚀 Microsoft Agent Framework - MCP Tools Demo")
    print("=" * 60)
    print(f"📡 MCP Server: {MCP_SERVER_NAME}")
    print(f"   URL: {MCP_SERVER_URL}")
    print(f"   Project: {PROJECT_ENDPOINT}")
    print("=" * 60)
    
    async with (
        AzureCliCredential() as credential,
        AzureAIAgentsProvider(
            credential=credential,
            project_endpoint=PROJECT_ENDPOINT,
        ) as provider,
    ):
        # Create agent with MCP tool attached at agent level
        agent = await provider.create_agent(
            name="docs-assistant",
            model=MODEL_DEPLOYMENT,
            instructions="""You are a helpful documentation assistant that specializes in 
Microsoft Azure and .NET documentation. You have access to the Microsoft Learn 
documentation through MCP tools.

IMPORTANT: Always use the MCP tools to search Microsoft Learn documentation before 
answering questions. Do not rely solely on your training data - use the tools to 
get the latest, accurate information from official Microsoft documentation.

When users ask questions:
1. Use the MCP tools to search for relevant documentation
2. Provide clear, helpful summaries based on what you find
3. Always cite the source URLs""",
            tools=MCPStreamableHTTPTool(
                name=MCP_SERVER_NAME,
                url=MCP_SERVER_URL,
            ),
        )
        
        print(f"\n✅ Created agent: {agent.name}")
        
        # Use agent context manager to connect MCP tools
        async with agent:
            # Example queries
            queries = [
                "Search Microsoft Learn for 'Azure Functions Python quickstart' and summarize the key steps.",
                "What is Microsoft Agent Framework? Search the docs.",
            ]
            
            for query in queries:
                print(f"\n{'='*60}")
                print(f"💬 User: {query}")
                print("-" * 60)
                
                result = await agent.run(query)
                
                print(f"\n📨 {agent.name}:")
                print(result)
                print("=" * 60)
    
    print("\n✅ Demo completed!")


async def run_simple_query(query: str):
    """
    Simple function to run a single query against the docs agent.
    """
    async with (
        AzureCliCredential() as credential,
        AzureAIAgentsProvider(
            credential=credential,
            project_endpoint=PROJECT_ENDPOINT,
        ) as provider,
    ):
        agent = await provider.create_agent(
            name="docs-assistant",
            model=MODEL_DEPLOYMENT,
            instructions="You are a helpful documentation assistant. Use MCP tools to search Microsoft Learn.",
            tools=MCPStreamableHTTPTool(
                name=MCP_SERVER_NAME,
                url=MCP_SERVER_URL,
            ),
        )
        
        async with agent:
            result = await agent.run(query)
            return result


async def main():
    """Main entry point."""
    try:
        await run_with_mcp_tools()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        if "PermissionDenied" in str(e):
            print("\n💡 Tip: You need 'Azure AI User' role on the AI Foundry resource.")
        elif "az login" in str(e).lower() or "credential" in str(e).lower():
            print("\n💡 Tip: Run 'az login' first to authenticate with Azure.")


if __name__ == "__main__":
    asyncio.run(main())
