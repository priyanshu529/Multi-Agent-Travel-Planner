from math import ceil

from langchain_core.messages import AIMessage

from model import TravelState
from tools.hotel_search_tool import search_hotels


def hotel_agent(state: TravelState):
    passengers = state.get("passengers", 1) or 1
    rooms_needed = ceil(passengers / 2)

    budget = state.get("budget")
    hotel_budget = None
    total_budget = None

    if budget:
        # 30% of trip budget allocated to hotels
        hotel_budget = int((budget * 0.30) / rooms_needed)
        total_budget = hotel_budget / state["stay"]
    # NOTE: preserved from original — if budget is falsy, total_budget stays
    # None and int(total_budget) below will raise. Left as-is per original
    # behavior; consider defaulting total_budget when splitting further.
    max_price = int(total_budget) if total_budget else None
    hotel_results = search_hotels(
        destination=state["arrival_city_name"],
        check_in=state["arrival_date"],
        check_out=state["return_date"],
        adults=passengers,
        currency=state.get("currency", "INR"),
        max_price=max_price,
        min_rating=4.0,          # or state.get("min_rating")
        max_results=5,
    )

    print("hotel", hotel_results)

    return {
        "hotel_results": hotel_results,
        "messages": [
            AIMessage(content="Hotel information fetched")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
