from models.schemas import NormalizedInput, ClimateData
from services.weather_service import fetch_weather

def analyze_climate(normalized_input: NormalizedInput) -> ClimateData:
    """
    Stage 2: Fetch and analyze climate conditions.
    """
    location = normalized_input.location
    if location.lower() == "unknown":
        location = "Gujarat" # Fallback location

    climate_data = fetch_weather(location=location)
    return climate_data
