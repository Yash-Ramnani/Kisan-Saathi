from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest, ChatResponse
import traceback
import re

from services.stage1_normalizer import normalize_input
from services.stage2_climate import analyze_climate
from services.stage3_risk import calculate_risk
from services.stage4_decision import generate_decision
from services.stage5_humanize import format_humanized_reply
from services.groq_client import generate_response
from services.market_insights import get_market_insights
from services.scheme_fetcher import get_scheme_context_for_ai, fetch_live_farmer_schemes

router = APIRouter()


def _detect_intent_bucket(message: str, action: str) -> str:
    text = (message or "").lower().strip()
    action = (action or "").lower().strip()

    if re.fullmatch(r"(hi|hello|hey|hii|namaste|kem cho|ram ram|good morning|good evening)[!. ]*", text):
        return "greeting"

    if any(k in text for k in ["weather", "rain", "temperature", "humidity", "forecast", "climate"]):
        return "weather"

    if any(k in text for k in ["irrigat", "water", "paani", "sinchai", "સિંચાઇ", "પાણી"]):
        return "irrigation"

    if action == "price" or any(k in text for k in ["market", "mandi", "price", "rate", "sell", "bhav", "ભાવ"]):
        return "market"

    if action == "disease" or any(k in text for k in ["disease", "pest", "spot", "blight", "rust", "fung", "infection", "રોગ", "कीट", "रोग"]):
        return "disease"

    if any(k in text for k in ["scheme", "yojana", "subsidy", "government", "govt", "pm-kisan", "pmkisan", "kcc"]):
        return "scheme"

    if any(k in text for k in ["crop", "fertiliz", "sow", "seed", "harvest", "soil", "ખેતી", "પાક", "ફસલ", "मिट्टी", "खेती"]):
        return "crop"

    if any(k in text for k in ["movie", "song", "cricket", "bitcoin", "celebrity", "netflix"]):
        return "non_agri"

    return "general"


def _get_general_agri_reply(message: str, bucket: str, crop: str, location: str, language: str) -> str:
    lang = "English + Gujarati" if language == "gu" else "English"
    scheme_context = get_scheme_context_for_ai(max_items=8)
    prompt = f"""
    Farmer message: {message}
    Intent bucket: {bucket}
    Crop context: {crop}
    Location context: {location}
    Live scheme context:
    {scheme_context}

    Provide a practical agriculture/farming answer, not weather-only.
    Include:
    1) Direct answer to farmer question
    2) 3 immediate actions for field
    3) 1 warning to avoid common mistake
    4) Keep it concise and farmer-friendly
    5) If relevant, mention applicable government schemes with clickable links copied exactly from context.

    Language: {lang}
    """
    system_prompt = "You are Kisan Saathi, an Indian agriculture expert assistant. Stay focused on farming and actionable advice."
    return generate_response(prompt, system_prompt).strip()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    try:
        # Stage 1: Normalize
        normalized = normalize_input(request.message)
        bucket = _detect_intent_bucket(request.message, normalized.action)

        if bucket == "greeting":
            welcome = (
                "Namaste! I can help with crop planning, pest/disease control, irrigation, fertilizers, mandi prices, and sowing/harvesting decisions. "
                "Tell me your crop, location, and exact problem, and I will give a direct farming plan.\n\n"
                "નમસ્તે! હું પાક આયોજન, રોગ-કીટ નિયંત્રણ, સિંચાઈ, ખાતર સલાહ, મંડી ભાવ અને વાવણી/કાપણી નિર્ણયમાં મદદ કરી શકું છું. "
                "તમારો પાક, વિસ્તાર અને સમસ્યા લખો, હું સીધી ખેતી યોજના આપું."
            )
            return ChatResponse(reply=welcome, original_message=request.message)

        if bucket == "non_agri":
            reply = (
                "I am focused on agriculture and farming. Ask me about crops, soil, irrigation, pest/disease, or mandi prices and I will give a detailed plan.\n\n"
                "હું ખેતી વિષયક પ્રશ્નો માટે બનાવેલો સહાયક છું. પાક, માટી, સિંચાઈ, રોગ/કીટ અથવા મંડી ભાવ વિશે પૂછો."
            )
            return ChatResponse(reply=reply, original_message=request.message)

        if bucket == "market":
            crop = normalized.crop if normalized.crop != "unknown" else "cotton"
            market = get_market_insights(crop)
            market_prompt = f"""
            Farmer asked: {request.message}
            Crop: {crop}
            Current price: {market.current_price}
            Week ago price: {market.week_ago_price}
            Trend: {market.trend}
            Best mandi: {market.best_mandi}
            Recommendation seed: {market.recommendation}

            Create a practical answer with:
            - Short market summary
            - Whether to sell now or wait
            - 3 specific selling actions
            - Bilingual English + Gujarati output
            """
            market_reply = generate_response(
                market_prompt,
                "You are a mandi market advisor for Indian farmers. Give practical decision support."
            ).strip()
            return ChatResponse(
                reply=market_reply,
                location=normalized.location,
                original_message=request.message
            )

        if bucket == "scheme":
            scheme_data = fetch_live_farmer_schemes(force_refresh=False)
            schemes = scheme_data.get("schemes", [])[:10]

            if not schemes:
                fallback = (
                    "I could not fetch live scheme links at the moment. Please open the Schemes section and retry refresh.\n\n"
                    "હાલમાં લાઇવ યોજના લિંક્સ મેળવવામાં મુશ્કેલી છે. કૃપા કરીને Schemes વિભાગ ખોલો અને Refresh કરો."
                )
                return ChatResponse(reply=fallback, original_message=request.message)

            lines = []
            for idx, item in enumerate(schemes, start=1):
                lines.append(f"{idx}. {item['title']} - {item['url']}")

            scheme_reply = (
                "Here are currently discoverable farmer government schemes:\n"
                + "\n".join(lines)
                + "\n\nYou can open these links directly from the Schemes page."
            )
            return ChatResponse(
                reply=scheme_reply,
                original_message=request.message,
            )

        # Weather and irrigation intents benefit from climate + risk pipeline.
        if bucket in {"weather", "irrigation"}:
            climate = analyze_climate(normalized)
            risks = calculate_risk(normalized, climate)
            decisions = generate_decision(normalized, climate, risks)
            final_reply = format_humanized_reply(normalized, decisions, climate, risks)
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

        # For crop/disease/general farming queries, use direct AI advisory path.
        ai_reply = _get_general_agri_reply(
            message=request.message,
            bucket=bucket,
            crop=normalized.crop,
            location=normalized.location,
            language=request.language,
        )

        return ChatResponse(
            reply=ai_reply,
            location=normalized.location,
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
