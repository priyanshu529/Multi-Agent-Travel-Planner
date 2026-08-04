"""Builds and compiles the LangGraph state graph from the individual
agent nodes."""

from langgraph.graph import StateGraph, START, END

from model import TravelState
from db import checkpointer
from agents.query_extract import query_agent
from agents.flight_agent import flight_agent
from agents.hotel_agent import hotel_agent
from agents.weather_agent import weather_agent
from agents.itinerary_agent import itinerary_agent
from agents.final_agent import final_agent
from agents.evaluation_agent import evaluation_agent, evaluation_router
from agents.route_input_guardrail import route_input_guardrail
from agents.input_guardrail import input_guardrail

graph = StateGraph(TravelState)
graph.add_node("input_guardrail", input_guardrail)
graph.add_node("query_agent", query_agent)
graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("weather_agent", weather_agent)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("final_agent", final_agent)
graph.add_node("evaluation_agent", evaluation_agent)

graph.add_edge(START, "input_guardrail")
graph.add_conditional_edges("input_guardrail",route_input_guardrail,{
    "rejected": END,
    "approved": "query_agent"
})
graph.add_edge("query_agent", "flight_agent")
graph.add_edge("query_agent", "hotel_agent")
graph.add_edge("query_agent", "weather_agent")
graph.add_edge("flight_agent", "itinerary_agent")
graph.add_edge("hotel_agent", "itinerary_agent")
graph.add_edge("weather_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", "final_agent")
graph.add_edge("final_agent", "evaluation_agent")
graph.add_conditional_edges("evaluation_agent", evaluation_router, {
    "approved": END,
    "revise": "final_agent"
})

app = graph.compile(checkpointer=checkpointer)
