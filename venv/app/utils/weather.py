import httpx
from dotenv import load_dotenv
import os

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

async def get_weather(city: str) -> dict:
    """
    Fetch weather data for a given city from OpenWeatherMap.
    """
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric"  # For Celsius; use "imperial" for Fahrenheit
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(WEATHER_API_URL, params=params)
        
        if response.status_code != 200:
            raise Exception(f"Weather API error: {response.json().get('message', 'Unknown error')}")
        
        data = response.json()
        return {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"]
        }