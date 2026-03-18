"""
Enhanced memory service with full farmer profile support.
Tracks: location, crops, sowing dates, land size, soil type, conversation history.
"""
from typing import Dict, List, Optional
from datetime import datetime

_sessions: Dict[str, dict] = {}

def _init_session(session_id: str) -> dict:
    if session_id not in _sessions:
        _sessions[session_id] = {
            "location": None,
            "crops": [],
            "sowing_dates": {},       # crop -> date
            "land_size_acres": None,
            "soil_type": None,
            "language": "gu",         # gu=Gujarati, hi=Hindi, en=English
            "history": [],
            "joined_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "state": "normal",        # 'normal' | 'awaiting_location' | 'awaiting_crop'
            "alert_subscribed": True, # opt-in for proactive alerts
            "daily_report": False,    # opt-in for daily morning report
            "message_count": 0,
        }
    return _sessions[session_id]

def get_session(session_id: str) -> dict:
    return _init_session(session_id)

def save_location(session_id: str, location: str):
    sess = get_session(session_id)
    if location and location.lower() not in ("unknown", "none", ""):
        sess["location"] = location
        sess["last_active"] = datetime.now().isoformat()

def save_crop(session_id: str, crop: str, sowing_date: str = None):
    sess = get_session(session_id)
    if crop and crop.lower() not in ("unknown", "none", ""):
        if crop not in sess["crops"]:
            sess["crops"].append(crop)
        if sowing_date:
            sess["sowing_dates"][crop] = sowing_date

def save_land_size(session_id: str, acres: float):
    get_session(session_id)["land_size_acres"] = acres

def save_soil_type(session_id: str, soil: str):
    get_session(session_id)["soil_type"] = soil

def set_state(session_id: str, state: str):
    get_session(session_id)["state"] = state

def get_state(session_id: str) -> str:
    return get_session(session_id).get("state", "normal")

def add_message(session_id: str, role: str, content: str):
    sess = get_session(session_id)
    sess["history"].append({"role": role, "content": content[:500]})  # trim long msgs
    sess["message_count"] += 1
    sess["last_active"] = datetime.now().isoformat()
    if len(sess["history"]) > 24:
        sess["history"] = sess["history"][-24:]

def get_history(session_id: str) -> List[dict]:
    return get_session(session_id).get("history", [])

def get_known_location(session_id: str) -> Optional[str]:
    return get_session(session_id).get("location")

def get_known_crops(session_id: str) -> List[str]:
    return get_session(session_id).get("crops", [])

def get_farmer_profile(session_id: str) -> str:
    """Returns a formatted farmer profile summary for WhatsApp."""
    sess = get_session(session_id)
    crops_str = ", ".join(sess["crops"]) if sess["crops"] else "Not set"
    loc = sess["location"] or "Not set"
    soil = sess["soil_type"] or "Not set"
    land = f"{sess['land_size_acres']} acres" if sess["land_size_acres"] else "Not set"
    msgs = sess["message_count"]

    sowing_info = ""
    if sess["sowing_dates"]:
        for crop, date in sess["sowing_dates"].items():
            sowing_info += f"\n   🌱 {crop}: Sown {date}"

    return (
        f"👨‍🌾 *તમારી પ્રોfaaHiL / Your Profile*\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"📍 Location: {loc}\n"
        f"🌾 Crops: {crops_str}{sowing_info}\n"
        f"🏞️ Land: {land}\n"
        f"🪨 Soil Type: {soil}\n"
        f"💬 Messages Sent: {msgs}\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"*Update:* Type 'location [city]' or 'crop [name]' to update your profile."
    )

def toggle_daily_report(session_id: str) -> bool:
    """Toggles daily morning report subscription. Returns new state."""
    sess = get_session(session_id)
    sess["daily_report"] = not sess.get("daily_report", False)
    return sess["daily_report"]

def get_daily_report_subscribers() -> List[str]:
    """Returns session IDs subscribed to daily reports."""
    return [sid for sid, s in _sessions.items() if s.get("daily_report")]
