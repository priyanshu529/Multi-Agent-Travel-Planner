from langchain_core.messages import HumanMessage

from model import TravelState
from llm import llm


def final_agent(state: TravelState):
    verification = state.get("evaluation")

    if verification and not verification["passed"]:
        final_prompt = f"""
The previous travel plan failed verification.
{state["final_result"]}
Issues:
{chr(10).join("- " + issue for issue in verification["issues"])}

The previous travel plan failed verification.

Revise the travel plan using the issues below.

Return the COMPLETE travel plan again in the exact same format.
Do not return only the changed sections.
Keep all correct information unchanged.
"""

    else:
        final_prompt = f"""
You are a professional travel planner.

Your task is to combine the flight results, hotel recommendations, weather, and itinerary into ONE concise, well-formatted travel plan.

Requirements:
- Use Markdown.
- Keep the response under 3000-4000 words.
- Do NOT explain your reasoning.
- Do NOT repeat information.
- Do NOT invent data — use only what is provided below. If a field is missing, write "N/A".
- Be concise and practical.

Format exactly like this:

# 🌏 Trip Summary
- Destination:
- Duration:
- Travelers:
- Budget:

# ✈️ Flights
note: Flight prices should be based on number of people from the query. If not provided, assume passengers = 1.
Show only a single round-trip flight option. Multiply the base fare by the number of passengers to get the total price.
provide 3-4 airline results(not estimated) from the flight_result
| Airline | Route(round trip) | Departure | Arrival | Duration | Stops | Price (Total) |
|---|---|---|---|---|---|---|
| | | | | | | |

# 🏨 Hotels
note: Prices should be based on number of people from the query (per room / total, whichever is available) and number of nights. If not provided, assume passengers = 1.
provide 3-4 hotel results (not estimated) from hotel_results
| City | Hotel | Price (per night) | Rating | Notes | url
|---|---|---|---|---|
| | | | | |
 give total price as price_per_night * no of days of stay
# 🌤️ Weather
Show weather for the destination during the travel dates (if available).

| Day | Temperature | Feels Like | Humidity | Forecast |
|---|---|---|---|---|
| | | | | |

If only current/general weather is available (not day-wise), show:
- Temperature:
- Feels Like:
- Humidity:
- Forecast:

# 📅 Itinerary
## Day 1
- Morning:
- Afternoon:
- Evening:
- Night:

## Day 2
- Morning:
- Afternoon:
- Evening:
- Night:

(...continue for all days in the trip duration)
note:if you dont have any itinerary for a specific time(eg evening,night) dont include it or add back to hotel or something rather than saying N/A
# 💰 Estimated Budget
| Category | Cost |
|---|---|
| Flights | |
| Hotels | |
| Food (estimate) | |
| Activities (estimate) | |

Total Estimated Cost:
Remaining Budget:

# 💡 Travel Tips
- 3-5 short, practical tips only (weather-appropriate packing, local transport, currency, etc.)

Use only the information provided below.

Flights:
{state["flight_result"]}

Hotels:
{state["hotel_results"]}

Itinerary:
{state["itinerary"]}

Weather:
{state["weather_result"]}
"""
    response = llm.invoke([
        HumanMessage(content=final_prompt)
    ])

    content = response.content

    if isinstance(content, list):
        final_text = "\n".join(
            block["text"]
            for block in content
            if block.get("type") == "text"
        )
    else:
        final_text = content

    return {
        "final_result": final_text,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }