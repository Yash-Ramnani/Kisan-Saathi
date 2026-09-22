import json
from models.schemas import NormalizedInput, ClimateData, RiskScores, DecisionData
from services.groq_client import generate_response

def generate_decision(
    normalized_input: NormalizedInput,
    climate_data: ClimateData,
    risk_scores: RiskScores
) -> DecisionData:
    """
    Stage 4: Intelligent Decision Engine powered by LLM.
    Combines input intent, climate data, and risk scores to provide actionable insights.
    """
    prompt = f"""
    You are an expert agronomist AI for Indian farmers.
    Based on the following data, provide a structured decision for the farmer.
    
    Data:
    - Crop: {normalized_input.crop}
    - Location: {normalized_input.location}
    - Farmer Query: {normalized_input.intent}
    - Current Weather: {climate_data.weather_condition}, {climate_data.temperature}°C, Rain: {climate_data.rainfall}mm, Wind: {climate_data.wind_speed}km/h
    - Risk Scores: Disease Risk {risk_scores.disease_risk}/100, Irrigation Need {risk_scores.irrigation_need}/100, Spray Effectiveness {risk_scores.spray_effectiveness}/100
    
    Respond STRICTLY in valid JSON without ANY markdown formatting.
    Format your response EXACTLY like this:
    {{
        "decisions": ["Decision 1", "Decision 2"],
        "action_plan": ["Action 1", "Action 2", "Action 3"],
        "reason": "Clear explanation of why these decisions were made based on data."
    }}
    """
    
    system_prompt = "You are a professional farming assistant. Always respond with raw valid JSON."
    
    response = generate_response(prompt, system_prompt).strip()
    
    if response.startswith("```json"):
        response = response[7:]
    if response.startswith("```"):
        response = response[3:]
    if response.endswith("```"):
        response = response[:-3]
        
    try:
        data = json.loads(response.strip())
        return DecisionData(
            decisions=data.get("decisions", ["Consult regular agronomist for details."]),
            action_plan=data.get("action_plan", ["Monitor crop closely."]),
            reason=data.get("reason", "Based on current risk scores and weather.")
        )
    except Exception as e:
        print(f"Error parsing JSON in Stage 4: {e}")
        # Intent-aware rule-based fallback if LLM fails.
        query = f"{normalized_input.intent} {normalized_input.action}".lower()

        if any(k in query for k in ["price", "market", "mandi", "sell", "rate"]):
            return DecisionData(
                decisions=[
                    "Track mandi rates for the next 2-3 days before selling.",
                    "Prefer selling in nearby high-demand markets if transport is feasible.",
                ],
                action_plan=[
                    "Compare at least 2 mandi prices.",
                    "Sell in batches instead of full stock at once.",
                    "Check moisture/quality before dispatch for better price.",
                ],
                reason="Market intent detected; fallback provided market-oriented advisory.",
            )

        if any(k in query for k in ["disease", "pest", "spot", "rust", "blight", "spray"]):
            decisions = [
                "Disease risk indicates preventive action is needed.",
                "Spray timing should avoid rain and high wind windows.",
            ]
            return DecisionData(
                decisions=decisions,
                action_plan=[
                    "Inspect 20 random plants in the field.",
                    "Remove visibly infected leaves/plants.",
                    "Spray only when wind is low and no rain is expected.",
                ],
                reason="Disease intent detected; fallback provided protection-oriented plan.",
            )

        decisions = []
        if risk_scores.irrigation_need > 60:
            decisions.append("High priority to irrigate the crop today.")
        else:
            decisions.append("Irrigation is not urgently required today.")

        if risk_scores.disease_risk > 50:
            decisions.append("High disease risk detected. Monitor for fungal infections.")

        return DecisionData(
            decisions=decisions,
            action_plan=["Check soil moisture manually.", "Stay updated on weather."],
            reason="Weather/irrigation fallback decision due to processing failure.",
        )
