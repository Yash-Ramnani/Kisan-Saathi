from models.schemas import NormalizedInput, ClimateData, RiskScores

# Crop-specific thresholds for better accuracy
CROP_HEAT_THRESHOLD = {
    "Wheat": 32, "Rice": 35, "Cotton": 40, "Maize": 38,
    "Potato": 28, "Tomato": 35, "Onion": 35, "Groundnut": 38,
    "Soybean": 35, "Pearl Millet": 42, "Sorghum": 40,
}

CROP_MIN_TEMP = {
    "Wheat": 5, "Potato": 7, "Tomato": 10, "Onion": 10,
    "Rice": 15, "Cotton": 18, "Maize": 12, "Groundnut": 18,
}

def calculate_risk(normalized_input: NormalizedInput, climate_data: ClimateData) -> RiskScores:
    """
    Stage 3: Multi-dimensional rule-based risk scoring.
    """
    crop = normalized_input.crop
    temp = climate_data.temperature
    humidity = climate_data.humidity
    rainfall = climate_data.rainfall
    wind = climate_data.wind_speed

    # --- 1. Disease / Fungal Risk ---
    # High humidity + warm temps = fungal/bacterial bloom risk
    disease_risk = 5
    if humidity > 80 and 20 <= temp <= 32:
        disease_risk = min(100, int((humidity - 80) * 3 + 40))
    elif humidity > 65 and 18 <= temp <= 35:
        disease_risk = min(100, int((humidity - 65) * 1.5 + 20))
    # Rainy conditions amplify disease risk
    if rainfall > 10:
        disease_risk = min(100, disease_risk + 15)
    # Specific disease concern mentioned
    if normalized_input.disease_concern:
        disease_risk = min(100, disease_risk + 20)

    # --- 2. Irrigation Need ---
    irrigation_need = 40
    if rainfall > 15.0:
        irrigation_need = 5
    elif rainfall > 5.0:
        irrigation_need = 20
    elif temp > 35 and rainfall == 0:
        irrigation_need = min(100, 60 + int((temp - 35) * 4))
    elif temp > 30 and rainfall == 0:
        irrigation_need = min(100, 50 + int((temp - 30) * 3))

    # High humidity reduces irrigation need slightly
    if humidity > 75:
        irrigation_need = max(5, irrigation_need - 15)

    # --- 3. Spray Effectiveness ---
    spray_effectiveness = 85
    if rainfall > 3.0:
        spray_effectiveness = 10   # Rain washes off spray
    elif wind > 20:
        spray_effectiveness = 15   # High wind causes drift
    elif wind > 12:
        spray_effectiveness = 45
    elif wind > 8:
        spray_effectiveness = 65
    # Early morning / low humidity = better absorption
    if humidity < 50 and wind < 8:
        spray_effectiveness = min(100, spray_effectiveness + 10)

    # --- 4. Heat Stress ---
    heat_threshold = CROP_HEAT_THRESHOLD.get(crop, 37)
    heat_stress = 0
    if temp > heat_threshold:
        heat_stress = min(100, int((temp - heat_threshold) * 12))
    elif temp > heat_threshold - 3:
        heat_stress = min(50, int((temp - (heat_threshold - 3)) * 8))

    # --- 5. Frost Risk ---
    frost_risk = 0
    min_temp_threshold = CROP_MIN_TEMP.get(crop, 8)
    if temp < min_temp_threshold + 3:
        frost_risk = min(100, int((min_temp_threshold + 3 - temp) * 20))

    # --- Overall Alert Level ---
    max_risk = max(disease_risk, irrigation_need, heat_stress, frost_risk)
    if max_risk >= 75 or (disease_risk > 60 and irrigation_need > 60):
        overall_alert = "CRITICAL"
    elif max_risk >= 50:
        overall_alert = "HIGH"
    elif max_risk >= 30:
        overall_alert = "MEDIUM"
    else:
        overall_alert = "LOW"

    return RiskScores(
        disease_risk=int(disease_risk),
        irrigation_need=int(irrigation_need),
        spray_effectiveness=int(spray_effectiveness),
        heat_stress=int(heat_stress),
        frost_risk=int(frost_risk),
        overall_alert=overall_alert,
    )
