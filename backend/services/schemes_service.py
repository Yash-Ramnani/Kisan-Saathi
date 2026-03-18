"""
Government Schemes Service for Kisan Saathi.
Provides information about PM-KISAN, crop insurance, subsidies, and state schemes.
"""

SCHEMES = {
    "pm_kisan": {
        "title": "PM KISAN Samman Nidhi",
        "gujarati": "PM કિસાન સન્માન નિધિ",
        "benefit": "₹6,000/year (₹2,000 × 3 installments) direct to bank account",
        "benefit_gu": "₹6,000/વર્ષ (₹2,000 × 3 હપ્તા) — સીધા બેંક ખાતામાં",
        "eligibility": "All small/marginal farmers with cultivable land",
        "documents": ["Aadhaar Card", "Land Records (7/12 Utara)", "Bank Account"],
        "how_to_apply": "PM-Kisan portal: pmkisan.gov.in | CSC Center | Village Patwari",
        "helpline": "155261 / 011-24300606",
        "status_link": "https://pmkisan.gov.in/BeneficiaryStatus.aspx",
    },
    "crop_insurance": {
        "title": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "gujarati": "PM ફસલ વીમા યોજના",
        "benefit": "Full crop loss coverage. Premium: only 2% (Kharif), 1.5% (Rabi)",
        "benefit_gu": "સંપૂર્ণ પાક નુકસાન વળતર. પ્રીમિયમ: ખરીફ 2%, રવિ 1.5%",
        "eligibility": "All farmers growing notified crops in notified areas",
        "documents": ["Land Records", "Bank Account", "Aadhaar", "Sowing Certificate"],
        "how_to_apply": "Bank / CSC / Insurance company office / PMFBY portal",
        "deadline": "Kharif: by July 31 | Rabi: by December 31",
        "helpline": "14447",
        "website": "https://pmfby.gov.in",
    },
    "kcc": {
        "title": "Kisan Credit Card (KCC)",
        "gujarati": "કિસાન ક્રેડિટ કાર્ડ",
        "benefit": "Crop loans up to ₹3 lakh at 4% interest. Short-term flexible credit.",
        "benefit_gu": "₹3 લાખ સુધી ક્રેડિટ — 4% વ્યાજ દરે (સરકારી સહાય સાથે)",
        "eligibility": "All farmers, sharecroppers, tenant farmers",
        "documents": ["Aadhaar", "Land Records", "Passport Photo", "Bank Account"],
        "how_to_apply": "Any nationalized bank, cooperative bank, or RRB",
        "helpline": "1800-180-1551",
    },
    "soil_health": {
        "title": "Soil Health Card Scheme",
        "gujarati": "માટી સ્વાસ્થ્ય કાર્ડ",
        "benefit": "Free soil testing every 2 years. NPK + micronutrient recommendations.",
        "benefit_gu": "મફત માટી પરીક્ષણ — NPK અને સૂક્ષ્મ પોષક તત્વો ભલામણ",
        "eligibility": "All farmers",
        "how_to_apply": "Nearest Agriculture Officer / Krishi Vigyan Kendra / soilhealth.dac.gov.in",
        "website": "https://soilhealth.dac.gov.in",
    },
    "pm_kusum": {
        "title": "PM-KUSUM Solar Pump Scheme",
        "gujarati": "PM KUSUM સૌર સિંચાઈ પંપ",
        "benefit": "90% subsidy on solar pumps (60% govt + 30% bank loan). Free electricity for irrigation.",
        "benefit_gu": "સોlar પંg પર 90% સહાય. સિંchaઈ માટે મફt વીs",
        "eligibility": "Individual farmers, farmer groups, cooperatives",
        "how_to_apply": "State nodal agency / District Agriculture Office",
    },
    "gujarat_schemes": {
        "title": "Gujarat State Schemes",
        "gujarati": "ગુજરાt સ rkerAR yojana",
        "schemes": [
            "🌱 Mukhyamantri Kisan Sahay Yojana — ₹25,000/ha for crop loss (no premium)",
            "💧 Sujalam Sufalam Jal Abhiyan — Canal renovation + water conservation",
            "🌞 Kisan Suryoday Yojana — 3-phase electricity 5 AM – 9 PM for farmers",
            "🌿 Natural Farming (Prakriti Kheti) — Subsidized cow urine/dung inputs",
            "🐄 Pashu Sakhi Yojana — Animal husbandry scheme for women farmers",
        ],
        "helpline": "Ikhedut Portal: ikhedut.gujarat.gov.in | 1800-233-4477",
    },
}

def get_all_schemes_menu() -> str:
    return (
        "🏛️ *સrkerAR yojnaAO / Government Schemes*\n"
        "━━━━━━━━━━━━━━━━━\n"
        "1️⃣ PM KISAN — ₹6,000/year cash\n"
        "2️⃣ PM Fasal Bima — Crop Insurance\n"
        "3️⃣ Kisan Credit Card — 4% interest loan\n"
        "4️⃣ Soil Health Card — Free soil test\n"
        "5️⃣ PM KUSUM — Solar pump 90% subsidy\n"
        "6️⃣ Gujarat State Schemes\n"
        "━━━━━━━━━━━━━━━━━\n"
        "👉 *Reply with scheme number* (e.g., reply '1' for PM KISAN details)\n"
        "👉 Or type: 'pm kisan', 'crop insurance', 'kcc', 'soil health', 'solar pump'"
    )

def get_scheme_details(scheme_key: str) -> str:
    scheme = SCHEMES.get(scheme_key)
    if not scheme:
        return f"❓ Scheme not found. Type *yojana* to see all schemes."

    if scheme_key == "gujarat_schemes":
        msg = (
            f"🏛️ *{scheme['title']}*\n"
            f"━━━━━━━━━━━━━━━━━\n"
        )
        for s in scheme["schemes"]:
            msg += f"{s}\n"
        msg += f"\n📞 {scheme['helpline']}"
        return msg

    msg = (
        f"🏛️ *{scheme['title']}*\n"
        f"   ({scheme['gujarati']})\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"✅ *ફાaYdo / Benefit:*\n   {scheme['benefit_gu']}\n"
        f"   _{scheme['benefit']}_\n\n"
        f"📋 *પatrtA / Eligibility:* {scheme.get('eligibility', 'N/A')}\n"
    )

    if scheme.get("documents"):
        msg += f"\n📄 *Documents:* {', '.join(scheme['documents'])}\n"

    if scheme.get("how_to_apply"):
        msg += f"\n🏢 *Apply at:* {scheme['how_to_apply']}\n"

    if scheme.get("deadline"):
        msg += f"\n⏰ *Deadline:* {scheme['deadline']}\n"

    if scheme.get("helpline"):
        msg += f"\n📞 *Helpline:* {scheme['helpline']}\n"

    if scheme.get("website"):
        msg += f"\n🌐 {scheme['website']}\n"

    return msg

def detect_scheme_query(text: str) -> str | None:
    """Detects if user is asking about a specific scheme."""
    text_lower = text.lower()
    if any(w in text_lower for w in ["pm kisan", "6000", "samman nidhi", "किसान सम्मान"]):
        return "pm_kisan"
    if any(w in text_lower for w in ["fasal bima", "insurance", "vima", "fpl", "pmfby", "crop insurance"]):
        return "crop_insurance"
    if any(w in text_lower for w in ["kcc", "kisan credit", "kredit card", "loan", "laan"]):
        return "kcc"
    if any(w in text_lower for w in ["soil health", "soil card", "mati", "soil test", "माटी"]):
        return "soil_health"
    if any(w in text_lower for w in ["solar", "kusum", "pump", "bijli", "solar pump"]):
        return "pm_kusum"
    if any(w in text_lower for w in ["gujarat", "mukhyamantri", "suryoday", "sahay"]):
        return "gujarat_schemes"
    if any(w in text_lower for w in ["yojana", "scheme", "sarkar", "government", "sarkari"]):
        return "all"
    return None
