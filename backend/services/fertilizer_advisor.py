"""
Fertilizer & Soil Advisor for Kisan Saathi.
Provides NPK recommendations, micronutrient advice, and organic farming tips
based on crop type, growth stage, and climate data.
"""

# NPK and micronutrient recommendations per crop (kg/ha)
FERTILIZER_GUIDE = {
    "Cotton": {
        "basal": {"N": 50, "P": 25, "K": 25, "Boron": "1 kg/ha"},
        "top_dress_1": {"N": 40, "timing": "At 30 DAS (vegetative)"},
        "top_dress_2": {"N": 30, "timing": "At 60 DAS (squaring)"},
        "micronutrients": ["Zinc 25 kg ZnSO4/ha", "Boron 1 kg/ha at flowering"],
        "organic": "Vermicompost 2 t/ha OR FYM 10 t/ha in basal",
        "deficiency_signs": {
            "N": "Pale yellow leaves, starting from older leaves",
            "P": "Purple/reddish leaves, poor root development",
            "K": "Leaf margin burn, boll shedding",
            "Zn": "Small leaves, interveinal chlorosis",
        }
    },
    "Wheat": {
        "basal": {"N": 60, "P": 60, "K": 40},
        "top_dress_1": {"N": 60, "timing": "At Crown Root Initiation (21 DAS)"},
        "micronutrients": ["Zinc 25 kg ZnSO4/ha if deficient"],
        "organic": "FYM 10 t/ha 2 weeks before sowing",
        "deficiency_signs": {
            "N": "Yellowing from older leaves, poor tillering",
            "P": "Dark green/purple leaves, delayed heading",
            "K": "Leaf tip/margin necrosis",
            "Zn": "White/light green stripes on newer leaves",
        }
    },
    "Rice": {
        "basal": {"N": 50, "P": 26, "K": 33, "Zn": "ZnSO4 25 kg/ha"},
        "top_dress_1": {"N": 35, "timing": "At Active Tillering (25-30 DAS)"},
        "top_dress_2": {"N": 35, "timing": "At Panicle Initiation"},
        "micronutrients": ["Zinc 25 kg ZnSO4/ha basal", "Sulphur 30 kg/ha"],
        "organic": "Green manure (Dhaincha) incorporation + FYM 5 t/ha",
        "deficiency_signs": {
            "N": "Light yellow-green color, slow growth",
            "K": "Orange-brown tips on older leaves",
            "Zn": "Brown spots, khaira disease (pale green stripe)",
            "Fe": "Interveinal chlorosis in young leaves",
        }
    },
    "Potato": {
        "basal": {"N": 75, "P": 80, "K": 120},
        "top_dress_1": {"N": 45, "timing": "At 25–30 DAS (earthing up)"},
        "micronutrients": ["Boron 1.5 kg/ha", "Magnesium sulphate 20 kg/ha"],
        "organic": "FYM 20 t/ha 2 weeks before planting",
        "deficiency_signs": {
            "N": "Light green leaves, stunted growth",
            "K": "Leaf rolling, reduced tuber size",
            "Mg": "Interveinal chlorosis (older leaves)",
            "Ca": "Hollow heart in tubers",
        }
    },
    "Groundnut": {
        "basal": {"N": 10, "P": 40, "K": 40, "Gypsum": "200 kg/ha at pegging"},
        "micronutrients": ["Zinc 25 kg ZnSO4/ha", "Boron foliar spray 0.1%"],
        "inoculant": "Rhizobium seed treatment + PSB biofertilizer",
        "organic": "FYM 5 t/ha or compost 3 t/ha basal",
        "deficiency_signs": {
            "Ca": "Empty pods, poor kernel filling",
            "S": "Yellowing of younger leaves",
            "Zn": "Short internodes, smaller leaflets",
            "Mg": "Interveinal chlorosis",
        }
    },
    "Maize": {
        "basal": {"N": 60, "P": 60, "K": 40},
        "top_dress_1": {"N": 60, "timing": "At knee-high stage (V6)"},
        "top_dress_2": {"N": 60, "timing": "At tasseling"},
        "micronutrients": ["Zinc 25 kg ZnSO4/ha", "Boron 1 kg/ha"],
        "organic": "FYM 10 t/ha basal",
        "deficiency_signs": {
            "N": "V-shaped yellowing from leaf tip",
            "K": "Tip and margin burning on lower leaves",
            "Zn": "Whitish stripe on young leaves (white bud)",
            "S": "Yellowing of entire young leaf",
        }
    },
}

def get_fertilizer_advice(crop: str, issue: str = None) -> str:
    """Returns fertilizer recommendation for a crop."""
    data = FERTILIZER_GUIDE.get(crop.capitalize())
    if not data:
        return f"🧪 Sorry, detailed fertilizer guide for *{crop}* is not available yet. Please consult your local agriculture officer."

    basal = data["basal"]
    basal_str = ", ".join(f"{k}: {v} kg/ha" for k, v in basal.items() if isinstance(v, (int, float)))
    for k, v in basal.items():
        if isinstance(v, str):
            basal_str += f", {k}: {v}"

    msg = (
        f"🧪 *{crop} — ખાd Advisoryr*\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"🌱 *Basal Dose (at sowing):*\n   {basal_str}\n"
    )

    if data.get("inoculant"):
        msg += f"🦠 *Bio-fertilizer:* {data['inoculant']}\n"

    if data.get("top_dress_1"):
        td1 = data["top_dress_1"]
        msg += f"\n💊 *Top-Dressing 1:*\n   N: {td1.get('N', '')} kg/ha — {td1.get('timing', '')}\n"

    if data.get("top_dress_2"):
        td2 = data["top_dress_2"]
        msg += f"\n💊 *Top-Dressing 2:*\n   N: {td2.get('N', '')} kg/ha — {td2.get('timing', '')}\n"

    if data.get("micronutrients"):
        msg += f"\n🔬 *Micronutrients:*\n"
        for m in data["micronutrients"]:
            msg += f"   • {m}\n"

    if data.get("organic"):
        msg += f"\n🌿 *Organic Option:* {data['organic']}\n"

    # If specific deficiency issue mentioned
    if issue and data.get("deficiency_signs"):
        issue_lower = issue.lower()
        for nutrient, symptom in data["deficiency_signs"].items():
            if nutrient.lower() in issue_lower or any(w in issue_lower for w in ["yellow", "pale", "burn", "spot"]):
                msg += f"\n⚠️ *Possible Deficiency ({nutrient}):* {symptom}\n"

    msg += (
        f"━━━━━━━━━━━━━━━━━\n"
        f"💡 *Tip:* Always do a Soil Health Card test before applying heavy fertilizers.\n"
        f"📞 Free soil test: soilhealth.dac.gov.in"
    )
    return msg


def get_pest_disease_advice(crop: str, pest: str = None, disease: str = None) -> str:
    """Returns pest/disease management advice."""
    PEST_ADVICE = {
        ("Cotton", "bollworm"): {
            "name": "American Bollworm / ઈelabaroorm",
            "chemical": "Chlorpyrifos 20 EC @ 2 ml/L OR Spinosad 45 SC @ 0.5 ml/L",
            "bio": "Release of Trichogramma cards @ 50,000/acre. NPV @ 250 LE/ha",
            "timing": "Spray at first sign of damage. Repeat after 10 days if needed.",
            "ipm": "Use pheromone traps (10/acre) to monitor adult population",
        },
        ("Cotton", "whitefly"): {
            "name": "Whitefly / સfedarmakkhhi",
            "chemical": "Imidacloprid 70 WG @ 30g/acre OR Spiromesifen 22.9 SC @ 1 ml/L",
            "bio": "Release Chrysoperla cards. Spray NSKE 5%",
            "timing": "Spray morning/evening. Avoid noon.avoid repeated same chemicals",
            "ipm": "Use yellow sticky traps. Remove weeds from bunds.",
        },
        ("Wheat", "rust"): {
            "name": "Yellow Rust / Stripe Rust",
            "chemical": "Propiconazole 25 EC @ 1 ml/L OR Tebuconazole 25.9 EC @ 1 ml/L",
            "bio": "Use resistant varieties (HD-2967, WH-1105)",
            "timing": "Spray at first appearance. Repeat at 15 days",
            "ipm": "Remove infected leaves. Avoid excessive N application",
        },
        ("Rice", "blast"): {
            "name": "Rice Blast / blaaastaa",
            "chemical": "Tricyclazole 75 WP @ 0.6g/L OR Isoprothiolane 40 EC @ 1.5 ml/L",
            "bio": "Pseudomonas fluorescens seed treatment",
            "timing": "Spray at tillering and booting stage preventively",
            "ipm": "Balanced NPK. Avoid excess N. Use resistant varieties (IR-36, MTU-7029)",
        },
    }

    target = pest or disease or ""
    target_lower = target.lower()

    for (c, p), advice in PEST_ADVICE.items():
        if c.lower() == crop.lower() and p.lower() in target_lower:
            return (
                f"🐛 *{advice['name']}*\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"💊 *Chemical Control:*\n   {advice['chemical']}\n\n"
                f"🌿 *Bio Control:*\n   {advice['bio']}\n\n"
                f"⏰ *Timing:* {advice['timing']}\n\n"
                f"🔄 *IPM Strategy:* {advice['ipm']}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"⚠️ Before spraying: Check wind speed (<8km/h), avoid rain next 4 hours."
            )

    return (
        f"🐛 *{crop} — Pest/Disease Query*\n"
        f"For '{target}' — please consult your local KVK or agriculture officer for crop-specific diagnosis.\n\n"
        f"📞 KVK Helpline: 1800-180-1551"
    )
