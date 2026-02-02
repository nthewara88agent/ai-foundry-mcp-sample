#!/usr/bin/env python3
"""
Azure AI Foundry Agent Service - MCP Tool Integration Sample

This sample demonstrates how to create an AI Agent that uses the Microsoft Learn
MCP (Model Context Protocol) server to search documentation and code samples.

The agent is created once and reused across runs. Each run creates a new thread
for conversation history.

Requirements:
- Azure AI Foundry resource with a deployed model (gpt-4o-mini recommended)
- Azure CLI authentication (run `az login` first)
- Azure AI User role on the AI Foundry resource

Note: MCP tools require the beta SDK version (azure-ai-agents>=1.2.0b6)
"""

import os
import time
from dotenv import load_dotenv

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import (
    ListSortOrder,
    McpTool,
    RequiredMcpToolCall,
    SubmitToolApprovalAction,
    ToolApproval,
)

# Load environment variables
load_dotenv()

# Configuration from environment
PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT", "")
MODEL_DEPLOYMENT_NAME = os.environ.get("MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "https://learn.microsoft.com/api/mcp")
MCP_SERVER_LABEL = os.environ.get("MCP_SERVER_LABEL", "microsoft_learn")

# Persistent agent name - will be created once and reused
AGENT_NAME = "mcp-docs-assistant"


def get_or_create_agent(agents_client, mcp_tool):
    """
    Get existing agent by name or create a new one.
    Returns the agent instance.
    """
    # List existing agents and find by name
    # Handle different SDK versions (list_agents vs get_agents)
    try:
        agents = list(agents_client.list_agents())
    except AttributeError:
        # Older SDK version uses get_agents or different method
        try:
            agents = list(agents_client.get_agents())
        except AttributeError:
            agents = []
    for agent in agents:
        if agent.name == AGENT_NAME:
            print(f"📌 Using existing agent: {agent.id}")
            return agent
    
    # Create new agent if not found
    print(f"🆕 Creating new agent: {AGENT_NAME}")
    agent = agents_client.create_agent(
        model=MODEL_DEPLOYMENT_NAME,
        name=AGENT_NAME,
        instructions="""You are a helpful documentation assistant that specializes in 
Microsoft Azure and .NET documentation. You have access to the Microsoft Learn 
documentation through MCP tools.

Available tools:
- microsoft_docs_search: Search for documentation on any Microsoft topic
- microsoft_code_sample_search: Find code samples in various programming languages
- microsoft_docs_fetch: Fetch the complete content of a specific documentation page

IMPORTANT: Always use the MCP tools to search Microsoft Learn documentation before 
answering questions. Do not rely solely on your training data - use the tools to 
get the latest, accurate information from official Microsoft documentation.

When users ask questions about Azure, .NET, or Microsoft products:
1. Use microsoft_docs_search to find relevant documentation
2. Use microsoft_code_sample_search to find code examples when appropriate
3. Provide clear, helpful summaries based on the documentation

Always cite the source URLs when providing information from documentation.""",
        tools=mcp_tool.definitions,
    )
    print(f"✅ Created agent: {agent.id}")
    return agent


def run_conversation(agents_client, agent, mcp_tool, user_message: str):
    """
    Run a conversation with the agent using the MCP tool.
    Creates a new thread for each conversation.
    """
    print(f"\n{'='*60}")
    print(f"💬 User: {user_message}")
    print("="*60)
    
    # Create a thread for the conversation
    thread = agents_client.threads.create()
    print(f"\n📝 Created thread: {thread.id}")
    
    # Add the user's message to the thread
    message = agents_client.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message,
    )
    
    # Auto-approve MCP tool calls
    mcp_tool.set_approval_mode("never")
    
    # Create and run the agent
    run = agents_client.runs.create(
        thread_id=thread.id,
        agent_id=agent.id,
        tool_resources=mcp_tool.resources,
    )
    print(f"🚀 Created run: {run.id}")
    
    # Poll for completion
    while run.status in ["queued", "in_progress", "requires_action"]:
        time.sleep(1)
        run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)
        
        # Handle manual approval if needed
        if run.status == "requires_action" and isinstance(run.required_action, SubmitToolApprovalAction):
            tool_calls = run.required_action.submit_tool_approval.tool_calls
            
            if not tool_calls:
                print("⚠️ No tool calls provided - cancelling run")
                agents_client.runs.cancel(thread_id=thread.id, run_id=run.id)
                break
            
            tool_approvals = []
            for tool_call in tool_calls:
                if isinstance(tool_call, RequiredMcpToolCall):
                    print(f"   🔧 Tool call: {tool_call.name}")
                    tool_approvals.append(
                        ToolApproval(
                            tool_call_id=tool_call.id,
                            approve=True,
                            headers=mcp_tool.headers,
                        )
                    )
            
            if tool_approvals:
                agents_client.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_approvals=tool_approvals,
                )
        
        print(f"   Status: {run.status}", end="\r")
    
    print(f"\n✅ Run completed: {run.status}")
    
    if run.status == "failed":
        print(f"❌ Run failed: {run.last_error}")
    else:
        # Get run steps to see tool usage
        run_steps = agents_client.run_steps.list(thread_id=thread.id, run_id=run.id)
        for step in run_steps:
            step_details = step.get("step_details", {})
            tool_calls = step_details.get("tool_calls", [])
            for call in tool_calls:
                if call.get("type") == "mcp":
                    print(f"   🔧 Used tool: {call.get('name', 'unknown')}")
        
        # Fetch and display messages
        messages = agents_client.messages.list(
            thread_id=thread.id,
            order=ListSortOrder.ASCENDING,
        )
        
        print("\n" + "-"*60)
        print("📨 Response:")
        print("-"*60)
        
        for msg in messages:
            if msg.role == "assistant" and msg.text_messages:
                for text_msg in msg.text_messages:
                    print(f"\n{text_msg.text.value}")
        
        print("\n" + "-"*60)
    
    print(f"\n📌 Thread preserved: {thread.id}")
    return thread.id


def main():
    """Main entry point."""
    
    print("\n🚀 Azure AI Foundry MCP Sample")
    print(f"   Project: {PROJECT_ENDPOINT}")
    print(f"   Model: {MODEL_DEPLOYMENT_NAME}")
    
    # Validate endpoint format
    if not PROJECT_ENDPOINT or "services.ai.azure.com" not in PROJECT_ENDPOINT:
        print("\n⚠️  WARNING: The PROJECT_ENDPOINT should be a Foundry project endpoint")
        print("   Expected format: https://<resource>.services.ai.azure.com/api/projects/<project>")
        print("   Current value:", PROJECT_ENDPOINT)
        return
    
    print("=" * 60)
    print("Azure AI Foundry Agent with Microsoft Learn MCP Tool")
    print("=" * 60)
    
    # Initialize the MCP tool
    mcp_tool = McpTool(
        server_label=MCP_SERVER_LABEL,
        server_url=MCP_SERVER_URL,
        allowed_tools=[
            "microsoft_docs_search",
            "microsoft_code_sample_search", 
            "microsoft_docs_fetch"
        ],
    )
    
    print(f"\n📡 MCP Server: {MCP_SERVER_LABEL}")
    print(f"   URL: {MCP_SERVER_URL}")
    print(f"   Allowed tools: {mcp_tool.allowed_tools}")
    
    # Create the project client
    credential = DefaultAzureCredential()
    project_client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=credential,
    )
    
    try:
        with project_client:
            agents_client = project_client.agents
            
            # Get or create the persistent agent
            agent = get_or_create_agent(agents_client, mcp_tool)
            
            # Run a sample conversation
            user_question = "Use the microsoft_docs_search tool to search Microsoft Learn for 'Azure Functions Python quickstart'. Summarize what you find."
            
            run_conversation(agents_client, agent, mcp_tool, user_question)
        
        print("\n✅ Sample completed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        if "PermissionDenied" in str(e):
            print("\n💡 Tip: You need 'Azure AI User' role on the AI Foundry resource.")
        elif "rate_limit" in str(e).lower():
            print("\n💡 Tip: Rate limit hit. Wait a minute and try again.")


if __name__ == "__main__":
    main()
