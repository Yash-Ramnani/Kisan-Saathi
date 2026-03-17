import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_mock_key_here")

# Initialize client only if we have a real key, else we'll mock it
def get_groq_client():
    if GROQ_API_KEY and not GROQ_API_KEY.startswith("your_"):
        return Groq(api_key=GROQ_API_KEY)
    return None

def generate_response(prompt: str, system_prompt: str = "You are an AI Agronomist.") -> str:
    """Centralized LLM call handler."""
    client = get_groq_client()
    
    if not client:
        # Fallback if no API key is provided
        return _mock_llm_response(prompt, system_prompt)
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-8b-8192",
            temperature=0.3,
            max_tokens=500
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Groq API Error: {e}")
        return _mock_llm_response(prompt, system_prompt)

def _mock_llm_response(prompt: str, system_prompt: str = "") -> str:
    """A fallback mock response generator for demo purposes if Groq fails or no key is set."""
    import re
    import json
    
    prompt_lower = prompt.lower()
    system_lower = system_prompt.lower()
    
    # Try to extract location and crop from prompt
    default_location = "unknown"
    default_crop = "unknown"
    
    # Simple extraction using regex (looking for words after 'in ' or 'for ')
    loc_match = re.search(r'in\s+([a-zA-Z]+)', prompt_lower)
    if loc_match and loc_match.group(1) not in ['only', 'valid']:
        default_location = loc_match.group(1).capitalize()
        
    crop_match = re.search(r'for\s+([a-zA-Z]+)', prompt_lower)
    if crop_match and crop_match.group(1) not in ['only', 'valid', 'the', 'my', 'our']:
        default_crop = crop_match.group(1).capitalize()
        
    # Override if specific common cities are mentioned
    cities = ['delhi', 'mumbai', 'pune', 'surat', 'ahmedabad', 'hyderabad', 'bangalore', 'maharashtra', 'punjab', 'kerala', 'chennai', 'rajkot', 'jaipur', 'bhopal', 'indore', 'patna', 'kanpur', 'lucknow', 'nagpur', 'agra', 'gandhinagar']
    for city in cities:
        if city in prompt_lower:
            default_location = city.capitalize()
            break
            
    crops = ['wheat', 'rice', 'cotton', 'sugarcane', 'maize', 'soybean', 'mustard', 'bajra', 'jowar', 'groundnut', 'onion', 'potato', 'tomato', 'mango', 'banana']
    for crop in crops:
        if crop in prompt_lower:
            default_crop = crop.capitalize()
            break
            
    gu_crops = {
        'ઘઉં': 'Wheat',
        'ચોખા': 'Rice',
        'ડાંગર': 'Rice',
        'કપાસ': 'Cotton',
        'શેરડી': 'Sugarcane',
        'મકાઈ': 'Maize',
        'સોયાબીન': 'Soybean',
        'સરસવ': 'Mustard',
        'બાજરી': 'Bajra',
        'જુવાર': 'Jowar',
        'મગફળી': 'Groundnut',
        'ડુંગળી': 'Onion',
        'બટાકા': 'Potato',
        'ટામેટા': 'Tomato',
        'કેરી': 'Mango',
        'કેળા': 'Banana',
        'કેળાં': 'Banana'
    }
    for gu_name, en_name in gu_crops.items():
        if gu_name in prompt_lower:
            default_crop = en_name
            break
            
    # Stage overrides
    if "input parser" in system_lower:
        # Stage 1: Normalize
        res = {
            "crop": default_crop,
            "action": "unknown" if "intent" not in prompt_lower else "check",
            "location": default_location,
            "intent": prompt_lower,
            "time_horizon": "today",
            "is_valid_agri_query": True
        }
        return json.dumps(res)
        
    elif "farming assistant" in system_lower or "decision" in system_lower:
        # Stage 4: Decision
        res = {
            "decisions": [f"{default_location} માં {default_crop} પર નજીકથી નજર રાખો.", "જો વરસાદની સંભાવના હોય તો સિંચાઈ ટાળો."],
            "action_plan": ["આવતીકાલે જમીનનો ભેજ તપાસો.", "હવામાનના અંદાજિત ફેરફારોની રાહ જુઓ."],
            "reason": f"{default_location} ના વર્તમાન હવામાન ડેટા પર આધારિત."
        }
        return json.dumps(res)
        
    elif "kisan saathi" in system_lower:
        # Stage 5: Humanize
        english = f"Namaste farmer friend! Based on the weather and risk data for {default_location}, my advice is to monitor your {default_crop} crop. Hold off on heavy irrigation if rain is likely."
        gujarati = f"નમસ્તે ખેડૂત મિત્ર! {default_location} માટે હવામાન અને જોખમના ડેટાના આધારે, મારી સલાહ છે કે તમારા {default_crop} પાકનું નિરીક્ષણ કરો. જો વરસાદની સંભાવના હોય તો ભારે સિંચાઈ ટાળો."
        return f"{gujarati}\n\n{english}"
    
    # Fallback
    return '{"status": "mock data returned"}'
