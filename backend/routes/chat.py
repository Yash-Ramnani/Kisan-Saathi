from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest, ChatResponse
import traceback

from services.stage1_normalizer import normalize_input
from services.stage2_climate import analyze_climate
from services.stage3_risk import calculate_risk
from services.stage4_decision import generate_decision
from services.stage5_humanize import format_humanized_reply

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    try:
        # Stage 1: Normalize
        normalized = normalize_input(request.message)
        
        # Guard clause for non-agri requests (optional approach)
        if not normalized.is_valid_agri_query:
            return ChatResponse(
                reply="Namaste! I am Kisan Saathi, your farming assistant. I can help you with crop advisory, weather, and decisions. Please ask a farming related question!\n\nનમસ્તે! હું કિસાન સાથી છું, તમારો ખેતી સહાયક. કૃપા કરીને ખેતી સંબંધિત પ્રશ્ન પૂછો!",
                original_message=request.message,
                location=normalized.location
            )
            
        # Stage 2: Weather & Climate
        climate = analyze_climate(normalized)
        
        # Stage 3: Risk Scoring
        risks = calculate_risk(normalized, climate)
        
        # Stage 4: Decision Engine
        decisions = generate_decision(normalized, climate, risks)
        
        # Stage 5: Humanize Response
        final_reply = format_humanized_reply(normalized, decisions, climate, risks)
        
        # Format payload to frontend
        weather_str = f"{climate.weather_condition}, {climate.temperature}°C, Rain: {climate.rainfall}mm, Humidity: {climate.humidity}%"
        
        return ChatResponse(
            reply=final_reply,
            location=climate.location,
            weather_summary=weather_str,
            risk_scores=risks.model_dump() if risks else None,
            decisions=decisions.decisions,
            action_plan=decisions.action_plan,
            reason=decisions.reason,
            original_message=request.message
        )
        
    except Exception as e:
        print(f"Error in chat pipeline: {e}")
        traceback.print_exc()
        # Fallback response to avoid crash
        fallback_msg = "Apologies, I encountered a temporary network issue analyzing your request. Please try again or check your internet connection.\n\nક્ષમા કરશો, સર્વર સમસ્યાને કારણે હું અત્યારે જવાબ આપી શકતો નથી. કૃપા કરીને થોડા સમય પછી ફરી પ્રયાસ કરો."
        return ChatResponse(
            reply=fallback_msg,
            original_message=request.message
        )
