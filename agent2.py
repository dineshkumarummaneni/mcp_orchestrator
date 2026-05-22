from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
import asyncio
async def weather_agent():
    mcp_client=MultiServerMCPClient({
        "weather":{
            "transport":"http",
            "url": "http://localhost:8000/mcp"
        }
    })
    llm=ChatOllama(model="qwen2.5:7b")
    tools=await mcp_client.get_tools()
    agent=create_agent(model=llm,tools=tools)
    return agent
