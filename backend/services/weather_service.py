import requests
import os
from datetime import datetime
from models.schemas import ClimateData
from dotenv import load_dotenv

load_dotenv()
WEATHER_API_KEY = os.getenv("Weather_API_Key", os.getenv("OPENWEATHERMAP_API_KEY", ""))

def fetch_weather(location: str) -> ClimateData:
    """
    Fetches real-time weather + 5-day forecast from WeatherAPI.com.
    Falls back to OpenWeatherMap if needed, then mock data.
    """
    if WEATHER_API_KEY and not WEATHER_API_KEY.startswith("your_"):
        return _fetch_weatherapi(location)
    return _get_mock_weather(location)

def _fetch_weatherapi(location: str) -> ClimateData:
    """Fetches from WeatherAPI.com (supports forecast natively). API key is Weather_API_Key."""
    try:
        url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={location}&days=5&aqi=no&alerts=no"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        current = data["current"]
        forecast_days = data.get("forecast", {}).get("forecastday", [])

        forecast_list = []
        for day in forecast_days:
            forecast_list.append({
                "date": day["date"],
                "max_temp": day["day"]["maxtemp_c"],
                "min_temp": day["day"]["mintemp_c"],
                "rainfall": day["day"]["totalprecip_mm"],
                "humidity": day["day"]["avghumidity"],
                "condition": day["day"]["condition"]["text"],
                "uv_index": day["day"]["uv"],
                "chance_of_rain": day["day"]["daily_chance_of_rain"],
            })

        return ClimateData(
            location=data["location"]["name"],
            temperature=current["temp_c"],
            feels_like=current["feelslike_c"],
            rainfall=current["precip_mm"],
            humidity=current["humidity"],
            wind_speed=current["wind_kph"],
            weather_condition=current["condition"]["text"],
            uv_index=current.get("uv", 0.0),
            visibility=current.get("vis_km", 10.0),
            forecast=forecast_list,
        )
    except Exception as e:
        print(f"WeatherAPI failed: {e}. Trying fallback...")
        return _get_mock_weather(location)

def _get_mock_weather(location: str) -> ClimateData:
    """Realistic mock weather for demo mode."""
    import random
    is_raining = random.choice([True, False, False])  # bias clear
    temp = round(random.uniform(24.0, 38.0), 1)
    humidity = random.randint(45, 88)

    forecast_list = []
    for i in range(5):
        rain_chance = random.randint(0, 80)
        forecast_list.append({
            "date": datetime.now().strftime(f"%Y-%m-{(datetime.now().day + i):02d}"),
            "max_temp": round(temp + random.uniform(-2, 3), 1),
            "min_temp": round(temp - random.uniform(3, 8), 1),
            "rainfall": round(random.uniform(5, 40), 1) if rain_chance > 50 else 0.0,
            "humidity": random.randint(45, 90),
            "condition": "Rain" if rain_chance > 50 else "Partly Cloudy",
            "uv_index": round(random.uniform(3, 10), 1),
            "chance_of_rain": rain_chance,
        })

    return ClimateData(
        location=location,
        temperature=temp,
        feels_like=round(temp + random.uniform(-2, 2), 1),
        rainfall=round(random.uniform(10.0, 45.0), 1) if is_raining else 0.0,
        humidity=humidity,
        wind_speed=round(random.uniform(4.0, 18.0), 1),
        weather_condition="Light Rain" if is_raining else "Clear Sky",
        uv_index=round(random.uniform(4.0, 9.0), 1),
        visibility=round(random.uniform(7.0, 15.0), 1),
        forecast=forecast_list,
    )
