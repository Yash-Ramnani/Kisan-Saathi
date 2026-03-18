"""Routes for WhatsApp Integration API"""

from fastapi import APIRouter, HTTPException, Form
from models.schemas import WhatsAppMessage
from services.whatsapp_service import (
    handle_incoming_whatsapp_message, 
    send_alert_to_farmer,
    get_farmer_profile,
    update_farmer_language,
    WhatsAppClient
)
from datetime import datetime

router = APIRouter()

@router.post("/whatsapp/webhook")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    MediaUrl: str = Form(None)
):
    """
    Webhook endpoint for incoming WhatsApp messages from Twilio.
    This is called by Twilio when a farmer sends a message.
    """
    
    try:
        message_data = {
            "From": From,
            "Body": Body,
            "MediaUrl": MediaUrl
        }
        
        # Process the message
        response = handle_incoming_whatsapp_message(message_data)
        
        # Send response back via WhatsApp
        client = WhatsAppClient()
        phone_number = From.replace("whatsapp:", "")
        client.send_message(phone_number, response)
        
        return {"status": "message_processed"}
    except Exception as e:
        print(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/whatsapp/send-alert/{farmer_phone}")
async def send_farmer_alert(farmer_phone: str, alert_type: str, message: str):
    """Send an alert to a farmer via WhatsApp."""
    
    try:
        if alert_type not in ["weather", "pest", "disease", "irrigation", "market"]:
            raise ValueError("Invalid alert type")
        
        success = send_alert_to_farmer(farmer_phone, alert_type, message)
        
        return {
            "success": success,
            "farmer_phone": farmer_phone,
            "alert_type": alert_type
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/whatsapp/farmer-profile/{farmer_phone}")
async def get_farmer_info(farmer_phone: str):
    """Get farmer profile from WhatsApp interaction history."""
    
    try:
        profile = get_farmer_profile(farmer_phone)
        return profile
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/whatsapp/farmer-language/{farmer_phone}/{language}")
async def update_language_preference(farmer_phone: str, language: str):
    """Update farmer's language preference."""
    
    try:
        if language not in ["en", "gu"]:
            raise ValueError("Language must be 'en' (English) or 'gu' (Gujarati)")
        
        success = update_farmer_language(farmer_phone, language)
        
        if not success:
            raise ValueError("Farmer not found")
        
        return {
            "success": True,
            "farmer_phone": farmer_phone,
            "language": language
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/whatsapp/send-message/{farmer_phone}")
async def send_whatsapp_message(farmer_phone: str, message: str):
    """Send a WhatsApp message to a farmer."""
    
    try:
        client = WhatsAppClient()
        result = client.send_message(farmer_phone, message)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
