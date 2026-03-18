"""
Mandi (Crop Market Price) Service for Kisan Saathi.
Uses data.gov.in API if key is set, otherwise uses realistic price data.
Prices in INR per quintal (100 kg).
"""
import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY", "")

# Realistic MSP + market price data (INR per quintal) as of 2025-26 season
# Source: CACP MSP + AGMARKNET averages
BASE_PRICES = {
    "Wheat":          {"min": 2115, "max": 2400, "msp": 2275,  "unit": "quintal"},
    "Rice":           {"min": 2183, "max": 2600, "msp": 2300,  "unit": "quintal"},
    "Cotton":         {"min": 6080, "max": 7200, "msp": 7121,  "unit": "quintal"},
    "Maize":          {"min": 1850, "max": 2200, "msp": 2090,  "unit": "quintal"},
    "Soybean":        {"min": 3950, "max": 4600, "msp": 4892,  "unit": "quintal"},
    "Groundnut":      {"min": 5550, "max": 6500, "msp": 6783,  "unit": "quintal"},
    "Sugarcane":      {"min": 315,  "max": 355,  "msp": 340,   "unit": "quintal"},
    "Onion":          {"min": 400,  "max": 2800, "msp": None,  "unit": "quintal"},
    "Potato":         {"min": 600,  "max": 1800, "msp": None,  "unit": "quintal"},
    "Tomato":         {"min": 300,  "max": 4000, "msp": None,  "unit": "quintal"},
    "Pearl Millet":   {"min": 2250, "max": 2600, "msp": 2625,  "unit": "quintal"},
    "Sorghum":        {"min": 2950, "max": 3400, "msp": 3371,  "unit": "quintal"},
    "Mustard":        {"min": 5200, "max": 6000, "msp": 5950,  "unit": "quintal"},
    "Banana":         {"min": 800,  "max": 2500, "msp": None,  "unit": "quintal"},
    "Mango":          {"min": 1500, "max": 5000, "msp": None,  "unit": "quintal"},
    "Turmeric":       {"min": 7000, "max": 14000,"msp": None,  "unit": "quintal"},
    "Garlic":         {"min": 1500, "max": 8000, "msp": None,  "unit": "quintal"},
}

# Regional price adjustments (multiplier)
REGIONAL_FACTORS = {
    "gujarat":     1.02,
    "punjab":      1.05,
    "maharashtra": 1.01,
    "rajasthan":   0.97,
    "haryana":     1.04,
    "madhya pradesh": 0.96,
    "uttar pradesh": 0.98,
    "karnataka":   1.01,
}

def get_mandi_price(crop: str, location: str = "") -> dict:
    """
    Gets crop market price. Tries real API first, falls back to MSP-based estimate.
    """
    # Try real API if key is set
    if DATA_GOV_API_KEY:
        result = _fetch_agmarknet(crop, location)
        if result:
            return result

    return _get_estimated_price(crop, location)


def _fetch_agmarknet(crop: str, location: str) -> dict | None:
    """Fetches from data.gov.in AGMARKNET dataset."""
    try:
        url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        params = {
            "api-key": DATA_GOV_API_KEY,
            "format": "json",
            "filters[Commodity]": crop,
            "filters[State]": location,
            "limit": 5,
        }
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        records = data.get("records", [])
        if not records:
            return None

        rec = records[0]
        return {
            "crop": crop,
            "market": rec.get("Market", location),
            "min_price": float(rec.get("Min Price", 0)),
            "max_price": float(rec.get("Max Price", 0)),
            "modal_price": float(rec.get("Modal Price", 0)),
            "msp": BASE_PRICES.get(crop, {}).get("msp"),
            "date": rec.get("Arrival Date", datetime.now().strftime("%d/%m/%Y")),
            "source": "AGMARKNET (Live)",
        }
    except Exception as e:
        print(f"AGMARKNET API error: {e}")
        return None


def _get_estimated_price(crop: str, location: str) -> dict:
    """Returns MSP-based estimated price with regional adjustment."""
    import random
    normalized_crop = crop.strip().capitalize()
    price_data = BASE_PRICES.get(normalized_crop, {
        "min": 1000, "max": 3000, "msp": None, "unit": "quintal"
    })

    # Apply regional factor
    loc_lower = location.lower()
    factor = 1.0
    for region, f in REGIONAL_FACTORS.items():
        if region in loc_lower:
            factor = f
            break

    min_p = int(price_data["min"] * factor)
    max_p = int(price_data["max"] * factor)
    modal_p = int((min_p + max_p) / 2 * random.uniform(0.95, 1.05))

    msp = price_data.get("msp")
    trend = "📈 ઉપર" if modal_p > (msp or modal_p) * 0.98 else "📉 નીચે"

    return {
        "crop": normalized_crop,
        "market": location or "Gujarat",
        "min_price": min_p,
        "max_price": max_p,
        "modal_price": modal_p,
        "msp": msp,
        "trend": trend,
        "date": datetime.now().strftime("%d/%m/%Y"),
        "source": "MSP-based Estimate",
    }


def format_mandi_whatsapp(price_data: dict) -> str:
    """Formats mandi price data as a WhatsApp message."""
    msp_line = f"🏛️ MSP: ₹{price_data['msp']:,}/quintal" if price_data.get("msp") else ""
    trend = price_data.get("trend", "")

    msg = (
        f"💹 *{price_data['crop']} — બજાર ભાવ*\n"
        f"📍 {price_data['market']} | 📅 {price_data['date']}\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"💰 ન્યૂનતમ: ₹{price_data['min_price']:,}/quintal\n"
        f"💰 મહત્તમ: ₹{price_data['max_price']:,}/quintal\n"
        f"💰 *સામાન્ય ભાવ: ₹{price_data['modal_price']:,}/quintal*\n"
    )
    if msp_line:
        msg += f"{msp_line}\n"
    if trend:
        msg += f"📊 ટ્રેન્ડ: {trend}\n"
    msg += (
        f"━━━━━━━━━━━━━━━━━\n"
        f"_(Source: {price_data['source']})_\n\n"
        f"📈 *Market Price | {price_data['crop']}*\n"
        f"Min: ₹{price_data['min_price']:,} | Max: ₹{price_data['max_price']:,}\n"
        f"Modal: ₹{price_data['modal_price']:,} per quintal"
    )
    return msg
