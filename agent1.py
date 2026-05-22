from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
import asyncio


async def call_agent1():

    mcp_client = MultiServerMCPClient(
        {
            "math": {
                "transport": "stdio",
                "command": "python3",
                "args": ["math_server.py"]
            }
        }
    )

    llm = ChatOllama(
        model="qwen2.5:7b"
    )

    tools = await mcp_client.get_tools()

    agent = create_agent(
        model=llm,
        tools=tools
    )

    return agent
