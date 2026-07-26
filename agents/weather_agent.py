from langchain_core.messages import AIMessage

from model import TravelState
from tools.weather_tool import get_future_forecast


def weather_agent(state: TravelState):
    weather_result = get_future_forecast(
        state["arrival_city_name"], state["arrival_date"], state["return_date"]
    )
    print("weather", weather_result)
    return {
        "weather_result": weather_result,
        "messages": [
            AIMessage(content="Weather information fetched")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }