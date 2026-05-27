from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain.tools import tool
import os


@tool
async def push_changes(commit_message: str):
    """
    Push all local code changes to GitHub repository.
    """

    mcp_client = MultiServerMCPClient({
        "gitserver": {
            "transport": "stdio",
            "command": "npx",
            "args": ["@cyanheads/git-mcp-server@latest"]
        }
    })

    tools = await mcp_client.get_tools()
    
    tool_map = {
        t.name: t
        for t in tools
    }
    print("git add args",tool_map["git_add"].args)
    current_dir = os.getcwd()

    print("Setting workspace...")

    await tool_map["git_set_working_dir"].ainvoke({
        "path": current_dir
    })

    print("Checking git status...")

    status = await tool_map["git_status"].ainvoke({
        "path": current_dir
    })

    print(status)

    print("Pulling latest code...")

    pull_result = await tool_map["git_pull"].ainvoke({
        "path": current_dir
    })

    print(pull_result)

    print("Adding files...")

    add_result = await tool_map["git_add"].ainvoke({
        "path": current_dir,
        "paths": ["."]
    })

    print(add_result)

    print("Creating commit...")

    commit_result = await tool_map["git_commit"].ainvoke({
        "path": current_dir,
        "message": commit_message
    })

    print(commit_result)

    print("Pushing code...")

    push_result = await tool_map["git_push"].ainvoke({
        "path": current_dir
    })

    print(push_result)

    return "Code pushed successfully."


async def gitserver():

    llm = ChatOllama(model="qwen2.5:7b")

    agent = create_agent(
        model=llm,
        tools=[push_changes]
    )

    response = await agent.ainvoke({
        "messages": [{
            "role": "user",
            "content": """
            Push all repository changes.

            Commit message:
            Added new MCP orchestration logic
            """
        }]
    })

    print(response["messages"][-1].content)


asyncio.run(gitserver())