import json
from models.schemas import NormalizedInput
from services.groq_client import generate_response

def normalize_input(user_message: str) -> NormalizedInput:
    """
    Stage 1: Extacts structured data from the raw user message.
    """
    prompt = f"""
    Analyze the following user query about farming: "{user_message}"
    Extract the following details in ONLY valid JSON format.
    Do not add markdown formatting like ```json ... ```, just output the raw JSON string.

    {{
        "crop": "Crop name if mentioned, else 'unknown'",
        "action": "Action requested like irrigate, spray, harvest. E.g., 'irrigate', 'unknown'",
        "location": "Location if specified, else 'Gujarat'",
        "intent": "Brief summary of the farmer's question",
        "is_valid_agri_query": true if the query is about farming, weather or agriculture, else false
    }}
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
            crop=data.get("crop", "unknown"),
            action=data.get("action", "unknown"),
            location=data.get("location", "Gujarat"),
            intent=data.get("intent", "Unknown intent"),
            is_valid_agri_query=data.get("is_valid_agri_query", True)
        )
    except Exception as e:
        print(f"Error parsing JSON in Stage 1: {e}")
        # Fallback mechanism
        return NormalizedInput(
            crop="unknown",
            action="unknown",
            location="Gujarat",
            intent=user_message,
            is_valid_agri_query=True
        )
