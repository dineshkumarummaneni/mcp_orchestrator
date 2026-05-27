
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
async def push_changes():
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
    print(tool_map["git_add"].args)
asyncio.run(push_changes())