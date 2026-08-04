"""All shared data models: the LangGraph state schema and the Pydantic
models used for structured LLM output."""

from typing import TypedDict, Annotated, Optional
import operator

from langchain_core.messages import AnyMessage
from pydantic import BaseModel, Field


class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str


    input_rejected:bool
    rejection_reason: Optional[str]


    departure_city_name: Optional[str]
    departure_city_iata: Optional[str]
    arrival_city_name: Optional[str]
    arrival_city_iata: Optional[str]
    country_name: Optional[str]
    departure_date: Optional[str]
    arrival_date: Optional[str]
    return_date: Optional[str]
    passenger: Optional[int]
    budget: Optional[float]
    passengers: Optional[int]
    currency: Optional[str]
    stay: Optional[int]

    flight_result: str
    hotel_results: str
    weather_result: str
    itinerary: str
    final_result: str
    evaluation: dict
    max_iteration: int
    revision_count: int
    llm_calls: Annotated[int, operator.add]


class QueryExtract(BaseModel):
    departure_city_name: Optional[str] = Field(
        default="Delhi", description="Name of the home city, e.g. 'Delhi'"
    )
    departure_city_iata: Optional[str] = Field(
        default="DEL", description="IATA airport code of the departure city, e.g. 'DEL'"
    )
    arrival_city_name: Optional[str] = Field(
        None, description="Name of the destination city, e.g. 'Mumbai'"
    )
    arrival_city_iata: Optional[str] = Field(
        None, description="IATA airport code of the destination city, e.g. 'BOM'"
    )
    country_name: Optional[str] = Field(
        default="india", description="Destination country name, e.g. 'India'"
    )
    departure_date: Optional[str] = Field(
        None, description="Date of departure in YYYY-MM-DD format"
    )
    arrival_date: Optional[str] = Field(
        None, description="Date of arrival at destination in YYYY-MM-DD format"
    )
    return_date: Optional[str] = Field(
        None, description="Date of return in YYYY-MM-DD format"
    )
    budget: Optional[float] = Field(
        None, description="Total trip budget, if mentioned"
    )
    currency: Optional[str] = Field(
        None, description="currency should be in 3 letter standar eg USD,INR"
    )
    passengers: Optional[int] = Field(default=1, description="number of passengers")
    stay: Optional[int] = Field(description="number of days for trip stay")


class EvaluationResult(BaseModel):
    passed: bool
    confidence: float
    issues: list[str]
