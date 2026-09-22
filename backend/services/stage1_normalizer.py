import json
import re
from models.schemas import NormalizedInput
from services.groq_client import generate_response


def _fallback_normalize_input(user_message: str) -> NormalizedInput:
    text = user_message.strip()
    lower = text.lower()

    crop_keywords = [
        "wheat", "rice", "cotton", "maize", "soybean", "sugarcane",
        "groundnut", "mustard", "bajra", "jowar", "tomato", "potato",
    ]
    action_keywords = {
        "irrigate": ["irrigate", "irrigation", "water"],
        "spray": ["spray", "fungicide", "pesticide"],
        "harvest": ["harvest", "cut", "ready"],
        "price": ["price", "market", "mandi", "sell", "rate"],
        "disease": ["disease", "infection", "pest", "spot", "blight", "rust"],
        "weather": ["weather", "rain", "temperature", "humidity", "forecast"],
    }

    detected_crop = "unknown"
    for crop in crop_keywords:
        if crop in lower:
            detected_crop = crop
            break

    detected_action = "unknown"
    for action, words in action_keywords.items():
        if any(word in lower for word in words):
            detected_action = action
            break

    location = "Gujarat"
    loc_match = re.search(r"\b(?:in|at|near|for)\s+([A-Za-z\s]{2,40})", text, flags=re.IGNORECASE)
    if loc_match:
        candidate = loc_match.group(1).strip(" .,!?")
        if candidate:
            location = candidate

    is_agri = any(
        word in lower
        for word in [
            "farm", "farming", "crop", "soil", "weather", "irrigation",
            "pest", "disease", "fertilizer", "mandi", "price", "harvest",
            "ખેતી", "પાક", "હવામાન", "બજાર", "રોગ", "માટી", "પાણી",
            "रोग", "फसल", "मौसम", "खेती", "मिट्टी", "सिंचाई",
        ]
    )

    # Be permissive for ambiguous inputs; only mark non-agri for clearly unrelated chat.
    explicit_non_agri = any(
        word in lower
        for word in [
            "movie", "song", "cricket score", "stock market", "bitcoin",
            "relationship", "girlfriend", "boyfriend", "celebrity", "netflix",
        ]
    )

    if not is_agri and not explicit_non_agri:
        is_agri = True

    return NormalizedInput(
        crop=detected_crop,
        action=detected_action,
        location=location,
        intent=text,
        is_valid_agri_query=is_agri,
    )

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
        "is_valid_agri_query": true by default for uncertain cases; false ONLY if clearly unrelated to agriculture
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
        # Rule-based fallback to keep intent-specific behavior even when LLM parsing fails.
        return _fallback_normalize_input(user_message)
