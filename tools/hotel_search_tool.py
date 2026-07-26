from serpapi import search
import os
from dotenv import load_dotenv
from pprint import pprint
load_dotenv()
import streamlit as st
SERPAPI_KEY = st.secrets["HOTEL_API_KEY"]


def search_hotels(
    destination: str,
    check_in: str,
    check_out: str,
    adults: int = 2,
    currency: str = "INR",
    max_price: int | None = None,
    min_rating: float | None = None,
    hotel_class: int | None = None,   # 3,4,5
    max_results: int = 5,
):
    params = {
        "engine": "google_hotels",
        "q": destination,
        "check_in_date": check_in,
        "check_out_date": check_out,
        "adults": adults,
        "currency": currency,
        "hl": "en",
        "api_key": SERPAPI_KEY,
    }

    # Optional Google Hotels filters
    if max_price is not None:
        params["max_price"] = max_price

    if min_rating is not None:
        params["min_rating"] = min_rating

    if hotel_class is not None:
        params["hotel_class"] = hotel_class

    result= search(params)
    results = result.as_dict()
    # pprint(results)

    hotels = []

    for hotel in results.get("properties", [])[:max_results]:
        rate = hotel.get("rate_per_night", {})
        gps = hotel.get("gps_coordinates", {})

        hotels.append({
            "name": hotel.get("name"),
            "price_per_night": rate.get("lowest"),
            "currency": rate.get("currency"),
            "rating": hotel.get("overall_rating"),
            "reviews": hotel.get("reviews"),
            "hotel_class": hotel.get("hotel_class"),
            "address": hotel.get("address"),
            "latitude": gps.get("latitude"),
            "longitude": gps.get("longitude"),
            "amenities": hotel.get("amenities", []),
            "booking_link": hotel.get("link"),
        })

    return hotels
