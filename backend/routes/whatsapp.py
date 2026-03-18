"""
Kisan Saathi — WhatsApp Webhook v2.0
Full-featured intelligent bot with:
- Interactive menus (10 features)
- Mandi prices, Crop calendar, Govt schemes
- Fertilizer & pest advisor
- Farmer profile memory
- Proactive CRITICAL weather alerts
- Daily morning report subscription
- Multi-language (Gujarati + English)
"""
import os
import asyncio
import re
from fastapi import APIRouter, Request, Response, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from datetime import datetime

from services.whatsapp_service import (
    extract_message_details,
    send_text_message,
    send_main_menu,
    send_weather_card,
    send_risk_card,
    send_forecast_card,
    send_help_message,
    mark_as_read,
)
from services.stage1_normalizer import normalize_input
from services.stage2_climate import analyze_climate
from services.stage3_risk import calculate_risk
from services.stage4_decision import generate_decision
from services.stage5_humanize import format_humanized_reply
from services import memory_service
from services.mandi_service import get_mandi_price, format_mandi_whatsapp
from services.crop_calendar import format_crop_calendar_whatsapp, CROP_CALENDAR
from services.schemes_service import (
    get_all_schemes_menu,
    get_scheme_details,
    detect_scheme_query,
)
from services.fertilizer_advisor import get_fertilizer_advice, get_pest_disease_advice

load_dotenv()
WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN", "kisan_saathi_secure_token_2024")

router = APIRouter()

# ─── Webhook Verification ────────────────────────────────────────

@router.get("/webhook")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == WEBHOOK_VERIFY_TOKEN:
        print("✅ WhatsApp webhook verified!")
        return Response(content=params.get("hub.challenge"), media_type="text/plain")
    raise HTTPException(status_code=403, detail="Webhook verification failed")


# ─── Incoming Message Handler ────────────────────────────────────

@router.post("/webhook")
async def receive_message(request: Request, background_tasks: BackgroundTasks):
    try:
        body = await request.json()
    except Exception:
        return Response(content="OK", status_code=200)
    background_tasks.add_task(process_message, body)
    return Response(content="OK", status_code=200)


# ─── Command Detection Helpers ────────────────────────────────────

def _detect_command(text: str) -> str | None:
    """Returns a command key if the message is a known shortcut."""
    t = text.lower().strip()

    # Menu / Help
    if t in ("menu", "help", "start", "hi", "hello", "namaste", "kem cho", "helo", "0"):
        return "menu"
    if t in ("1", "weather"):
        return "weather_only"
    if t in ("2", "advisory"):
        return "advisory"
    if t in ("3", "calendar"):
        return "calendar"
    if t in ("4", "mandi", "bhav", "price"):
        return "mandi"
    if t in ("5", "schemes", "yojana", "sarkar"):
        return "schemes"
    if t in ("6", "fertilizer", "khaad", "khad"):
        return "fertilizer"
    if t in ("7", "pest", "jeevaat", "bimari"):
        return "pest"
    if t in ("8", "profile", "maro profile", "my profile"):
        return "profile"
    if t in ("9", "daily report", "subah report", "morning report"):
        return "daily_report_toggle"
    if t in ("help", "?", "how to use"):
        return "help"

    # Mandi price patterns — "wheat price", "kapas bhav", "mandi cotton"
    if re.search(r"(bhav|price|mandi|market|bazar|bazaar)", t):
        return "mandi"

    # Crop calendar
    if re.search(r"(calendar|calender|schedule|vavni|harvest|laNavni)", t):
        return "calendar"

    # Fertilizer
    if re.search(r"(khaad|fertilizer|npk|urea|daa|potash|nutrient|soil test)", t):
        return "fertilizer"

    # Pest/disease
    if re.search(r"(jeevaat|keeda|pest|bollworm|blight|rust|spray|fungicide|insect|disease|bimari)", t):
        return "pest"

    # Govt schemes
    scheme = detect_scheme_query(t)
    if scheme:
        return f"scheme:{scheme}"

    # Profile update shortcuts
    if re.match(r"^location\s+\w+", t):
        return "set_location"
    if re.match(r"^crop\s+\w+", t):
        return "set_crop"

    return None  # Normal agricultural query → run full AI pipeline


def _extract_crop_from_text(text: str, known_crops: list) -> str | None:
    """Extracts crop name from text or uses known crops."""
    from services.crop_calendar import CROP_CALENDAR
    t = text.lower()
    for crop in CROP_CALENDAR.keys():
        if crop.lower() in t:
            return crop
    for crop in known_crops:
        if crop.lower() in t:
            return crop
    if known_crops:
        return known_crops[0]
    return None


def _get_season() -> str:
    month = datetime.now().month
    if month in (6, 7, 8, 9, 10):   return "Kharif (ખ rif)"
    elif month in (11, 12, 1, 2, 3): return "Rabi (R abi)"
    return "Zaid (Z id)"


# ─── Main Message Processor ──────────────────────────────────────

async def process_message(body: dict):
    from_number, text, message_id = extract_message_details(body)

    if not from_number or not text:
        return

    print(f"📱 [{from_number}]: {text[:100]}")

    # Mark as read (blue ticks)
    if message_id:
        mark_as_read(message_id)

    session_id = from_number
    known_location = memory_service.get_known_location(session_id)
    known_crops = memory_service.get_known_crops(session_id)
    history = memory_service.get_history(session_id)

    memory_service.add_message(session_id, "user", text)

    # Detect command
    cmd = _detect_command(text)

    try:
        # ── MENU ──
        if cmd == "menu":
            crop_name = known_crops[0] if known_crops else "ખKhedut"
            send_main_menu(from_number, crop_name)
            return

        # ── HELP ──
        if cmd == "help":
            send_help_message(from_number)
            return

        # ── PROFILE ──
        if cmd == "profile":
            send_text_message(from_number, memory_service.get_farmer_profile(session_id))
            return

        # ── SET LOCATION ──
        if cmd == "set_location":
            new_loc = text.strip().split(None, 1)[1].strip()
            memory_service.save_location(session_id, new_loc.capitalize())
            send_text_message(from_number,
                f"📍 Location updated: *{new_loc.capitalize()}*\n"
                f"tmlocation save thai chhe! Hve baadhi advice {new_loc} mate milse. ✅"
            )
            return

        # ── SET CROP ──
        if cmd == "set_crop":
            new_crop = text.strip().split(None, 1)[1].strip().capitalize()
            memory_service.save_crop(session_id, new_crop)
            send_text_message(from_number,
                f"🌾 Crop saved: *{new_crop}*\n"
                f"Tmaaro paak save thai gayo! Hve {new_crop} mato advice milse. ✅"
            )
            return

        # ── DAILY REPORT TOGGLE ──
        if cmd == "daily_report_toggle":
            subscribed = memory_service.toggle_daily_report(session_id)
            if subscribed:
                send_text_message(from_number,
                    "⏰ *Daily Morning Report — Subscribe! ✅*\n\n"
                    "Subah 7 AJe tmne havaman + kheti advice milse! 🌅\n\n"
                    "You'll receive a daily 7 AM farming advisory. Type 'daily report' to unsubscribe."
                )
            else:
                send_text_message(from_number,
                    "⏰ Daily Morning Report unsubscribed.\nType 'daily report' to subscribe again."
                )
            return

        # ── GOVT SCHEMES ──
        if cmd == "schemes":
            send_text_message(from_number, get_all_schemes_menu())
            return

        if cmd and cmd.startswith("scheme:"):
            key = cmd.split(":", 1)[1]
            if key == "all":
                send_text_message(from_number, get_all_schemes_menu())
            else:
                send_text_message(from_number, get_scheme_details(key))
            return

        # Check if user replied 1-6 for scheme (after seeing scheme menu)
        scheme_map = {
            "1": "pm_kisan", "2": "crop_insurance", "3": "kcc",
            "4": "soil_health", "5": "pm_kusum", "6": "gujarat_schemes"
        }
        # Detect inline scheme query from any message
        scheme_key = detect_scheme_query(text)
        if scheme_key and scheme_key != "all" and cmd is None:
            send_text_message(from_number, get_scheme_details(scheme_key))
            return

        # ── MANDI PRICES ──
        if cmd == "mandi":
            crop = _extract_crop_from_text(text, known_crops)
            if not crop:
                send_text_message(from_number,
                    "💹 *Mandi Bhav*\n\nKyaa paak no bhav joiSe? (Which crop?)\n\n"
                    "Example:\n• 'Cotton price'\n• 'kapas bhav'\n• 'wheat mandi'"
                )
                return
            price_data = get_mandi_price(crop, known_location or "Gujarat")
            send_text_message(from_number, format_mandi_whatsapp(price_data))
            # Offer quick actions
            await asyncio.sleep(0.5)
            send_text_message(from_number,
                "💡 *Tip:* Type 'pm kisan' for ₹6000/year scheme OR 'calendar' for crop schedule."
            )
            return

        # ── CROP CALENDAR ──
        if cmd == "calendar":
            crop = _extract_crop_from_text(text, known_crops)
            if not crop:
                available = ", ".join(CROP_CALENDAR.keys())
                send_text_message(from_number,
                    f"📅 *Paak Calendar*\n\nKyaa paak? (Which crop?)\n"
                    f"Available: {available}\n\nExample: 'cotton calendar' or 'kapas calendar'"
                )
                return
            send_text_message(from_number, format_crop_calendar_whatsapp(crop))
            return

        # ── FERTILIZER ──
        if cmd == "fertilizer":
            crop = _extract_crop_from_text(text, known_crops)
            if not crop:
                send_text_message(from_number,
                    "🧪 *Khaad Advisory*\n\nKyaa paak? (Which crop?)\n"
                    "Example: 'wheat fertilizer' or 'gheun khaad'"
                )
                return
            send_text_message(from_number, get_fertilizer_advice(crop, text))
            return

        # ── PEST/DISEASE ──
        if cmd == "pest":
            crop = _extract_crop_from_text(text, known_crops)
            # Extract pest/disease name
            pest_keywords = ["bollworm", "whitefly", "aphid", "rust", "blight", "blast", "jassid", "mite"]
            detected_pest = next((p for p in pest_keywords if p in text.lower()), None)
            if not crop or not detected_pest:
                send_text_message(from_number,
                    "🐛 *Jeevaat & Bimari*\n\nPlease specify crop and pest/disease.\n\n"
                    "Example:\n• 'Cotton bollworm'\n• 'Wheat rust'\n• 'Rice blast'\n• 'Potato blight'"
                )
                return
            send_text_message(from_number, get_pest_disease_advice(crop, pest=detected_pest))
            return

        # ── WEATHER ONLY (Command 1) ──
        if cmd == "weather_only":
            loc = known_location or "Ahmedabad"
            from services.weather_service import fetch_weather
            climate = fetch_weather(loc)
            season = _get_season()
            weather_str = (
                f"🌡️ {climate.temperature}°C (feels {climate.feels_like}°C)\n"
                f"💧 Humidity: {climate.humidity}%\n"
                f"🌧️ Rain: {climate.rainfall}mm\n"
                f"💨 Wind: {climate.wind_speed} km/h\n"
                f"☀️ UV: {climate.uv_index} | 👁️ Vis: {climate.visibility}km\n"
                f"🌤️ {climate.weather_condition}"
            )
            send_weather_card(from_number, climate.location, weather_str, season)
            await asyncio.sleep(0.8)
            send_forecast_card(from_number, climate.forecast or [])
            return

        # ──────────────────────────────────────────────────────
        # FULL AI PIPELINE (Default — any crop/weather/farming query)
        # ──────────────────────────────────────────────────────
        normalized = normalize_input(
            user_message=text,
            current_location=known_location,
            known_crops=known_crops,
            history=history,
        )

        # Non-agri query
        if not normalized.is_valid_agri_query:
            send_text_message(from_number,
                "🌾 *Kisan Saathi*\n\n"
                "Hu sirf kheti, pavman ane paak related prshnna jawab aapi shakhu chhu.\n\n"
                "I can only help with farming, crops, weather & irrigation. "
                "Type *menu* to see all features! 📋"
            )
            return

        # Missing location/crop
        missing = []
        if normalized.crop.lower() == "unknown":
            missing.append("🌾 Paak / Crop (e.g., Cotton, Wheat)")
        if normalized.location.lower() == "unknown":
            missing.append("📍 Sthan / Location (e.g., Rajkot, Surat)")

        if missing:
            reply = "🌾 *Kisan Saathi*\n\nSachat salah mate, please kaho:\n"
            for m in missing:
                reply += f"\n• {m}"
            reply += "\n\n_Or type *profile* to update your details._"
            send_text_message(from_number, reply)
            return

        # Save context
        memory_service.save_location(session_id, normalized.location)
        memory_service.save_crop(session_id, normalized.crop)

        # Stage 2–5 pipeline
        climate = analyze_climate(normalized)
        risks = calculate_risk(normalized, climate)
        decisions = generate_decision(normalized, climate, risks)
        final_reply = format_humanized_reply(normalized, decisions, climate, risks)
        memory_service.add_message(session_id, "assistant", final_reply[:300])

        season = _get_season()
        weather_str = (
            f"🌡️ {climate.temperature}°C (feels {climate.feels_like}°C)\n"
            f"💧 Humidity: {climate.humidity}%\n"
            f"🌧️ Rain: {climate.rainfall}mm\n"
            f"💨 Wind: {climate.wind_speed} km/h\n"
            f"☀️ UV: {climate.uv_index}\n"
            f"🌤️ {climate.weather_condition}"
        )

        # Send 1: Weather card
        send_weather_card(from_number, climate.location, weather_str, season)
        await asyncio.sleep(0.8)

        # Send 2: Risk card (only if notable)
        if risks.overall_alert in ("MEDIUM", "HIGH", "CRITICAL"):
            send_risk_card(from_number, risks.model_dump())
            await asyncio.sleep(0.8)

        # Send 3: Main AI reply
        send_text_message(from_number, final_reply)
        await asyncio.sleep(0.8)

        # Send 4: Forecast (for weather/irrigation queries)
        if climate.forecast and normalized.intent in ("weather", "irrigation", "general_advice"):
            send_forecast_card(from_number, climate.forecast)
            await asyncio.sleep(0.5)

        # Send 5: Relevant quick tip based on intent
        tips = {
            "mandi_price":   "💡 Type *mandi* to see today's crop market price.",
            "disease":       f"💡 Type '{normalized.crop} fertilizer' for NPK recommendations.",
            "pest":          f"💡 Spray only when wind < 8 km/h and no rain expected for 4 hrs.",
            "fertilizer":    "💡 Type 'soil health' to get a free government soil test card.",
            "harvest":       "💡 Type 'mandi' to check today's market prices before selling.",
            "irrigation":    "💡 Irrigate in early morning (6-8 AM) to reduce evaporation.",
        }
        tip = tips.get(normalized.intent)
        if tip:
            send_text_message(from_number, tip)

        # CRITICAL ALERT — Send extra warning
        if risks.overall_alert == "CRITICAL":
            await asyncio.sleep(1)
            send_text_message(from_number,
                f"🚨 *CRITICAL ALERT — {normalized.crop} @ {normalized.location}*\n\n"
                f"Tmara paak par turant dhyan aapvu jaruri chhe! Badha kaary aaj j karo.\n\n"
                f"⚠️ URGENT: Your crop needs immediate attention today! "
                f"Type *menu* for all options or call *1800-180-1551* for expert help."
            )

        print(f"✅ Replied to {from_number}: {normalized.crop} @ {normalized.location} | {risks.overall_alert}")

    except Exception as e:
        print(f"❌ Error for {from_number}: {e}")
        import traceback
        traceback.print_exc()
        send_text_message(from_number,
            "⚠️ Ksama karso, technical samasya chhe. 1-2 minute rahi ne fari try karo.\n"
            "Sorry, a technical issue occurred. Please try again shortly."
        )


# ─── Daily Morning Report (called by scheduler) ──────────────────

async def send_daily_morning_reports():
    """Sends proactive 7AM advisory to all subscribed farmers."""
    subscribers = memory_service.get_daily_report_subscribers()
    print(f"📬 Sending daily reports to {len(subscribers)} farmers...")

    for session_id in subscribers:
        try:
            location = memory_service.get_known_location(session_id) or "Ahmedabad"
            crops = memory_service.get_known_crops(session_id)
            from services.weather_service import fetch_weather
            climate = fetch_weather(location)

            season = _get_season()
            date_str = datetime.now().strftime("%d %b %Y")

            header = (
                f"🌅 *Good Morning! Subah Ki Salam!*\n"
                f"📅 {date_str} | 📍 {location}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"🌡️ {climate.temperature}°C | 💧{climate.humidity}% | 🌧️{climate.rainfall}mm\n"
                f"🌤️ {climate.weather_condition}\n"
                f"🌾 Season: {season}\n"
                f"━━━━━━━━━━━━━━━━━"
            )
            send_text_message(session_id, header)

            if crops:
                await asyncio.sleep(0.5)
                # Generate quick risk for primary crop
                from models.schemas import NormalizedInput
                dummy_input = NormalizedInput(
                    crop=crops[0], action="monitor", location=location,
                    intent="general_advice", is_valid_agri_query=True
                )
                risks = calculate_risk(dummy_input, climate)
                if risks.overall_alert != "LOW":
                    send_risk_card(session_id, risks.model_dump())

            await asyncio.sleep(0.5)
            send_text_message(session_id,
                "💡 Aaj ni kheti advice mate type karo tmaro savaal!\n"
                "For today's advice, just type your question.\n"
                "📋 Type *menu* for all features."
            )
        except Exception as e:
            print(f"Daily report error for {session_id}: {e}")
