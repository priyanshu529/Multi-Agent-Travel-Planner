from langchain_core.messages import SystemMessage, HumanMessage

from model import TravelState
from llm import llm


def itinerary_agent(state: TravelState):
    print("entering itinerary")
    prompt = f"""
    create a travel itinerary based on the following data.
    User Query:{state['user_query']},
    Flight Results:{state["flight_result"]},
    Hotel Results:{state["hotel_results"]},
    weather results:{state.get("weather_result", "")}
"""
    try:
        response = llm.invoke([
            SystemMessage(
                content="You are an expert Travel planner create itinerary based on the given data and user's budget"
            ),
            HumanMessage(content=prompt)
        ])
    except Exception as e:
        print("ITINERARY ERROR:", e)
        raise
    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }