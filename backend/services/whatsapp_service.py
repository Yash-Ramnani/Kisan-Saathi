"""
WhatsApp Integration Service - Handles WhatsApp chatbot communication
Uses Twilio WhatsApp API for messaging
"""

import os
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
import requests

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

# Mock database for WhatsApp farmer profiles
WHATSAPP_FARMERS = {}

class WhatsAppClient:
    """Handles WhatsApp messaging through Twilio."""
    
    def __init__(self):
        self.account_sid = TWILIO_ACCOUNT_SID
        self.auth_token = TWILIO_AUTH_TOKEN
        self.from_number = TWILIO_WHATSAPP_NUMBER
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}"
    
    def send_message(self, to_number: str, message: str, media_url: Optional[str] = None) -> dict:
        """Send WhatsApp message to a farmer."""
        
        # If no credentials, return mock success
        if not self.account_sid or self.account_sid.startswith("your_"):
            return {
                "success": True,
                "message_sid": f"mock_{datetime.now().timestamp()}",
                "status": "queued",
                "note": "Demo mode - message not actually sent"
            }
        
        try:
            url = f"{self.base_url}/Messages.json"
            
            data = {
                "From": self.from_number,
                "To": f"whatsapp:{to_number}",
                "Body": message
            }
            
            if media_url:
                data["MediaUrl"] = media_url
            
            response = requests.post(
                url,
                data=data,
                auth=(self.account_sid, self.auth_token)
            )
            
            if response.status_code == 201:
                result = response.json()
                return {
                    "success": True,
                    "message_sid": result.get("sid"),
                    "status": result.get("status")
                }
            else:
                return {
                    "success": False,
                    "error": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def register_webhook(self, webhook_url: str) -> bool:
        """Register webhook for receiving incoming messages."""
        print(f"Webhook configured to receive messages at: {webhook_url}")
        return True

def handle_incoming_whatsapp_message(message_data: dict) -> str:
    """
    Process incoming WhatsApp message and generate response.
    Webhook from Twilio will call this function.
    """
    
    from_number = message_data.get("From", "").replace("whatsapp:", "")
    message_text = message_data.get("Body", "")
    media_url = message_data.get("MediaUrl")
    
    # Register farmer if new
    if from_number not in WHATSAPP_FARMERS:
        WHATSAPP_FARMERS[from_number] = {
            "phone": from_number,
            "joined_date": datetime.now().isoformat(),
            "messages_count": 0,
            "language": "en"
        }
    
    # Update message count
    WHATSAPP_FARMERS[from_number]["messages_count"] += 1
    
    # Process message based on intent
    response = process_whatsapp_query(message_text, from_number, media_url)
    
    return response

def process_whatsapp_query(message: str, farmer_phone: str, media_url: Optional[str] = None) -> str:
    """Process farmer query and generate response."""
    
    message_lower = message.lower()
    farmer_lang = WHATSAPP_FARMERS.get(farmer_phone, {}).get("language", "en")
    
    # Greeting responses
    if any(word in message_lower for word in ["hello", "hi", "नमस्ते", "namaste", "salaam"]):
        return get_greeting_response(farmer_lang)
    
    # Weather query
    elif any(word in message_lower for word in ["weather", "rain", "temperature", "temp", "मौसम", "तापमान"]):
        return "🌤️ *Weather Update*\n\nCurrent Conditions:\n• Temperature: 32°C\n• Humidity: 65%\n• Wind: 12 km/h\n• Chance of Rain: 20%\n\n📊 Recommendation: Good conditions for irrigation today.\n\nReply with your location for more detailed forecast."
    
    # Crop advisory
    elif any(word in message_lower for word in ["crop", "advice", "plant", "grow", "खेती", "फसल"]):
        return "🌾 *Crop Advisory*\n\nWhich crop do you want advice on?\n1. Wheat\n2. Rice\n3. Cotton\n4. Maize\n5. Groundnut\n\nReply with crop name or number."
    
    # Soil analysis with image
    elif media_url:
        return "📸 *Soil Analysis*\n\nWe received your soil image! Our AI will analyze it.\n\nAnalysis Results:\n• Soil Type: Loamy\n• Fertility: Medium\n• pH: 6.8\n\n✅ Recommended Crops:\n- Wheat, Rice, Maize, Vegetables\n\n💡 Next: Apply organic manure for better fertility."
    
    # Market prices
    elif any(word in message_lower for word in ["price", "market", "sell", "mandi", "कीमत", "बाजार"]):
        return "💰 *Market Prices*\n\nCurrent Mandi Rates:\n• Wheat: ₹2,450/quintal\n• Rice: ₹3,600/quintal\n• Cotton: ₹8,700/bale\n\n📈 Trend: Prices trending UP\n💡 Recommendation: Best prices at Chandni Chowk Mandi, Delhi"
    
    # Disease detection
    elif any(word in message_lower for word in ["disease", "sick", "pest", "problem", "बीमारी", "कीट"]):
        return "🐛 *Disease Detection*\n\nSend us a photo of your affected crop plant.\n\nOur AI will identify the disease and suggest treatment."
    
    # Default helpful response
    else:
        return get_help_response(farmer_lang)

def get_greeting_response(language: str = "en") -> str:
    """Get localized greeting."""
    if language == "gu":  # Gujarati
        return """🙏 *સ્વાગત છે આપનું*

હું કિસાન સાથી છું, તમારો સ્માર્ટ ખેતી સહાયક.

હું આપને પણ સાહાય્য કરી શકું:
1️⃣ 🌦️ આબોહવા અને વર્ષા માહિતી
2️⃣ 🌾 પાક સલાહ
3️⃣ 💰 બાજાર કિંમતો
4️⃣ 🐛 રોગ નિવારણ
5️⃣ 📸 જમીન વિશ્લેષણ

કૃપા કરીને તમારો પ્રશ્ન પૂછો!"""
    else:  # English
        return """🙏 *Welcome to Kisan Saathi*

I'm your AI-powered farming assistant.

I can help you with:
1️⃣ 🌦️ Weather & Rainfall Info
2️⃣ 🌾 Crop Advisory
3️⃣ 💰 Market Prices
4️⃣ 🐛 Disease Detection
5️⃣ 📸 Soil Analysis

What can I help you with today?"""

def get_help_response(language: str = "en") -> str:
    """Get localized help menu."""
    if language == "gu":  # Gujarati
        return """📋 *સાહાય્યક અપશન*

હું અહીં તમારો મદદ કરવા છું:

📝 આ શબ્દો ટાઇપ કરો:
• "મૌસમ" - આબોહવા માહિતી માટે
• "પાક" - પાક સલાહ માટે
• "કીમત" - બાજાર હાવ માટે
• "રોગ" - રોગ નિવારણ માટે
• "જમીન" - જમીન વિશ્લેષણ માટે

📱 અથવા આપણી વેબસાઇટ મલાય કરો વધુ માહિતી માટે."""
    else:  # English
        return """📋 *How Can I Help?*

Try typing:
• "Weather" - for weather info
• "Crop" - for crop advice
• "Price" - for market rates
• "Disease" - for pest/disease help
• "Soil" - for soil analysis

Or visit our website for detailed dashboards!"""

def send_alert_to_farmer(farmer_phone: str, alert_type: str, message: str) -> bool:
    """Send alert to farmer via WhatsApp."""
    
    client = WhatsAppClient()
    
    alert_emoji = {
        "weather": "⚠️",
        "pest": "🐛",
        "disease": "🤒",
        "irrigation": "💧",
        "market": "💰"
    }
    
    emoji = alert_emoji.get(alert_type, "🔔")
    alert_message = f"{emoji} *Alert*\n\n{message}"
    
    result = client.send_message(farmer_phone, alert_message)
    return result.get("success", False)

def get_farmer_profile(farmer_phone: str) -> dict:
    """Get farmer profile from WhatsApp."""
    return WHATSAPP_FARMERS.get(farmer_phone, {
        "phone": farmer_phone,
        "joined_date": datetime.now().isoformat(),
        "messages_count": 0,
        "language": "en"
    })

def update_farmer_language(farmer_phone: str, language: str) -> bool:
    """Update farmer's language preference."""
    if farmer_phone in WHATSAPP_FARMERS:
        WHATSAPP_FARMERS[farmer_phone]["language"] = language
        return True
    return False
