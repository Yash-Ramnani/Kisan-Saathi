import json
from models.schemas import NormalizedInput
from services.groq_client import generate_response

def normalize_input(user_message: str, current_location: str = None, known_crops: list = None) -> NormalizedInput:
    """
    Stage 1: Extacts structured data from the raw user message.
    """
    loc_context = current_location if current_location else 'None'
    crop_context = ', '.join(known_crops) if known_crops else 'None'

    prompt = f"""
    You are a structured data extraction engine for an agricultural AI system in India.

    Your job is to convert user input into structured JSON.

    Extract the following JSON keys:
    - "location": String (city/state)
    - "crop": String (Standard English crop name)
    - "intent": String (Brief summary of the farmer's question, e.g., irrigation, spraying, disease, general_advice)
    - "time_horizon": String (today, tomorrow, next_3_days)
    - "action": String (e.g., irrigate, spray, harvest, unknown)
    - "is_valid_agri_query": Boolean (true if related to farming, else false)

    IMPORTANT INSTRUCTIONS:
    1. The user may enter crop names in Gujarati, Hindi, or English.
    2. You MUST normalize crop names into standard English crop names.
       Examples:
       - "કપાસ" or "kapas" -> "Cotton"
       - "ગહું" or "gehun" -> "Wheat"
       - "ચોખા" or "chawal" -> "Rice"
       - "મકાઈ" or "makka" -> "Maize"
       - "ડુંગળી" -> "Onion"
       - "બટાકા" -> "Potato"
       - "ટમેટા" -> "Tomato"
    3. If crop is written in Gujarati or Hinglish, convert it correctly.
    4. Do NOT ask again for crop if it is already present in any language.
    5. Infer missing values logically using Context below. If missing and not in Context, output 'unknown'.
    6. Output ONLY valid JSON. No explanation. No markdown formatting if possible.

    Context:
    - Farmer's known location: {loc_context}
    - Farmer's known crops: {crop_context}

    User Input:
    {user_message}
    """
    system_prompt = "You are an agricultural input parser. Return strictly valid JSON."
    
    response = generate_response(prompt, system_prompt).strip()
    
    # Cleaning any markdown tags if LLM still returned them
    if response.startswith("```json"):
        response = response[7:]
    if response.startswith("```"):
        response = response[3:]
    if response.endswith("```"):
        response = response[:-3]

    try:
        data = json.loads(response.strip())
        return NormalizedInput(
            crop=data.get("crop", "unknown").capitalize() if data.get("crop") and data.get("crop") != "unknown" else "unknown",
            action=data.get("action", "unknown"),
            location=data.get("location", "unknown"),
            intent=data.get("intent", "Unknown intent"),
            time_horizon=data.get("time_horizon", "today"),
            is_valid_agri_query=data.get("is_valid_agri_query", True)
        )
    except Exception as e:
        print(f"Error parsing JSON in Stage 1: {e}")
        # Fallback mechanism
        return NormalizedInput(
            crop="unknown",
            action="unknown",
            location="unknown",
            intent=user_message,
            time_horizon="today",
            is_valid_agri_query=True
        )
