from models.schemas import NormalizedInput, DecisionData, ClimateData, RiskScores
from services.groq_client import generate_response

def format_humanized_reply(
    normalized_input: NormalizedInput, 
    decision_data: DecisionData,
    climate_data: ClimateData,
    risk_scores: RiskScores
) -> str:
    """
    Stage 5: Final Humanization.
    Translates the structured data into a friendly, readable conversational message 
    in English and Gujarati.
    """
    prompt = f"""
    You are 'Kisan Saathi', a friendly AI agronomist for Indian farmers.
    Create a brief, comforting, yet highly practical response for a farmer based on the following decisions.
    
    Data:
    - Farmer's crop: {normalized_input.crop}
    - Weather: {climate_data.weather_condition}, {climate_data.temperature}°C, {climate_data.rainfall}mm rain.
    - Decisions: {", ".join(decision_data.decisions)}
    - Action Plan: {", ".join(decision_data.action_plan)}
    - Reason: {decision_data.reason}
    
    Instructions:
    1. Start with a warm greeting like "Namaste farmer friend!" or similar.
    2. Keep it conversational.
    3. Include the advice clearly.
    4. Provide the exact text first in GUJARATI, and then add a line break `\n\n` and provide the FULL TRANSLATION in English.
    
    Response format:
    [Gujarati translation]
    
    [English version]
    """
    
    system_prompt = "You are Kisan Saathi, a helpful farming AI. Answer in Gujarati first, followed by English translation."
    
    response = generate_response(prompt, system_prompt).strip()
    return response

