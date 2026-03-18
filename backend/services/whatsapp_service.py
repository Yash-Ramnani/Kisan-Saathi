"""
Enhanced WhatsApp Cloud API service for Kisan Saathi.
Includes interactive list menus, button replies, and formatted messages.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

WHATSAPP_ACCESS_TOKEN = os.getenv("Whatsapp_Access_Token", "")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("Whatsapp_Phone_Number_ID", "")
WHATSAPP_API_URL = f"https://graph.facebook.com/v19.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"

HEADERS = {
    "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
    "Content-Type": "application/json",
}

# ─── Core Send Functions ─────────────────────────────────

def send_text_message(to: str, text: str) -> dict:
    """Sends plain text. Auto-splits if > 4000 chars."""
    MAX_LEN = 4000
    parts = [text[i:i+MAX_LEN] for i in range(0, len(text), MAX_LEN)]
    responses = []
    for part in parts:
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"preview_url": False, "body": part},
        }
        resp = requests.post(WHATSAPP_API_URL, json=payload, headers=HEADERS, timeout=15)
        if not resp.ok:
            print(f"WhatsApp send error {resp.status_code}: {resp.text[:200]}")
        responses.append(resp.json())
    return responses[0] if len(responses) == 1 else {"parts": responses}


def send_interactive_list(to: str, header: str, body: str, footer: str, button_text: str, sections: list) -> dict:
    """
    Sends a WhatsApp interactive list message.
    sections = [{"title": "Section Name", "rows": [{"id": "id1", "title": "...", "description": "..."}]}]
    """
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": header},
            "body": {"text": body},
            "footer": {"text": footer},
            "action": {
                "button": button_text,
                "sections": sections,
            }
        }
    }
    resp = requests.post(WHATSAPP_API_URL, json=payload, headers=HEADERS, timeout=15)
    if not resp.ok:
        print(f"Interactive list error {resp.status_code}: {resp.text[:200]}")
        # Fall back to plain text
        fallback = f"*{header}*\n{body}\n{footer}"
        return send_text_message(to, fallback)
    return resp.json()


def send_interactive_buttons(to: str, body: str, buttons: list, header: str = None, footer: str = None) -> dict:
    """
    Sends up to 3 quick-reply buttons.
    buttons = [{"id": "btn1", "title": "Button Text"}]
    """
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": b["id"], "title": b["title"][:20]}}
                    for b in buttons[:3]
                ]
            }
        }
    }
    if header:
        payload["interactive"]["header"] = {"type": "text", "text": header}
    if footer:
        payload["interactive"]["footer"] = {"text": footer}

    resp = requests.post(WHATSAPP_API_URL, json=payload, headers=HEADERS, timeout=15)
    if not resp.ok:
        print(f"Button error {resp.status_code}: {resp.text[:200]}")
        fallback = body + "\n" + "\n".join(f"• {b['title']}" for b in buttons)
        return send_text_message(to, fallback)
    return resp.json()


def mark_as_read(message_id: str) -> dict:
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id,
    }
    resp = requests.post(WHATSAPP_API_URL, json=payload, headers=HEADERS, timeout=10)
    return resp.json()


# ─── Specialized Message Builders ──────────────────────────────

def send_main_menu(to: str, farmer_name: str = "ખેડૂત"):
    """Sends the main interactive feature menu."""
    return send_interactive_list(
        to=to,
        header="🌾 Kisan Saathi — કિસaathi ia Saathi",
        body=f"નMaste {farmer_name}! 👋 આJ આ ખ service na featur કstomize ChoOse k karo:\n\nHello! Choose a service below:",
        footer="Powered by AI 🤖 | Free for Farmers",
        button_text="🌿 Service ChoOse Karo",
        sections=[
            {
                "title": "🌦️ Havaman & Kheti",
                "rows": [
                    {"id": "weather", "title": "🌤️ Havaman Report", "description": "Real-time weather + 5-day forecast"},
                    {"id": "advisory", "title": "🌾 AI Kheti Advice", "description": "Crop-specific advisory with risk analysis"},
                    {"id": "calendar", "title": "📅 Paak Calendar", "description": "Sowing, stage & harvest schedule"},
                ]
            },
            {
                "title": "💰 Bazaar & Yojana",
                "rows": [
                    {"id": "mandi", "title": "💹 Mandi Bhav", "description": "Crop market prices (MSP + live rates)"},
                    {"id": "schemes", "title": "🏛️ Sarkar Yojana", "description": "PM KISAN, Fasal Bima, KCC & more"},
                ]
            },
            {
                "title": "🧪 Kheti Support",
                "rows": [
                    {"id": "fertilizer", "title": "🧪 Khaad Advisory", "description": "NPK recommendations for your crop"},
                    {"id": "pest", "title": "🐛 Jeevaat & Bimari", "description": "Pest & disease management"},
                    {"id": "profile", "title": "👤 Maro Profile", "description": "View & update your farmer profile"},
                ]
            },
            {
                "title": "⚙️ Settings",
                "rows": [
                    {"id": "daily_report", "title": "⏰ Daily Report", "description": "Subscribe to 7AM morning advisory"},
                    {"id": "help", "title": "❓ Help & Tips", "description": "How to use Kisan Saathi"},
                ]
            }
        ]
    )


def send_weather_card(to: str, location: str, weather_str: str, season: str):
    return send_text_message(to, (
        f"🌤️ *Havaman Report — {location}*\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"{weather_str}\n"
        f"🌾 ઋ atu (Season): {season}\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"_Updated: just now_ 🕐"
    ))


def send_risk_card(to: str, risks: dict):
    def bar(score: int) -> str:
        if score >= 75: return "🔴 CRITICAL"
        if score >= 50: return "🟠 HIGH"
        if score >= 30: return "🟡 MEDIUM"
        return "🟢 LOW"

    return send_text_message(to, (
        f"📊 *Jokhm Vishleshan (Risk Intelligence)*\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"🦠 Roog Jokham: {bar(risks.get('disease_risk',0))} ({risks.get('disease_risk',0)}/100)\n"
        f"💧 Sinchai Jaroor: {bar(risks.get('irrigation_need',0))} ({risks.get('irrigation_need',0)}/100)\n"
        f"💊 Chhtankav Asar: {bar(risks.get('spray_effectiveness',0))} ({risks.get('spray_effectiveness',0)}/100)\n"
        f"🌡️ Garmi Tanaav: {bar(risks.get('heat_stress',0))} ({risks.get('heat_stress',0)}/100)\n"
        f"❄️ Thand Jokham: {bar(risks.get('frost_risk',0))} ({risks.get('frost_risk',0)}/100)\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"⚡ Overall Alert: *{risks.get('overall_alert','LOW')}*"
    ))


def send_forecast_card(to: str, forecast: list):
    if not forecast:
        return
    lines = ["📅 *5-Day Forecast / Aaagami 5 Din:*\n"]
    for day in forecast[:5]:
        rain = day.get("chance_of_rain", 0)
        emoji = "🌧️" if rain > 50 else ("⛅" if rain > 20 else "☀️")
        lines.append(
            f"{emoji} *{day.get('date','')}*: {day.get('condition','')}, "
            f"{day.get('min_temp','?')}–{day.get('max_temp','?')}°C, "
            f"🌧️{rain}%"
        )
    return send_text_message(to, "\n".join(lines))


def send_help_message(to: str):
    return send_text_message(to, (
        "❓ *Kisan Saathi — Help Guide*\n"
        "━━━━━━━━━━━━━━━━━\n"
        "📱 *Type or tap any of these:*\n\n"
        "🌤️ *Havaman:* 'Rajkot weather' or 'Rajkot ma havaman'\n"
        "🌾 *Kheti:* 'Cotton irrigation advice Surat'\n"
        "💹 *Bhav:* 'Wheat mandi price' or 'gheun bhav'\n"
        "📅 *Calendar:* 'Cotton calendar' or 'kapas calendar'\n"
        "🧪 *Khaad:* 'Rice fertilizer' or 'chawal khaad'\n"
        "🐛 *Bimari:* 'Cotton bollworm' or 'kapas jeevaat'\n"
        "🏛️ *Yojana:* 'pm kisan' or 'fasal bima' or 'yojana'\n"
        "👤 *Profile:* 'profile' or 'maro profile'\n"
        "📋 *Menu:* 'menu' or 'help'\n"
        "━━━━━━━━━━━━━━━━━\n"
        "💬 Or just type naturally in Gujarati/Hindi/English!\n"
        "📞 Support: 1800-180-1551 (Kisan Call Centre)"
    ))


# ─── Payload Parser ────────────────────────────────────────

def extract_message_details(body: dict):
    """Parses incoming WhatsApp webhook payload."""
    try:
        entry = body["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        messages = value.get("messages", [])
        if not messages:
            return None, None, None

        msg = messages[0]
        from_number = msg["from"]
        message_id = msg["id"]
        msg_type = msg.get("type", "")

        if msg_type == "text":
            text = msg["text"]["body"].strip()
        elif msg_type == "interactive":
            interactive = msg.get("interactive", {})
            itype = interactive.get("type")
            if itype == "button_reply":
                text = interactive["button_reply"].get("id") or interactive["button_reply"].get("title")
            elif itype == "list_reply":
                text = interactive["list_reply"].get("id") or interactive["list_reply"].get("title")
            else:
                text = None
        else:
            text = None

        return from_number, text, message_id
    except Exception as e:
        print(f"Payload parse error: {e}")
        return None, None, None
