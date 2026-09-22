from models.schemas import NormalizedInput, DecisionData, ClimateData, RiskScores
from services.groq_client import generate_response


def _fallback_humanized_reply(decision_data: DecisionData) -> str:
    english_lines = ["Namaste farmer friend!", "Here is your farm advice:"]
    for idx, item in enumerate(decision_data.decisions[:3], start=1):
        english_lines.append(f"{idx}. {item}")

    english_lines.append("Action plan:")
    for idx, item in enumerate(decision_data.action_plan[:3], start=1):
        english_lines.append(f"{idx}. {item}")

    gujarati_lines = [
        "નમસ્તે ખેડૂત મિત્ર!",
        "આ રહી તમારી ખેતી સલાહ:",
    ]
    for idx, item in enumerate(decision_data.decisions[:3], start=1):
        gujarati_lines.append(f"{idx}. {item}")
    gujarati_lines.append("કાર્ય યોજના:")
    for idx, item in enumerate(decision_data.action_plan[:3], start=1):
        gujarati_lines.append(f"{idx}. {item}")

    return "\n".join(english_lines) + "\n\n" + "\n".join(gujarati_lines)

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
    4. Provide the exact text first in English, and then add a line break `\n\n` and provide the FULL TRANSLATION in Gujarati.
    
    Response format:
    [English version]
    
    [Gujarati translation]
    """
    
    system_prompt = "You are Kisan Saathi, a helpful farming AI. Answer in English, followed by Gujarati translation."

    response = generate_response(prompt, system_prompt).strip()

    # If output is empty, malformed, or mock-like, return deterministic bilingual content.
    if (
        not response
        or response.startswith('{"status"')
        or len(response) < 30
        or "\n\n" not in response
    ):
        return _fallback_humanized_reply(decision_data)

    return response

