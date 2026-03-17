from models.schemas import NormalizedInput, ClimateData, RiskScores

def calculate_risk(normalized_input: NormalizedInput, climate_data: ClimateData) -> RiskScores:
    """
    Stage 3: Calculate rule-based risk scoring using climate and input.
    """
    # Disease risk logic
    # High humidity + moderate to high temps = fungal/disease risk
    disease_risk = 10
    if climate_data.humidity > 70 and 20 <= climate_data.temperature <= 35:
        disease_risk = min(100, (climate_data.humidity - 70) * 2 + 30)

    # Irrigation need
    # High temp + no rain = high need. High rain = zero need
    irrigation_need = 50
    if climate_data.rainfall > 5.0:
        irrigation_need = 5
    elif climate_data.temperature > 30 and climate_data.rainfall == 0:
        irrigation_need = min(100, 50 + (climate_data.temperature - 30) * 3)
    
    # Spray effectiveness
    # High wind or rain = low effectiveness
    spray_effectiveness = 80
    if climate_data.rainfall > 2.0 or climate_data.wind_speed > 15:
        spray_effectiveness = 20
    elif climate_data.wind_speed > 8:
        spray_effectiveness = 50

    return RiskScores(
        disease_risk=int(disease_risk),
        irrigation_need=int(irrigation_need),
        spray_effectiveness=int(spray_effectiveness)
    )
