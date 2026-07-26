import requests
from datetime import date, timedelta

def get_weather_by_city(city_name):
    # Step 1: geocode
    geo = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city_name, "count": 1}
    ).json()
    
    if "results" not in geo:
        return f"No location found for {city_name}"
    
    place = geo["results"][0]
    return  place["latitude"], place["longitude"]
    
    # Step 2: get weather
def get_future_forecast(city_name, start_date, end_date):
    lat,lon=get_weather_by_city(city_name)

    max_date = date.today() + timedelta(days=15)
    if date.fromisoformat(end_date) > max_date:
        params = {
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,precipitation_sum,weather_code",
                "hourly": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation_probability,weather_code",
                "timezone": "auto",
                "start_date": start_date if date.fromisoformat(start_date) < max_date else str(date.today() + timedelta(days=7)),   # "YYYY-MM-DD"
                "end_date": max_date
            }
        response = requests.get("https://api.open-meteo.com/v1/forecast", params=params)
        return response.json()
        

    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,precipitation_sum,weather_code",
        "hourly": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation_probability,weather_code",
        "timezone": "auto",
        "start_date": start_date,   # "YYYY-MM-DD"
        "end_date": end_date
    }
    response = requests.get("https://api.open-meteo.com/v1/forecast", params=params)
    return f" weather data: {response.json()}"
