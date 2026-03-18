from models.schemas import NormalizedInput, ClimateData
from services.weather_service import fetch_weather

def analyze_climate(normalized_input: NormalizedInput) -> ClimateData:
    """
    Stage 2: Fetch real-time weather + 5-day forecast for the detected location.
    """
    location = normalized_input.location
    if not location or location.lower() == "unknown":
        location = "Ahmedabad"  # Fallback to common Gujarat city

    climate_data = fetch_weather(location=location)
    return climate_data
