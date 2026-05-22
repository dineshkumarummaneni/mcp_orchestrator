from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain.tools import tool
from agent1 import call_agent1
from agent2 import weather_agent
import asyncio
import json
from langchain_core.messages import (
    SystemMessage,
    HumanMessage
)
async def main():
    agent1=await call_agent1()
    agent2=await weather_agent()
    @tool
    async def agent1_as_tool(query):
        """
        description: this is the agent1 that is capable to do mathematical operations
        """
        response=await agent1.ainvoke(
        {"messages": [{"role": "user", "content": query}]})
        return response["messages"][-1].content
    @tool
    async def agent2_as_tool(query):
        """
        description: this agent is responsble for weather fetching tools and weather related queries
        """
        response=await agent2.ainvoke(
            {"messages": [{"role": "user", "content": query}]}
        )
        return response["messages"][-1].content
    llm=ChatOllama(model="qwen2.5:7b")

    orchestroter_agent=create_agent(model=llm,tools=[agent1_as_tool,agent2_as_tool])
    planner_prompt="""
    You are a planner agent.

Break the user query into ordered executable tasks.

Available agents:
- math_agent
- weather_agent
list of json
json structure -
{
"step": "what is the step number sequence" example 1 or 2 or 3
"agent":"what is the agent need for this step of input"
"input":"input at current step"

}

Return JSON array only.
    """
    query=input("enter the query\n")
    planner_response = llm.invoke([
    SystemMessage(content=planner_prompt),
    HumanMessage(content=query)
            ])
    
    
    current_response=""
    
    tasks=json.loads(planner_response.content)
    for res in tasks:
        step=res['step']
        agent=res['agent']
        query_at_step=res['input']
        # final_query="for step"+str(step)+"this agent is useful"+str(agent)+"for the user query"+str(query_at_step)
        response=await orchestroter_agent.ainvoke({
            "messages":[{"role":"user","content":query_at_step}]
        })
        print(response["messages"][-1].content)
        current_response+=response["messages"][-1].content
    response=llm.invoke([SystemMessage(
        content="""
You are a response synthesizer.

Combine all agent outputs into
one coherent final response.
"""
    ),
    HumanMessage(
        content=f"""
Original User Query:
{query}

Execution Results:
{current_response}
"""
    )])
    print(response.content)
if __name__=="__main__":
    asyncio.run(main())

# what is weather of texas and if distance from texas to New Mexico distance is 30 miles and new mexcio to New Mexico distance is 40 miles how much i need to travel to reach from texas to mexico
