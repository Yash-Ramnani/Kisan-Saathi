"""
Soil Analysis Service - Uses image processing and LLM to analyze soil conditions
"""

import re
from typing import Optional
from models.schemas import SoilAnalysisResult
from services.groq_client import generate_vision_response


CROP_RECOMMENDATIONS = {
    "clay": ["Rice", "Wheat", "Sugarcane", "Cotton"],
    "sandy": ["Groundnut", "Millets", "Watermelon", "Cucumber"],
    "loamy": ["Maize", "Soybean", "Vegetables", "Pulses"],
    "silty": ["Rice", "Wheat", "Vegetables", "Fruits"],
}

FERTILIZER_SUGGESTIONS = {
    "low": ["Apply 50kg N/acre", "Add organic manure", "Use NPK 10:26:26"],
    "medium": ["Apply 30kg N/acre", "Balanced NPK 12:12:12", "Add compost annually"],
    "high": ["Light NPK application", "Organic matter maintenance", "Biofertilizers"],
}


def _extract_field(text: str, key: str) -> str:
    pattern = rf"^\s*(?:[-*]\s*)?(?:\*\*)?{re.escape(key)}(?:\*\*)?\s*:\s*(.+)$"
    match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else ""


def _extract_block(text: str, start_key: str, end_key: Optional[str] = None) -> str:
    start_pattern = rf"\b(?:\*\*)?{re.escape(start_key)}(?:\*\*)?\s*:"
    start_match = re.search(start_pattern, text, flags=re.IGNORECASE)
    if not start_match:
        return ""

    start_index = start_match.end()
    if end_key:
        end_pattern = rf"\n\s*(?:[-*]\s*)?(?:\*\*)?{re.escape(end_key)}(?:\*\*)?\s*:"
        end_match = re.search(end_pattern, text[start_index:], flags=re.IGNORECASE)
        end_index = start_index + end_match.start() if end_match else len(text)
    else:
        end_index = len(text)

    return text[start_index:end_index].strip()


def _normalize_soil_type(value: str) -> str:
    val = value.lower().strip()
    allowed = {"clay", "sandy", "loamy", "silty"}
    if val in allowed:
        return val
    for item in allowed:
        if item in val:
            return item
    return "loamy"


def _normalize_fertility(value: str) -> str:
    val = value.lower().strip()
    allowed = {"low", "medium", "high"}
    if val in allowed:
        return val
    for item in allowed:
        if item in val:
            return item
    return "medium"


def _normalize_moisture(value: str) -> str:
    val = value.lower().strip()
    aliases = {
        "dry": "dry",
        "low": "dry",
        "optimal": "optimal",
        "normal": "optimal",
        "wet": "wet",
        "high": "wet",
    }
    if val in aliases:
        return aliases[val]
    for key, mapped in aliases.items():
        if key in val:
            return mapped
    return "optimal"


def _extract_first_field(text: str, keys: list[str]) -> str:
    for key in keys:
        value = _extract_field(text, key)
        if value:
            return value
    return ""


def analyze_soil_image(
    image_data: str,
    location: str = "Unknown",
    image_mime_type: str = "image/jpeg",
) -> SoilAnalysisResult:
    """Analyze soil image using Groq vision model and return structured + multilingual report."""

    prompt = f"""Analyze this uploaded soil image from {location} and provide output in EXACT format:

SOIL_TYPE: one of clay/sandy/loamy/silty
FERTILITY: one of low/medium/high
MOISTURE: one of dry/optimal/wet
PH: numeric value between 4.0 and 8.5
CONFIDENCE: integer 0-100
RECOMMENDED_CROPS: comma-separated crop names
FERTILIZER_SUGGESTIONS: semicolon-separated short suggestions
ENGLISH_REPORT:
A farmer-friendly report in English with sections:
- Soil summary
- Fertility and moisture
- pH interpretation
- Actionable recommendations
GUJARATI_REPORT:
Same report in Gujarati for farmer understanding.
HINDI_REPORT:
Same report in Hindi for farmer understanding.

Important:
- Do not return JSON.
- Keep crop/fertilizer recommendations practical for Indian farmers.
"""

    response = generate_vision_response(
        prompt=prompt,
        image_base64=image_data,
        image_mime_type=image_mime_type,
        system_prompt="You are an expert agronomist and soil scientist for Indian agriculture.",
    )

    soil_type_raw = _extract_first_field(response, ["SOIL_TYPE", "SOIL TYPE"])
    fertility_raw = _extract_first_field(response, ["FERTILITY", "FERTILITY_LEVEL", "FERTILITY LEVEL"])
    moisture_raw = _extract_first_field(response, ["MOISTURE", "MOISTURE_CONDITION", "MOISTURE CONDITION"])
    ph_raw = _extract_first_field(response, ["PH", "PH_LEVEL", "PH LEVEL"])
    confidence_raw = _extract_first_field(response, ["CONFIDENCE", "CONFIDENCE_SCORE", "CONFIDENCE SCORE"])

    if not soil_type_raw or not fertility_raw or not moisture_raw:
        raise ValueError("Vision response missing structured soil fields.")

    soil_type = _normalize_soil_type(soil_type_raw)
    fertility = _normalize_fertility(fertility_raw)
    moisture = _normalize_moisture(moisture_raw)

    ph_match = re.search(r"\d+(?:\.\d+)?", ph_raw)
    if not ph_match:
        raise ValueError("Vision response missing valid pH value.")
    ph_level = float(ph_match.group(0))
    ph_level = min(8.5, max(4.0, ph_level))

    confidence_match = re.search(r"\d+", confidence_raw)
    if not confidence_match:
        raise ValueError("Vision response missing confidence score.")
    confidence_val = int(confidence_match.group(0))
    confidence = min(100, max(30, confidence_val)) / 100.0

    crops_raw = _extract_first_field(response, ["RECOMMENDED_CROPS", "RECOMMENDED CROPS"])
    if not crops_raw:
        raise ValueError("Vision response missing recommended crops.")
    recommended_crops = [item.strip().title() for item in crops_raw.split(",") if item.strip()]
    if not recommended_crops:
        raise ValueError("Vision response has empty recommended crops.")

    fert_raw = _extract_first_field(response, ["FERTILIZER_SUGGESTIONS", "FERTILIZER SUGGESTIONS"])
    if not fert_raw:
        raise ValueError("Vision response missing fertilizer suggestions.")
    fertilizer_suggestions = [item.strip() for item in fert_raw.split(";") if item.strip()]
    if not fertilizer_suggestions:
        raise ValueError("Vision response has empty fertilizer suggestions.")

    english_report = _extract_block(response, "ENGLISH_REPORT", "GUJARATI_REPORT")
    gujarati_report = _extract_block(response, "GUJARATI_REPORT", "HINDI_REPORT")
    hindi_report = _extract_block(response, "HINDI_REPORT")

    if not english_report or not gujarati_report or not hindi_report:
        raise ValueError("Vision response missing one or more language reports.")

    detailed_report = (
        f"English:\\n{english_report}\\n\\n"
        f"Gujarati:\\n{gujarati_report}\\n\\n"
        f"Hindi:\\n{hindi_report}"
    )

    return SoilAnalysisResult(
        soil_type=soil_type,
        fertility_level=fertility,
        moisture_condition=moisture,
        ph_level=ph_level,
        recommended_crops=recommended_crops,
        fertilizer_suggestions=fertilizer_suggestions,
        detailed_report=detailed_report,
        report_en=english_report,
        report_gu=gujarati_report,
        report_hi=hindi_report,
        confidence_score=confidence,
    )


def get_soil_improvement_plan(soil_type: str, fertility: str) -> dict:
    """Generate improvement plan for soil."""
    plan = {
        "immediate_actions": [],
        "monthly_tasks": [],
        "seasonal_work": [],
        "long_term_improvement": [],
    }

    if fertility == "low":
        plan["immediate_actions"].append("Apply compost or FYM (20 tons/acre)")
        plan["immediate_actions"].append("Use NPK fertilizer 10:26:26")

    if soil_type == "sandy":
        plan["immediate_actions"].append("Add organic matter to improve water retention")

    plan["monthly_tasks"].append("Monitor soil moisture")
    plan["monthly_tasks"].append("Check for pests and diseases")
    plan["monthly_tasks"].append("Apply foliar sprays as needed")

    plan["seasonal_work"].append("Crop rotation every year")
    plan["seasonal_work"].append("Green manuring in off-season")

    plan["long_term_improvement"].append("Build soil organic matter (target: 3-5%)")
    plan["long_term_improvement"].append("Maintain soil health through sustainable practices")
    plan["long_term_improvement"].append("Regular soil testing (every 2 years)")

    return plan
