import json
from models.schemas import NormalizedInput
from services.groq_client import generate_response

def normalize_input(user_message: str, current_location: str = None, known_crops: list = None, history: list = None) -> NormalizedInput:
    """
    Stage 1: Extract structured data from raw user message.
    Uses conversation history for context-aware extraction.
    """
    loc_context = current_location if current_location else 'Not specified'
    crop_context = ', '.join(known_crops) if known_crops else 'Not specified'

    history_text = ""
    if history:
        for h in history[-6:]:  # last 3 turns
            role = "Farmer" if h["role"] == "user" else "Kisan Saathi"
            history_text += f"{role}: {h['content']}\n"

    prompt = f"""You are a structured data extraction engine for an agricultural AI system in India.

Convert the farmer's message into structured JSON. Use conversation history for context.

Extract:
- "location": String (city/village/state in India. Use context if not in current message)
- "crop": String (Standard English crop name. Use context if not in current message)
- "intent": String (one of: irrigation, spraying, disease, pest, harvest, fertilizer, weather, market_price, general_advice)
- "time_horizon": String (today, tomorrow, next_3_days, this_week)
- "action": String (irrigate, spray, harvest, fertilize, monitor, unknown)
- "is_valid_agri_query": Boolean (true if farming/agriculture/weather related)
- "pest_concern": String or null (specific pest mentioned e.g. "aphid", "bollworm", "whitefly")
- "disease_concern": String or null (specific disease mentioned e.g. "blight", "rust", "powdery_mildew")

RULES:
1. Normalize crop names from Gujarati/Hindi/Hinglish to standard English.
   - કપાસ/kapas → Cotton | ઘઉં/gehun → Wheat | ડાંગર/chawal → Rice
   - મકાઈ/makka → Maize | ડુંગળી → Onion | બટાકા → Potato | ટામેટા → Tomato
   - મગફળી/moongphali → Groundnut | કેળા → Banana | કેરી/aam → Mango
   - બાજરી → Pearl Millet | જુવાર → Sorghum | સોયાબીન → Soybean
2. If location or crop is missing from current message, infer from Context below.
3. Output ONLY valid raw JSON - no markdown, no explanation.

Context:
- Farmer's known location: {loc_context}
- Farmer's known crops: {crop_context}

Conversation History:
{history_text if history_text else "No history yet."}

Current Message: {user_message}
"""
    system_prompt = "You are an agricultural input parser for Indian farmers. Return strictly valid JSON only."

    response = generate_response(prompt, system_prompt).strip()

    # Strip markdown code fences if present
    for prefix in ["```json", "```"]:
        if response.startswith(prefix):
            response = response[len(prefix):]
    if response.endswith("```"):
        response = response[:-3]

    try:
        data = json.loads(response.strip())
        crop = data.get("crop", "unknown")
        if crop and crop.lower() not in ("unknown", "null", "none", ""):
            crop = crop.strip().capitalize()
        else:
            crop = "unknown"

        location = data.get("location", "unknown")
        if not location or location.lower() in ("null", "none", "not specified"):
            location = "unknown"

        return NormalizedInput(
            crop=crop,
            action=data.get("action") or "unknown",
            location=location,
            intent=data.get("intent") or "general_advice",
            time_horizon=data.get("time_horizon") or "today",
            is_valid_agri_query=bool(data.get("is_valid_agri_query", True)),
            pest_concern=data.get("pest_concern") or None,
            disease_concern=data.get("disease_concern") or None,
        )
    except Exception as e:
        print(f"Stage 1 JSON parse error: {e} | Raw: {response[:200]}")
        return NormalizedInput(
            crop="unknown",
            action="unknown",
            location=current_location or "unknown",
            intent=user_message[:100],
            time_horizon="today",
            is_valid_agri_query=True,
        )
