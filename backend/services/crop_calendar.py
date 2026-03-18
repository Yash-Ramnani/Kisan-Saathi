"""
Crop Calendar Service — Provides crop-specific sowing, growing, and harvest schedules
with stage-wise agronomic advice for Indian conditions.
"""
from datetime import datetime

MONTH = datetime.now().month

# Comprehensive crop calendar for Indian conditions
CROP_CALENDAR = {
    "Cotton": {
        "kharif": True,
        "sowing_months": [4, 5, 6],
        "harvest_months": [10, 11, 12],
        "stages": [
            {"name": "ભૂમિ તૈયારી / Land Prep", "months": [3, 4], "days": "0–15",
             "advice": "Deep ploughing 30cm. Add 10 tonnes FYM/acre. Soil pH 6–8 ideal."},
            {"name": "વાવણી / Sowing", "months": [5, 6], "days": "15–30",
             "advice": "Seed rate: 1.5 kg/acre. Row spacing: 90×60 cm. Treat seed with Imidacloprid."},
            {"name": "અંકુરણ / Germination", "months": [6], "days": "30–45",
             "advice": "Ensure soil moisture. Thin to 1 plant/hill at 10 days."},
            {"name": "વૃદ્ધિ / Vegetative", "months": [7, 8], "days": "45–90",
             "advice": "Apply N:P:K 50:25:25 kg/acre. Irrigate every 10–12 days. Weed control at 30 days."},
            {"name": "ફૂલ / Flowering", "months": [8, 9], "days": "90–120",
             "advice": "Critical irrigation period. Spray Boron 1g/L. Watch for bollworm."},
            {"name": "બોલ વિકાસ / Boll Development", "months": [9, 10], "days": "120–150",
             "advice": "Reduce irrigation. Spray ethephon if needed for early opening."},
            {"name": "લણણી / Harvest", "months": [10, 11, 12], "days": "150–180",
             "advice": "Pick when 60% bolls open. Do 3–4 pickings. Store in dry place."},
        ],
        "common_pests": ["Bollworm", "Whitefly", "Aphid", "Jassid"],
        "water_need": "High — 700-800mm total",
        "fertilizer": "N:120, P:60, K:60 kg/ha",
    },
    "Wheat": {
        "kharif": False,
        "sowing_months": [11, 12],
        "harvest_months": [3, 4],
        "stages": [
            {"name": "ભૂમિ તૈયારી / Land Prep", "months": [10, 11], "days": "0–10",
             "advice": "2–3 ploughings. Level field. Apply 8–10 t FYM. Pre-sowing irrigation (paleva)."},
            {"name": "વાવણી / Sowing", "months": [11, 12], "days": "10–20",
             "advice": "Seed rate: 100 kg/acre. Depth: 5cm. Spacing: 22.5 cm rows. Use certified seed."},
            {"name": "ફૂટ / Crown Root", "months": [12], "days": "20–35",
             "advice": "First irrigation at Crown Root Initiation (21 days). Apply 1/3 N dose."},
            {"name": "ટિلेरिंग / Tillering", "months": [12, 1], "days": "35–65",
             "advice": "Apply herbicide (Clodinafop) at 30–35 DAS. Second irrigation."},
            {"name": "જ્વાળા / Jointing", "months": [1, 2], "days": "65–90",
             "advice": "Apply remaining N. Critical irrigation. Watch for yellow rust."},
            {"name": "ફૂલ / Flowering", "months": [2], "days": "90–105",
             "advice": "Irrigation essential. Avoid water stress. Spray fungicide for rust prevention."},
            {"name": "દાણા ભરણ / Grain Filling", "months": [2, 3], "days": "105–120",
             "advice": "Foliar spray of 2% urea. Last irrigation at grain filling."},
            {"name": "પાક / Harvest", "months": [3, 4], "days": "120–150",
             "advice": "Harvest at 12–14% moisture. Use combine harvester if available."},
        ],
        "common_pests": ["Yellow Rust", "Brown Rust", "Aphid", "Termite"],
        "water_need": "Medium — 400-500mm (5–6 irrigations)",
        "fertilizer": "N:120, P:60, K:40 kg/ha",
    },
    "Rice": {
        "kharif": True,
        "sowing_months": [6, 7],
        "harvest_months": [10, 11],
        "stages": [
            {"name": "નર્સરી / Nursery", "months": [5, 6], "days": "0–25",
             "advice": "Raise nursery in 1/10th area. Seed rate: 25 kg/acre. Maintain 2.5cm water."},
            {"name": "રોપણી / Transplanting", "months": [6, 7], "days": "25–35",
             "advice": "Transplant 2–3 seedlings/hill at 20×15 cm. Apply Basal NPK."},
            {"name": "ટiलेरिंg / Tillering", "months": [7, 8], "days": "35–60",
             "advice": "Maintain 5cm water. Apply N top dressing. Weed management."},
            {"name": "ઘૂઘા / Panicle Initiation", "months": [8, 9], "days": "60–80",
             "advice": "Apply Potash. Control sheath blight. Maintain water level."},
            {"name": "ફૂલ / Flowering", "months": [9], "days": "80–95",
             "advice": "Ensure water. Do not allow dry stress. Spray zinc if deficiency seen."},
            {"name": "દાણા / Grain Filling", "months": [9, 10], "days": "95–120",
             "advice": "Drain water 10 days before harvest. Monitor for gall midge."},
            {"name": "લણણી / Harvest", "months": [10, 11], "days": "120–140",
             "advice": "Harvest at 80% grain maturity. Moisture < 20%. Dry to 14% before storage."},
        ],
        "common_pests": ["Brown Plant Hopper", "Stem Borer", "Blast", "Sheath Blight"],
        "water_need": "Very High — 1200-1400mm",
        "fertilizer": "N:120, P:60, K:60 kg/ha",
    },
    "Groundnut": {
        "kharif": True,
        "sowing_months": [6, 7],
        "harvest_months": [10, 11],
        "stages": [
            {"name": "વાવણી / Sowing", "months": [6, 7], "days": "0–10",
             "advice": "Seed rate: 80 kg/acre (bold). Depth: 5–6 cm. Treat with Rhizobium."},
            {"name": "અંકુરણ / Germination", "months": [6, 7], "days": "10–20",
             "advice": "Ensure soil moisture. Replant gaps within 7–10 days."},
            {"name": "વૃદ્ધિ / Vegetative", "months": [7, 8], "days": "20–40",
             "advice": "Top dress with Gypsum 200 kg/acre at pegging. Earthing up."},
            {"name": "ફૂVIZAi / Flowering & Pegging", "months": [8], "days": "40–65",
             "advice": "Critical irrigation. Apply calcium. Avoid waterlogging."},
            {"name": "પૉડ ભરણ / Pod Filling", "months": [9], "days": "65–95",
             "advice": "Foliar spray of 1% MgSO4. Monitor Tikka leaf spot."},
            {"name": "પરિપક્વ / Maturity", "months": [10], "days": "95–120",
             "advice": "Check maturity by peeling sample pods. Inner pericarp turns dark."},
            {"name": "ખોદ / Harvest", "months": [10, 11], "days": "120–130",
             "advice": "Harvest before rains. Windrow and dry in field for 3–4 days."},
        ],
        "common_pests": ["Tikka Leaf Spot", "Bud Necrosis", "White Grub", "Aphid"],
        "water_need": "Medium — 500-600mm",
        "fertilizer": "N:20, P:40, K:40 + Gypsum:200 kg/ha",
    },
    "Potato": {
        "kharif": False,
        "sowing_months": [10, 11],
        "harvest_months": [1, 2, 3],
        "stages": [
            {"name": "ભૂમિ / Land Prep", "months": [9, 10], "days": "0",
             "advice": "Deep ploughing. Ridges at 60–75 cm. Apply 20 t FYM."},
            {"name": "વાવણી / Planting", "months": [10, 11], "days": "0–15",
             "advice": "Seed rate: 10–12 quintal/acre. Depth: 5–7cm. Pre-treat with fungicide."},
            {"name": "અંકુરણ / Emergence", "months": [11], "days": "15–25",
             "advice": "Keep soil moist. Apply pre-emergence herbicide (Pendimethalin)."},
            {"name": "ગ્રૉe / Vegetative", "months": [11, 12], "days": "25–55",
             "advice": "Earthing up at 25 DAS. Apply N top dressing. Control aphids (virus vector)."},
            {"name": "ઓળ / Tuber Initiation", "months": [12, 1], "days": "55–75",
             "advice": "Maintain soil moisture. Apply 60 kg K2O. Watch for late blight."},
            {"name": "ઓળ ભરણ / Tuber Filling", "months": [1], "days": "75–90",
             "advice": "Continue irrigation. Spray Mancozeb for blight prevention. Avoid waterlogging."},
            {"name": "ખોદ / Harvest", "months": [1, 2, 3], "days": "90–110",
             "advice": "Haulm kill 2 weeks before harvest. Harvest at 80% skin set. Avoid greening."},
        ],
        "common_pests": ["Late Blight", "Aphid", "Cutworm", "Scab"],
        "water_need": "Medium-High — 400-600mm (8–10 irrigations)",
        "fertilizer": "N:120, P:80, K:120 kg/ha",
    },
}

def get_current_stage(crop: str) -> dict | None:
    """Returns the current crop stage based on current month."""
    data = CROP_CALENDAR.get(crop)
    if not data:
        return None

    current_month = datetime.now().month
    current_stage = None
    for stage in data["stages"]:
        if current_month in stage["months"]:
            current_stage = stage
            break

    if not current_stage and data["stages"]:
        # Off-season — show next upcoming stage
        for stage in data["stages"]:
            if min(stage["months"]) > current_month:
                current_stage = stage
                current_stage["upcoming"] = True
                break

    return {
        "crop": crop,
        "current_stage": current_stage,
        "sowing_months": data["sowing_months"],
        "harvest_months": data["harvest_months"],
        "common_pests": data["common_pests"],
        "water_need": data["water_need"],
        "fertilizer": data["fertilizer"],
        "season": "Kharif" if data["kharif"] else "Rabi",
    }

MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}

def format_crop_calendar_whatsapp(crop: str) -> str:
    """Formats crop calendar info as WhatsApp message."""
    data = get_current_stage(crop)
    if not data:
        return f"📅 Sorry, crop calendar for *{crop}* is not available yet.\nAvailable crops: {', '.join(CROP_CALENDAR.keys())}"

    stage = data["current_stage"]
    sow_months = ", ".join(MONTH_NAMES.get(m, "") for m in data["sowing_months"])
    harv_months = ", ".join(MONTH_NAMES.get(m, "") for m in data["harvest_months"])

    msg = (
        f"📅 *{crop} — પાક કૅલેન્ડર*\n"
        f"🌾 ઋતુ: {data['season']}\n"
        f"━━━━━━━━━━━━━━━━━\n"
    )

    if stage:
        upcoming_tag = " (Upcoming 🔜)" if stage.get("upcoming") else " ✅ NOW"
        msg += (
            f"📍 *વર્તમાન તબક્કો{upcoming_tag}*\n"
            f"   {stage['name']}\n"
            f"💡 {stage['advice']}\n"
            f"━━━━━━━━━━━━━━━━━\n"
        )

    msg += (
        f"🌱 વાવણી: {sow_months}\n"
        f"🌾 લણણી: {harv_months}\n"
        f"💧 પાણી: {data['water_need']}\n"
        f"🧪 ખાતર: {data['fertilizer']}\n"
        f"🐛 સામાન્ય જીવાત: {', '.join(data['common_pests'])}\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"_(Crop: {crop} | Season: {data['season']})_"
    )
    return msg
