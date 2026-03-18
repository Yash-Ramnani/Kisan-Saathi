from models.schemas import NormalizedInput, DecisionData, ClimateData, RiskScores
from services.groq_client import generate_response

def format_humanized_reply(
    normalized_input: NormalizedInput,
    decision_data: DecisionData,
    climate_data: ClimateData,
    risk_scores: RiskScores,
) -> str:
    """
    Stage 5: Convert structured decisions into a warm, WhatsApp-friendly message.
    Returns Gujarati first, then English. Concise enough for mobile reading.
    """
    alert_emoji = {"LOW": "✅", "MEDIUM": "⚠️", "HIGH": "🔴", "CRITICAL": "🚨"}.get(risk_scores.overall_alert, "ℹ️")

    decisions_text = "\n".join(f"• {d}" for d in decision_data.decisions)
    action_text = "\n".join(f"{i+1}. {a}" for i, a in enumerate(decision_data.action_plan))

    prompt = f"""You are 'Kisan Saathi' (કિસાન સાથી), a friendly AI farming advisor for Indian farmers.

Write a warm, WhatsApp-style message for the farmer. It must be:
- Concise and easy to read on mobile (no long paragraphs)
- Use simple language a village farmer would understand
- Include relevant emojis to make it friendly (🌾🌧️🌡️💧🦠✅⚠️)
- End with an encouraging note

Data:
- Crop: {normalized_input.crop}
- Location: {climate_data.location}
- Weather: {climate_data.weather_condition}, {climate_data.temperature}°C, {climate_data.humidity}% humidity
- Alert Level: {alert_emoji} {risk_scores.overall_alert}
- Key Decisions: {decisions_text}
- Action Plan: {action_text}
- Reason: {decision_data.reason}

FORMAT (strictly follow this):
Write the full response FIRST in Gujarati, then add exactly "---" as separator, then the FULL English translation.

Gujarati response:
[Gujarati text here - use bullet points, keep under 200 words]

---

English response:
[English text here - same structure, under 200 words]"""

    system_prompt = "You are Kisan Saathi, a farming AI. Write in Gujarati first, then '---', then English. Keep it warm, short, emoji-rich."

    response = generate_response(prompt, system_prompt).strip()
    return response
