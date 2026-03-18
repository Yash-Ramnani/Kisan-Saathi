"""Routes for Weather and Climate API"""

from fastapi import APIRouter, HTTPException
from models.schemas import ClimateData
from services.weather_service import fetch_weather, get_forecast_weekly, get_irrigation_advice, get_spray_recommendations

router = APIRouter()

@router.get("/weather/{location}", response_model=ClimateData)
async def get_weather(location: str):
    """Get current weather for a location."""
    
    try:
        climate = fetch_weather(location)
        return climate
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Weather fetch failed: {str(e)}")

@router.get("/weather/forecast/{location}")
async def get_forecast(location: str):
    """Get 5-day weather forecast."""
    
    try:
        forecast = get_forecast_weekly(location)
        return forecast
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/weather/irrigation-advice/{location}")
async def get_irrigation_recommendations(location: str, soil_moisture: int = 50):
    """Get irrigation recommendations based on weather."""
    
    try:
        climate = fetch_weather(location)
        advice = get_irrigation_advice(climate, soil_moisture)
        return {
            "location": location,
            "weather": climate,
            "irrigation_advice": advice
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/weather/spray-recommendations/{location}")
async def get_spray_advice(location: str):
    """Get recommendations for pesticide/fertilizer spraying."""
    
    try:
        climate = fetch_weather(location)
        spray_advice = get_spray_recommendations(climate)
        return {
            "location": location,
            "spray_recommendations": spray_advice
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
