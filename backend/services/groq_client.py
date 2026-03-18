import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_mock_key_here")
GROQ_VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")


def get_groq_client():
    """Initialize Groq client only when API key is configured."""
    if GROQ_API_KEY and not GROQ_API_KEY.startswith("your_"):
        return Groq(api_key=GROQ_API_KEY)
    return None


def generate_response(prompt: str, system_prompt: str = "You are an AI Agronomist.") -> str:
    """Centralized text LLM call handler."""
    client = get_groq_client()

    if not client:
        return _mock_llm_response(prompt, system_prompt)

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=700,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Groq API Error: {e}")
        return _mock_llm_response(prompt, system_prompt)


def generate_vision_response(
    prompt: str,
    image_base64: str,
    image_mime_type: str = "image/jpeg",
    system_prompt: str = "You are an AI Agronomist.",
) -> str:
    """Call Groq vision model with an image and prompt."""
    client = get_groq_client()

    if not client:
        raise RuntimeError("Groq API key is missing or invalid. Vision analysis unavailable.")

    allowed_mime_types = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
    normalized_mime_type = image_mime_type.lower().strip()
    if normalized_mime_type not in allowed_mime_types:
        normalized_mime_type = "image/jpeg"

    model_candidates = [
        GROQ_VISION_MODEL,
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "meta-llama/llama-4-maverick-17b-128e-instruct",
    ]

    # De-duplicate model names while preserving order.
    seen = set()
    unique_models = []
    for model in model_candidates:
        if model and model not in seen:
            unique_models.append(model)
            seen.add(model)

    last_error = None
    for model_name in unique_models:
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{normalized_mime_type};base64,{image_base64}",
                                },
                            },
                        ],
                    },
                ],
                model=model_name,
                temperature=0.2,
                max_tokens=900,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            last_error = e
            print(f"Groq Vision API Error with model '{model_name}': {e}")

    # Let caller choose fallback strategy (heuristic, error response, etc.).
    raise RuntimeError(f"Groq vision models failed: {last_error}")


def _mock_llm_response(prompt: str, system_prompt: str = "") -> str:
    """Fallback response generator for demo mode when no real API key is provided."""
    import re
    import json

    prompt_lower = prompt.lower()
    system_lower = system_prompt.lower()

    default_location = "Gujarat"
    default_crop = "Cotton"

    loc_match = re.search(r"in\s+([a-zA-Z]+)", prompt_lower)
    if loc_match and loc_match.group(1) not in ["only", "valid"]:
        default_location = loc_match.group(1).capitalize()

    crop_match = re.search(r"for\s+([a-zA-Z]+)", prompt_lower)
    if crop_match and crop_match.group(1) not in ["only", "valid", "the"]:
        default_crop = crop_match.group(1).capitalize()

    cities = [
        "delhi", "mumbai", "pune", "surat", "ahmedabad", "hyderabad", "bangalore",
        "maharashtra", "punjab", "kerala", "chennai", "rajkot", "jaipur", "bhopal",
        "indore", "patna", "kanpur", "lucknow", "nagpur", "agra", "gandhinagar",
    ]
    for city in cities:
        if city in prompt_lower:
            default_location = city.capitalize()
            break

    crops = [
        "wheat", "rice", "cotton", "sugarcane", "maize", "soybean", "mustard",
        "bajra", "jowar", "groundnut", "onion", "potato", "tomato", "mango", "banana",
    ]
    for crop in crops:
        if crop in prompt_lower:
            default_crop = crop.capitalize()
            break

    if "input parser" in system_lower:
        res = {
            "crop": default_crop,
            "action": "check",
            "location": default_location,
            "intent": "User query",
            "is_valid_agri_query": True,
        }
        return json.dumps(res)

    if "farming assistant" in system_lower or "decision" in system_lower:
        res = {
            "decisions": [
                f"Monitor {default_crop} closely in {default_location}.",
                "Hold off on irrigation if rain is expected.",
            ],
            "action_plan": [
                "Check soil moisture tomorrow.",
                "Wait for predicted weather changes.",
            ],
            "reason": f"Based on location {default_location} and current weather data.",
        }
        return json.dumps(res)

    if "kisan saathi" in system_lower:
        english = (
            f"Namaste farmer friend! Based on the weather and risk data for {default_location}, "
            f"my advice is to monitor your {default_crop} crop. Hold off on heavy irrigation if rain is likely."
        )
        gujarati = (
            f"નમસ્તે ખેડૂત મિત્ર! {default_location} માટે હવામાન અને જોખમના ડેટાના આધારે, "
            f"મારી સલાહ છે કે તમારા {default_crop} પાકનું નિરીક્ષણ કરો. જો વરસાદની સંભાવના હોય તો ભારે સિંચાઈ ટાળો."
        )
        return f"{english}\n\n{gujarati}"

    return '{"status": "mock data returned"}'
