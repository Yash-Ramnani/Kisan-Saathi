from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest, ChatResponse
import traceback

from services.stage1_normalizer import normalize_input
from services.stage2_climate import analyze_climate
from services.stage3_risk import calculate_risk
from services.stage4_decision import generate_decision
from services.stage5_humanize import format_humanized_reply
from services import memory_service

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    session_id = request.session_id or "default"

    # Load session memory
    known_location = request.current_location or memory_service.get_known_location(session_id)
    known_crops = request.known_crops or memory_service.get_known_crops(session_id)
    history = memory_service.get_history(session_id)

    # Record user message
    memory_service.add_message(session_id, "user", request.message)

    try:
        # Stage 1: Normalize
        normalized = normalize_input(
            user_message=request.message,
            current_location=known_location,
            known_crops=known_crops,
            history=history,
        )

        # Guard: non-agri query
        if not normalized.is_valid_agri_query:
            reply = (
                "નમસ્તે! 🌾 હું કિસાન સાથી છું — તમારો ખેતી AI સહાયક.\n"
                "કૃપા કરીને ખેતી, પાક, હવામાન અથવા સિંચાઈ સંબંધિત પ્રશ્ન પૂછો.\n\n"
                "---\n\n"
                "Namaste! 🌾 I am Kisan Saathi — your farming AI assistant.\n"
                "Please ask a question related to farming, crops, weather, or irrigation."
            )
            memory_service.add_message(session_id, "assistant", reply)
            return ChatResponse(reply=reply, original_message=request.message)

        # Guard: missing location + crop
        missing = []
        if normalized.crop.lower() == "unknown":
            missing.append("crop (e.g., Cotton, Wheat) | પાક (દા.ત. કપાસ, ઘઉં)")
        if normalized.location.lower() == "unknown":
            missing.append("location (e.g., Surat, Rajkot) | સ્થાન (દા.ત. સુરત, રાજકોટ)")

        if missing:
            missing_str = " and ".join(missing)
            reply = (
                f"📍 સચોટ સલાહ આપવા માટે, કૃપા કરીને તમારું **{missing_str}** જણાવો.\n\n"
                f"---\n\n"
                f"📍 To give you accurate advice, please specify your **{missing_str}**."
            )
            memory_service.add_message(session_id, "assistant", reply)
            return ChatResponse(reply=reply, original_message=request.message)

        # Save detected location & crop to memory
        memory_service.save_location(session_id, normalized.location)
        memory_service.save_crop(session_id, normalized.crop)

        # Stage 2: Weather & Climate
        climate = analyze_climate(normalized)

        # Stage 3: Risk Scoring
        risks = calculate_risk(normalized, climate)

        # Stage 4: Decision Engine
        decisions = generate_decision(normalized, climate, risks)

        # Stage 5: Humanize Response
        final_reply = format_humanized_reply(normalized, decisions, climate, risks)
        memory_service.add_message(session_id, "assistant", final_reply)

        # Determine season
        from datetime import datetime
        month = datetime.now().month
        if month in (6, 7, 8, 9, 10):
            season = "Kharif (ખરીફ)"
        elif month in (11, 12, 1, 2, 3):
            season = "Rabi (રવિ)"
        else:
            season = "Zaid (ઝાઈદ)"

        weather_str = (
            f"{climate.weather_condition} | {climate.temperature}°C "
            f"(feels {climate.feels_like}°C) | 💧{climate.humidity}% | "
            f"🌧️{climate.rainfall}mm | 💨{climate.wind_speed}km/h | UV:{climate.uv_index}"
        )

        return ChatResponse(
            reply=final_reply,
            location=climate.location,
            weather_summary=weather_str,
            forecast=climate.forecast,
            risk_scores=risks.model_dump(),
            decisions=decisions.decisions,
            action_plan=decisions.action_plan,
            reason=decisions.reason,
            original_message=request.message,
            detected_crop=normalized.crop,
            season=season,
        )

    except Exception as e:
        print(f"Pipeline error: {e}")
        traceback.print_exc()
        fallback = (
            "⚠️ ક્ષમા કરશો, સર્વર સમસ્યા. કૃપા કરીને ફરી પ્રયાસ કરો.\n\n"
            "---\n\n"
            "⚠️ Sorry, a server error occurred. Please try again in a moment."
        )
        memory_service.add_message(session_id, "assistant", fallback)
        return ChatResponse(reply=fallback, original_message=request.message)
