"""
Crop Advisory System - Provides recommendations based on conditions
"""

from typing import List, Dict
from models.schemas import CropAdvisoryResponse, ClimateData
from services.groq_client import generate_response

CROP_DATABASE = {
    "wheat": {
        "growth_stages": ["Germination (0-20 days)", "Vegetative (20-80 days)", "Flowering (80-100 days)", "Maturity (100-120 days)"],
        "ideal_temp": "15-25°C",
        "ideal_rainfall": "40-60cm",
        "common_diseases": ["Rust", "Powdery Mildew", "Karnal Bunt"],
        "common_pests": ["Armyworm", "Aphids", "Cutworm"],
        "season": "Rabi (Oct-Mar)"
    },
    "rice": {
        "growth_stages": ["Nursery", "Vegetative (30-60 days)", "Flowering (60-90 days)", "Maturity (90-120 days)"],
        "ideal_temp": "20-30°C",
        "ideal_rainfall": "150-250cm",
        "common_diseases": ["Leaf Blast", "Panicle Blast", "Brown Spot"],
        "common_pests": ["Leaf Folder", "Rice Case Worm", "Stem Borer"],
        "season": "Kharif (Jun-Nov)"
    },
    "cotton": {
        "growth_stages": ["Germination (15-20 days)", "Vegetative (30-60 days)", "Flowering (60-90 days)", "Boll Maturity (120-150 days)"],
        "ideal_temp": "21-30°C",
        "ideal_rainfall": "60-100cm",
        "common_diseases": ["Leaf Curl", "Wilt", "Rust"],
        "common_pests": ["Bollworm", "Whitefly", "Spider Mite"],
        "season": "Kharif (Apr-Oct)"
    },
    "maize": {
        "growth_stages": ["Germination (3-5 days)", "Vegetative (30-50 days)", "Tasseling (50-60 days)", "Grain Fill (60-100 days)"],
        "ideal_temp": "24-30°C",
        "ideal_rainfall": "50-80cm",
        "common_diseases": ["Leaf Blight", "Charcoal Rot", "Fusarium Rot"],
        "common_pests": ["Stem Borer", "Leaf Roller", "Fall Armyworm"],
        "season": "Kharif & Spring (Mar-Oct)"
    }
}

def get_crop_advice(crop: str, location: str, soil_type: str, climate: ClimateData) -> CropAdvisoryResponse:
    """Generate comprehensive crop advisory based on multiple factors."""
    
    crop_lower = crop.lower()
    crop_info = CROP_DATABASE.get(crop_lower, {})
    
    if not crop_info:
        # For crops not in DB, use LLM
        prompt = f"Generate crop advisory for {crop} in {location} with {soil_type} soil. Current weather: {climate.temperature}°C, {climate.humidity}% humidity."
        advice = generate_response(prompt, system_prompt="You are a crop advisory expert.")
        
        return CropAdvisoryResponse(
            crop=crop,
            growth_stage="Current Stage",
            irrigation_plan=["Regular irrigation as per season"],
            fertilizer_plan=["Follow recommended fertilizer schedule"],
            pest_risks=["Monitor for common pests"],
            disease_risks=["Watch for signs of disease"],
            next_actions=["Consult local agriculture officer for detailed guidance"]
        )
    
    # Generate advice from database
    irrigation_plan = generate_irrigation_schedule(crop_lower, climate)
    fertilizer_plan = generate_fertilizer_schedule(crop_lower, soil_type)
    
    return CropAdvisoryResponse(
        crop=crop,
        growth_stage=crop_info["growth_stages"][0],
        irrigation_plan=irrigation_plan,
        fertilizer_plan=fertilizer_plan,
        pest_risks=crop_info["common_pests"],
        disease_risks=crop_info["common_diseases"],
        next_actions=generate_action_plan(crop_lower, climate, soil_type)
    )

def generate_irrigation_schedule(crop: str, climate: ClimateData) -> List[str]:
    """Generate irrigation recommendations."""
    schedule = []
    
    if crop == "rice":
        schedule.append("Keep field flooded during vegetative stage (5-10cm water)")
        schedule.append("Maintain saturation during flowering")
        schedule.append("Gradually reduce water during grain filling")
    elif crop == "wheat":
        schedule.append("Irrigation at CRI stage (Crown Root Initiation)")
        schedule.append("Second irrigation at Tillering stage")
        schedule.append("Third irrigation at Jointing stage")
        schedule.append("Final irrigation at Grain Filling stage")
    elif crop == "cotton":
        schedule.append("First irrigation after 45-50 days")
        schedule.append("Subsequent irrigations at 10-15 day intervals")
        schedule.append("Reduce frequency during flowering")
    elif crop == "maize":
        schedule.append("First irrigation after 20-25 days of sowing")
        schedule.append("Critical irrigation at tasseling stage")
        schedule.append("Regular intervals of 10-15 days")
    
    # Adjust based on current weather
    if climate.humidity > 70:
        schedule.append(f"⚠️ High humidity ({climate.humidity}%) - Reduce irrigation frequency")
    if climate.rainfall > 20:
        schedule.append(f"💧 Recent rainfall ({climate.rainfall}mm) - Skip this irrigation")
    
    return schedule

def generate_fertilizer_schedule(crop: str, soil_type: str) -> List[str]:
    """Generate fertilizer application schedule."""
    base_npk = {
        "wheat": "120:60:40",
        "rice": "120:60:60",
        "cotton": "100:50:50",
        "maize": "150:75:40"
    }
    
    npk = base_npk.get(crop, "100:50:50")
    schedule = [f"Target NPK: {npk} kg/ha"]
    
    # Split application strategy
    schedule.append(f"Basal: Apply full Phosphorus & Potassium + 50% Nitrogen at sowing")
    schedule.append(f"Top dress: Split remaining Nitrogen at 2-3 stages")
    
    if soil_type == "sandy":
        schedule.append("Apply split doses due to high leaching potential")
    elif soil_type == "clay":
        schedule.append("Apply organic matter to improve nutrient availability")
    
    return schedule

def generate_action_plan(crop: str, climate: ClimateData, soil_type: str) -> List[str]:
    """Generate immediate action items."""
    actions = []
    
    actions.append("🌱 Conduct soil testing if not done recently")
    actions.append("💧 Check irrigation system for leaks or damage")
    actions.append("🔍 Monitor weather forecast for next 7 days")
    actions.append("🐛 Scout for pests and diseases daily")
    
    # Weather-based actions
    if climate.temperature > 35:
        actions.append("🌡️ HEAT ALERT: Increase irrigation frequency")
    if climate.humidity > 80:
        actions.append("💨 High humidity: Improve air circulation, watch for fungal diseases")
    if climate.wind_speed > 20:
        actions.append("💨 Strong wind: Secure structures, reduce spray application")
    
    actions.append("📱 Check market prices for selling decisions")
    
    return actions

def suggest_companion_crops(main_crop: str) -> List[str]:
    """Suggest companion crops for intercropping."""
    companions = {
        "cotton": ["Pulses", "Groundnut", "Vegetables"],
        "rice": ["Fish farming", "Ducks", "Vegetables"],
        "wheat": ["Pulses", "Mustard"],
        "maize": ["Pulses", "Beans", "Cucumbers"]
    }
    return companions.get(main_crop.lower(), ["Vegetables", "Pulses"])

def get_disease_management(crop: str, disease: str) -> Dict:
    """Get management strategy for a specific disease."""
    return {
        "disease": disease,
        "cause": "Fungal/Bacterial/Viral pathogen",
        "symptoms": "Check crop for visible signs",
        "management": [
            "Remove affected plant parts",
            "Apply recommended fungicide/pesticide",
            "Maintain proper spacing for air circulation",
            "Avoid overhead irrigation"
        ],
        "preventive_measures": [
            "Use disease-resistant varieties",
            "Crop rotation",
            "Proper sanitation",
            "Monitor weather conditions"
        ]
    }
