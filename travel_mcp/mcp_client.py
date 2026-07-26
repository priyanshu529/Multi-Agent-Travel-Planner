from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
import os
import asyncio
import sys
import json

def get_loop_factory():
    if sys.platform == "win32":
        return asyncio.ProactorEventLoop
    return None
load_dotenv()

SERPAPI_KEY=os.getenv("SERPAPI_KEY")

client=MultiServerMCPClient(
    {
          
         "travelpayouts-custom": {
            "command": "python",
            "args": [r"C:\\Users\\Priyanshu2006\\Desktop\\travel agent\\travel_mcp\\mcp_server.py"],
            "transport": "stdio"
        }
                }
)




flight_tools={}

async def initialize_mcp():
    global search_tool
    global flight_tools
    
    tools=await client.get_tools()
    
    
    required_flight_tools = ["search_flights_prices"]

    flight_tools={
            tool.name:tool
            for tool in tools
            if tool.name in required_flight_tools
        }
    if len(flight_tools)<len(required_flight_tools):
        raise RuntimeError(
            f""""only {len(flight_tools)} flight_tools are loaded:\n"""
             f"Found: {list(flight_tools.keys())}"
        )




async def flight_mcp_search(destination, depart_date, ret_date=None, origin="DEL", passengers=1,currency="INR"):

    await initialize_mcp()  # make sure flight_tools is populated first

    one_way = ret_date is None

    search_args = {
        "origin": origin,
        "destination": destination,
        "departure_at": depart_date,
        "one_way": one_way,
        "currency": currency,
        "limit": 5,
    }
    if not one_way:
        search_args["return_at"] = ret_date

    exact_result = await flight_tools["search_flights_prices"].ainvoke(search_args)

    return f"""
    requested_date:
    date:{depart_date},
    "flight":{exact_result}
"""