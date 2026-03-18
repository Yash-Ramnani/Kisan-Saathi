import json
from models.schemas import NormalizedInput, ClimateData, RiskScores, DecisionData
from services.groq_client import generate_response

def generate_decision(
    normalized_input: NormalizedInput,
    climate_data: ClimateData,
    risk_scores: RiskScores,
) -> DecisionData:
    """
    Stage 4: AI-powered decision engine with rich agronomic context.
    """
    # Build forecast summary if available
    forecast_text = ""
    if climate_data.forecast:
        forecast_text = "5-Day Forecast:\n"
        for day in climate_data.forecast[:5]:
            forecast_text += (
                f"  - {day.get('date', 'N/A')}: {day.get('condition', 'N/A')}, "
                f"Max {day.get('max_temp', '?')}°C, Min {day.get('min_temp', '?')}°C, "
                f"Rain {day.get('rainfall', 0)}mm, {day.get('chance_of_rain', 0)}% rain chance\n"
            )

    pest_info = f"\n- Pest Concern: {normalized_input.pest_concern}" if normalized_input.pest_concern else ""
    disease_info = f"\n- Disease Concern: {normalized_input.disease_concern}" if normalized_input.disease_concern else ""

    prompt = f"""You are an expert agronomist AI providing hyper-local, actionable advice to Indian farmers.

Farmer Data:
- Crop: {normalized_input.crop}
- Location: {normalized_input.location}
- Farmer's Question/Intent: {normalized_input.intent}{pest_info}{disease_info}
- Time Horizon: {normalized_input.time_horizon}
- Preferred Action: {normalized_input.action}

Real-Time Climate:
- Condition: {climate_data.weather_condition}
- Temperature: {climate_data.temperature}°C (Feels like {climate_data.feels_like}°C)
- Humidity: {climate_data.humidity}%
- Rainfall: {climate_data.rainfall}mm
- Wind Speed: {climate_data.wind_speed} km/h
- UV Index: {climate_data.uv_index}
{forecast_text}

Risk Intelligence:
- Disease Risk: {risk_scores.disease_risk}/100
- Irrigation Need: {risk_scores.irrigation_need}/100
- Spray Effectiveness: {risk_scores.spray_effectiveness}/100
- Heat Stress: {risk_scores.heat_stress}/100
- Frost Risk: {risk_scores.frost_risk}/100
- Overall Alert: {risk_scores.overall_alert}

Provide decisions that are:
1. Specific to the crop and current weather (not generic)
2. Actionable within the next 24-72 hours
3. Science-backed (mention specific practices, timing, quantities where relevant)
4. Safety-first (avoid spraying in rain/wind, avoid irrigation before rain, etc.)

Respond STRICTLY in raw valid JSON (no markdown):
{{
    "decisions": ["2-4 specific decisions based on data"],
    "action_plan": ["3-5 ordered step-by-step actions for today/tomorrow"],
    "reason": "1-2 sentence explanation referencing specific weather + risk data"
}}"""

    system_prompt = "You are an expert AI agronomist for Indian farmers. Respond only with valid JSON."

    response = generate_response(prompt, system_prompt).strip()

    for prefix in ["```json", "```"]:
        if response.startswith(prefix):
            response = response[len(prefix):]
    if response.endswith("```"):
        response = response[:-3]

    try:
        data = json.loads(response.strip())
        return DecisionData(
            decisions=data.get("decisions", ["Monitor your crop closely today."]),
            action_plan=data.get("action_plan", ["Check soil moisture.", "Observe crop leaves for stress signs."]),
            reason=data.get("reason", "Based on current weather and risk analysis.")
        )
    except Exception as e:
        print(f"Stage 4 JSON parse error: {e}")
        # Rule-based fallback
        decisions = []
        action_plan = []

        if risk_scores.irrigation_need > 60:
            decisions.append(f"⚠️ High irrigation need ({risk_scores.irrigation_need}/100) — water your {normalized_input.crop} today.")
            action_plan.append("Irrigate early morning (6-8 AM) to minimize evaporation.")
        else:
            decisions.append(f"💧 Irrigation not urgent ({risk_scores.irrigation_need}/100) — hold off for now.")

        if risk_scores.disease_risk > 55:
            decisions.append(f"🦠 Disease risk is HIGH ({risk_scores.disease_risk}/100) — inspect crop for fungal signs.")
            action_plan.append("Check leaves for discolouration, spots, or rot. Apply preventive fungicide if needed.")

        if risk_scores.spray_effectiveness < 40:
            decisions.append(f"🚫 Poor spray conditions ({risk_scores.spray_effectiveness}/100) — delay spraying to clear conditions.")
        else:
            action_plan.append("Spray pesticides early morning when wind is calm (below 8 km/h).")

        if risk_scores.heat_stress > 40:
            decisions.append(f"🌡️ Heat stress detected — mulch soil and increase irrigation frequency.")

        action_plan.append("Monitor weather updates every 6 hours.")
        action_plan.append("Record any visible crop changes for follow-up assessment.")

        return DecisionData(
            decisions=decisions or ["Monitor crop and stay updated on weather."],
            action_plan=action_plan or ["Check soil moisture.", "Observe crop daily."],
            reason=f"Based on {climate_data.temperature}°C temp, {climate_data.humidity}% humidity, and {risk_scores.overall_alert} alert level."
        )
