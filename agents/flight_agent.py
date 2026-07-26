import asyncio

from langchain_core.messages import AIMessage

from model import TravelState
from travel_mcp.mcp_client import flight_mcp_search


def flight_agent(state: TravelState):
    flight_data = asyncio.run(
        flight_mcp_search(
            state["arrival_city_iata"],
            state["departure_date"],
            state["return_date"],
            state["departure_city_iata"],
            state.get("passengers", 1),
            state.get("currency", "INR")
        )
    )

    print(flight_data)
    return {
        "flight_result": flight_data,
        "messages": [
            AIMessage(content="Flight results fetched")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }