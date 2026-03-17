import requests
import random
from models.schemas import ClimateData
from dotenv import load_dotenv
import os

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

def fetch_weather(location: str) -> ClimateData:
    """
    Fetches weather data for a location. 
    Uses OpenWeather API if key is available, else returns mock data.
    """
    # If no key or mock key, return dummy data
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY.startswith("your_"):
        return get_mock_weather(location or "Gujarat")

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location or 'Gujarat'}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        return ClimateData(
            location=data.get('name', location),
            temperature=data['main']['temp'],
            rainfall=data.get('rain', {}).get('1h', 0.0),
            humidity=data['main']['humidity'],
            wind_speed=data['wind']['speed'],
            weather_condition=data['weather'][0]['description']
        )
    except Exception as e:
        print(f"Weather API failed: {e}. Falling back to mock data.")
        return get_mock_weather(location or "Gujarat")

def get_mock_weather(location: str) -> ClimateData:
    """Returns realistic mock weather data."""
    is_raining = random.choice([True, False])
    return ClimateData(
        location=location,
        temperature=round(random.uniform(25.0, 38.0), 1),
        rainfall=round(random.uniform(10.0, 45.0), 1) if is_raining else 0.0,
        humidity=random.randint(40, 95),
        wind_speed=round(random.uniform(5.0, 20.0), 1),
        weather_condition="Rainy" if is_raining else "Clear Sky"
    )
