"""
Translation Service - Supports English and Gujarati
Uses simple translation dictionaries + LLM for complex text
"""

from services.groq_client import generate_response

# Gujarati translation dictionaries
TRANSLATIONS = {
    "weather_alert": {
        "en": "🌦️ Weather Alert",
        "gu": "🌦️ મૌસમ ચેતવણી"
    },
    "disease_detected": {
        "en": "🐛 Disease Detected",
        "gu": "🐛 રોગ શોધાયો"
    },
    "irrigation_needed": {
        "en": "💧 Irrigation Needed",
        "gu": "💧 સિંચાઇ આવશ્યક"
    },
    "crop_ready": {
        "en": "✅ Crop Ready for Harvest",
        "gu": "✅ પાક લણાઈ માટે તૈયાર"
    },
    "soil_type": {
        "en": "Soil Type",
        "gu": "જમીનનો પ્રકાર"
    },
    "temperature": {
        "en": "Temperature",
        "gu": "તાપમાન"
    },
    "humidity": {
        "en": "Humidity",
        "gu": "ஈતાવર"
    },
    "rainfall": {
        "en": "Rainfall",
        "gu": "વર્ષા"
    },
    "recommended_crops": {
        "en": "Recommended Crops",
        "gu": "પ્રશંસિત પાકો"
    },
    "farming_advice": {
        "en": "Farming Advice",
        "gu": "ખેતી સલાહ"
    },
    "market_prices": {
        "en": "Market Prices",
        "gu": "બાજાર કિંમતો"
    }
}

def translate_text(text: str, target_language: str = "gu") -> str:
    """Translate text to target language (English or Gujarati)."""
    
    if target_language == "en":
        return text  # Already in English
    
    if target_language not in ["en", "gu"]:
        return text
    
    # Check if exact translation exists
    for key, translations in TRANSLATIONS.items():
        if text == translations.get("en"):
            return translations.get(target_language, text)
    
    # For longer text, use LLM
    if len(text) > 50:
        return translate_with_llm(text, target_language)
    
    # Simple word-by-word translation for short text
    gujarati_words = {
        "crop": "પાક",
        "weather": "મૌસમ",
        "rain": "વર્ષા",
        "soil": "જમીન",
        "disease": "રોગ",
        "pest": "કીટ",
        "irrigation": "સિંચાઇ",
        "fertilizer": "ખાતર",
        "temperature": "તાપમાન",
        "humidity": "ર્દ્રતા",
        "good": "સારું",
        "bad": "ખરાબ",
        "excellent": "શ્રેષ્ઠ",
        "alert": "ચેતવણી",
        "warning": "ચેતવણી",
        "help": "સાહાય્য",
        "price": "કિંમત",
        "market": "બાજાર",
        "health": "સ્વાસ્થ્ય",
        "water": "પાણી"
    }
    
    result = text
    for english, gujarati in gujarati_words.items():
        result = result.replace(english, gujarati, flags=2)
    
    return result

def translate_with_llm(text: str, target_language: str) -> str:
    """Use LLM for complex translation."""
    
    prompt = f"""Translate the following farming-related text from English to {'Gujarati' if target_language == 'gu' else 'English'}. 
    Keep agricultural terminology consistent and accurate.
    
    Text to translate:
    {text}
    
    Provide ONLY the translated text, no explanations."""
    
    system_prompt = "You are an expert translator specializing in agriculture and farming terminology."
    
    try:
        translation = generate_response(prompt, system_prompt)
        return translation.strip()
    except:
        return text  # Fallback to original if LLM fails

def get_localized_report(report_data: dict, language: str = "en") -> dict:
    """Generate localized report based on language."""
    
    localized = report_data.copy()
    
    if language == "gu":
        # Translate key fields
        for key in ["title", "summary", "recommendations", "warnings"]:
            if key in localized and isinstance(localized[key], str):
                localized[key] = translate_text(localized[key], language)
            elif key in localized and isinstance(localized[key], list):
                localized[key] = [translate_text(item, language) for item in localized[key]]
    
    return localized

def format_multilingual_advice(advice_text: str, language: str = "en") -> str:
    """Format advice in requested language."""
    
    if language == "en":
        return advice_text
    
    # Translate advice
    translated = translate_text(advice_text, language)
    return translated

def get_language_preference(farmer_id: str) -> str:
    """Get farmer's language preference (mock)."""
    # In production, fetch from database
    return "en"  # Default English

def set_language_preference(farmer_id: str, language: str) -> bool:
    """Set farmer's language preference."""
    # In production, save to database
    if language in ["en", "gu"]:
        return True
    return False

# Gujarati UI strings dictionary
GUJARATI_UI_STRINGS = {
    "navbar": {
        "home": "હોમ",
        "soil_analysis": "જમીન વિશ્લેષણ",
        "weather": "મૌસમ",
        "crop_advisor": "પાક સલાહ",
        "disease": "રોગ નિવારણ",
        "market": "બાજાર",
        "chat": "ચેટ"
    },
    "common": {
        "hello": "નમસ્તે",
        "welcome": "સ્વાગતમ",
        "thank_you": "આભાર",
        "yes": "હા",
        "no": "ના",
        "submit": "સમર્પણ",
        "cancel": "રદ કરો",
        "loading": "લોડ થઇ રહ્યું છે...",
        "error": "ભૂલ",
        "success": "સફળતા"
    },
    "weather": {
        "temperature": "તાપમાન",
        "humidity": "ર્દ્રતા",
        "rainfall": "વર્ષા",
        "wind_speed": "પવનનો વેગ",
        "forecast": "આગાહી"
    }
}

def get_ui_string(key: str, section: str = "common", language: str = "en") -> str:
    """Get translated UI string."""
    
    if language == "en":
        return key  # Return key as is for English
    
    if section in GUJARATI_UI_STRINGS:
        return GUJARATI_UI_STRINGS[section].get(key, key)
    
    return key
