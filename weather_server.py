from  fastmcp import FastMCP
weather_server=FastMCP("weather")
@weather_server.tool()
def weather_api(location:str):
    return f"The current weather of {location} is cool"
if __name__=="__main__":
    weather_server.run(transport="http")