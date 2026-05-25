from langchain_ollama import ChatOllama
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
import os
from dotenv import load_dotenv
load_dotenv()
async def github_mcp_client():
    github_client=MultiServerMCPClient({
        "github":{
            "transport":"stdio",
            "command":"npx",
            "args":[
                "-y",
                "@modelcontextprotocol/server-github"
            ],
            "env":{
                "GITHUB_PERSONAL_ACCESS_TOKEN":os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
            }
        }
    })
    tools=await github_client.get_tools()
    for tool in tools:

        if tool.name == "search_repositories":

            response = await tool.ainvoke({

                "query":
                "user:dineshkumarummaneni"
            })

            print(response.content)
    llm=ChatOllama(model="qwen2.5:7b")
    agent = create_agent(

    model=llm,

    tools=tools,

    system_prompt="""
        You are a GitHub assistant.

        Use valid GitHub search syntax.

        Examples:
        - user:username
        - repo:owner/repo
        - org:organization

        Do not generate invalid search qualifiers.
        """
        )
    # response=await agent.ainvoke({
    #     "messages":[{
    #         "role":"user",
    #         "content":"Use search_repositories to find repositories for user:dineshkumarummaneni"
    #     }
        
    # ]})
    # print(response["messages"][-1].content)
asyncio.run(github_mcp_client())
