from datetime import date

from langchain_core.messages import SystemMessage, HumanMessage

from model import TravelState, QueryExtract
from llm import llm


def query_agent(state: TravelState):
    prompt = f"""
    You are a travel query extraction agent.

Extract the user's travel information according to these rules.

Use information explicitly mentioned whenever possible. The only fields you may infer when missing are budget, currency, passengers, departure_date, arrival_date, and return_date.

If only a country is mentioned as the destination, replace it with its capital city and infer the country from the destination city when necessary.

Resolve all relative dates (for example, "next Friday") into YYYY-MM-DD using today's date: {date.today()}.

If departure_date is missing, use today's date.
If arrival_date is missing, use today's date.
If return_date is missing, calculate it from the trip duration if one is mentioned; otherwise assume a 5-day trip.

Normalize budget values such as "60k" → 60000 and "1.5 lakh" → 150000.
If no budget is provided, estimate a reasonable mid-range total trip budget based on the departure city, destination, trip duration, and passenger count in INR.

If a currency is explicitly mentioned, return its ISO 4217 code. If the budget is estimated or a budget is provided without a currency, infer the currency from the departure country.

If the number of passengers is not mentioned, assume one adult passenger.

For airport codes, use the correct 3-letter IATA code when known. If you are not confident, return null rather than guessing.
If the departure city is not mentioned,
assume the traveler departs from Delhi, India.

Return:
departure_city_name = "Delhi"
departure_city_iata = "DEL"

Do NOT return null for the departure city.
Do not invent cities, countries, airport codes, or dates beyond the inference rules above.
"""
    query_llm = llm.with_structured_output(QueryExtract)
    query = state["user_query"]
    # FIX: prompt (system rules) was built but never sent to the LLM — only raw query was
    response = query_llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=query)
    ])
    print(response.model_dump())
    state.update(response.model_dump())
    print(state)
    return state