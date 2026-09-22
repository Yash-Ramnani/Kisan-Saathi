import requests
import random
from models.schemas import ClimateData
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()
WEATHERAPI_API_KEY = os.getenv("WEATHERAPI_API_KEY", "").strip()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()  # legacy fallback


def _is_placeholder(value: str) -> bool:
    return not value or value.startswith("your_")


def _fetch_weather_weatherapi(location: str, api_key: str) -> ClimateData:
    url = "https://api.weatherapi.com/v1/current.json"
    params = {
        "key": api_key,
        "q": location or "Gujarat",
        "aqi": "no",
    }
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    current = data.get("current", {})
    loc = data.get("location", {})
    condition = current.get("condition", {})

    return ClimateData(
        location=loc.get("name", location),
        temperature=current.get("temp_c", 0.0),
        rainfall=current.get("precip_mm", 0.0),
        humidity=current.get("humidity", 0),
        wind_speed=current.get("wind_kph", 0.0),
        weather_condition=condition.get("text", "Unknown"),
        feels_like=current.get("feelslike_c", current.get("temp_c", 0.0)),
        visibility=current.get("vis_km", 10.0),
        uv_index=current.get("uv", None),
    )


def _fetch_forecast_weatherapi(location: str, api_key: str) -> dict:
    url = "https://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": api_key,
        "q": location or "Gujarat",
        "days": 5,
        "aqi": "no",
        "alerts": "no",
    }
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    location_name = data.get("location", {}).get("name", location)
    forecast_days = data.get("forecast", {}).get("forecastday", [])

    forecast = []
    for item in forecast_days:
        day = item.get("day", {})
        forecast.append({
            "date": item.get("date", ""),
            "temp_max": day.get("maxtemp_c", 0.0),
            "temp_min": day.get("mintemp_c", 0.0),
            "description": day.get("condition", {}).get("text", "Unknown"),
            "rainfall_prob": float(day.get("daily_chance_of_rain", 0.0)),
            "humidity": day.get("avghumidity", 0),
        })

    return {"location": location_name, "forecast": forecast[:5]}


def _fetch_weather_openweather(location: str, api_key: str) -> ClimateData:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location or "Gujarat",
        "appid": api_key,
        "units": "metric",
    }
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    return ClimateData(
        location=data.get("name", location),
        temperature=data["main"]["temp"],
        rainfall=data.get("rain", {}).get("1h", 0.0),
        humidity=data["main"]["humidity"],
        wind_speed=round(float(data["wind"].get("speed", 0.0)) * 3.6, 2),
        weather_condition=data["weather"][0]["description"],
        feels_like=data["main"]["feels_like"],
        visibility=data.get("visibility", 10000) / 1000,
        uv_index=None,
    )


def _fetch_forecast_openweather(location: str, api_key: str) -> dict:
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": location or "Gujarat",
        "appid": api_key,
        "units": "metric",
    }
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    forecast = []
    for item in data["list"][::8]:
        forecast.append({
            "date": item["dt_txt"],
            "temp_max": item["main"]["temp_max"],
            "temp_min": item["main"]["temp_min"],
            "description": item["weather"][0]["description"],
            "rainfall_prob": item.get("pop", 0) * 100,
            "humidity": item["main"]["humidity"],
        })
    return {"location": location, "forecast": forecast[:5]}

def fetch_weather(location: str) -> ClimateData:
    """
    Fetches weather data for a location.
    Prefers WeatherAPI.com; falls back to OpenWeather legacy key; then mock data.
    """
    try:
        if not _is_placeholder(WEATHERAPI_API_KEY):
            return _fetch_weather_weatherapi(location, WEATHERAPI_API_KEY)

        if not _is_placeholder(OPENWEATHER_API_KEY):
            return _fetch_weather_openweather(location, OPENWEATHER_API_KEY)

        return get_mock_weather(location or "Gujarat")
    except Exception as e:
        print(f"Weather API failed: {e}. Falling back to mock data.")
        return get_mock_weather(location or "Gujarat")

def get_forecast_weekly(location: str) -> dict:
    """Fetch 5-day forecast using WeatherAPI or legacy OpenWeather."""
    try:
        if not _is_placeholder(WEATHERAPI_API_KEY):
            return _fetch_forecast_weatherapi(location, WEATHERAPI_API_KEY)

        if not _is_placeholder(OPENWEATHER_API_KEY):
            return _fetch_forecast_openweather(location, OPENWEATHER_API_KEY)

        return get_mock_forecast(location or "Gujarat")
    except Exception as e:
        print(f"Forecast API failed: {e}")
        return get_mock_forecast(location or "Gujarat")

def get_mock_forecast(location: str) -> dict:
    """Returns realistic mock forecast data."""
    forecast = []
    for day in range(5):
        date = datetime.now() + timedelta(days=day)
        forecast.append({
            "date": date.strftime("%Y-%m-%d %H:%M:%S"),
            "temp_max": round(random.uniform(30.0, 38.0), 1),
            "temp_min": round(random.uniform(20.0, 28.0), 1),
            "description": random.choice(["Clear Sky", "Partly Cloudy", "Rainy", "Light Rain"]),
            "rainfall_prob": round(random.uniform(0, 60), 1),
            "humidity": random.randint(40, 95)
        })
    return {"location": location, "forecast": forecast}

def get_mock_weather(location: str) -> ClimateData:
    """Returns realistic mock weather data."""
    is_raining = random.choice([True, False])
    return ClimateData(
        location=location,
        temperature=round(random.uniform(25.0, 38.0), 1),
        rainfall=round(random.uniform(10.0, 45.0), 1) if is_raining else 0.0,
        humidity=random.randint(40, 95),
        wind_speed=round(random.uniform(5.0, 20.0), 1),
        weather_condition="Rainy" if is_raining else "Clear Sky",
        feels_like=round(random.uniform(24.0, 40.0), 1),
        visibility=round(random.uniform(8.0, 10.0), 1),
        uv_index=round(random.uniform(3.0, 10.0), 1)
    )

def get_irrigation_advice(climate: ClimateData, soil_moisture: int = 50) -> list:
    """Generate irrigation advice based on weather."""
    advice = []
    
    if climate.humidity < 40 and climate.rainfall < 5:
        advice.append("💧 High irrigation need - Low humidity and no recent rain")
    elif climate.humidity > 80:
        advice.append("💧 Reduce irrigation - High humidity may cause fungal disease")
    
    if climate.temperature > 35:
        advice.append("🌡️ Extreme heat alert - Increase irrigation frequency")
    
    if climate.rainfall > 30:
        advice.append("⚠️ Heavy rain expected - Postpone irrigation")
    
    return advice if advice else ["💧 Maintain regular irrigation schedule"]

def get_spray_recommendations(climate: ClimateData) -> dict:
    """Get recommendations for pesticide/fertilizer spraying."""
    is_good_time = True
    reason = []
    
    # Wind speed should be 3-15 km/h for effective spraying
    if climate.wind_speed < 3:
        reason.append("Wind too calm - spray won't disperse properly")
        is_good_time = False
    elif climate.wind_speed > 15:
        reason.append("Wind too strong - spray will drift away")
        is_good_time = False
    
    # Should not spray in rain or high humidity
    if climate.humidity > 85:
        reason.append("High humidity may reduce spray effectiveness")
        is_good_time = False
    
    if climate.rainfall > 10:
        reason.append("Rain expected - spray will wash away")
        is_good_time = False
    
    return {
        "is_good_time": is_good_time and climate.wind_speed >= 3 and climate.wind_speed <= 15,
        "wind_speed": climate.wind_speed,
        "humidity": climate.humidity,
        "rainfall": climate.rainfall,
        "recommendations": reason if reason else ["✅ Good conditions for spraying"]
    }
