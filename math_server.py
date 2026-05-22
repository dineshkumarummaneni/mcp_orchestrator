from fastmcp import FastMCP
import pydantic
mcp_server=FastMCP("Math")

@mcp_server.tool()
def addition(a:int,b:int):
    """
    This is the additio function thet add two numbers
    a: first argument
    b: second argument
    """
    return a+b
mcp_server.tool()
def multiplication(a:int,b:int):
    """
    This is the additio function thet add two numbers
    a: first argument
    b: second argument
    """
    return a*b

if __name__=="__main__":
    mcp_server.run(transport="stdio")