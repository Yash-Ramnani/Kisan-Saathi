"""
Disease Detection Service - Analyzes crop images for diseases
"""

import re
from models.schemas import DiseaseDetectionResult
from services.groq_client import generate_vision_response

DISEASE_TREATMENT_DB = {
    "rust": {
        "cause": "Fungal infection",
        "treatment": [
            "Apply sulfur dust or fungicides",
            "Spray Mancozeb 2.5kg/ha",
            "Improve air circulation in field",
            "Remove infected leaves",
        ],
        "prevention": [
            "Use resistant varieties",
            "Proper crop spacing",
            "Avoid overhead irrigation",
            "Crop rotation",
        ],
    },
    "leaf_spot": {
        "cause": "Bacterial/Fungal infection",
        "treatment": [
            "Remove affected leaves",
            "Spray Chlorothalonil or Copper fungicide",
            "Apply Bacillus subtilis for biological control",
            "Maintain proper plant spacing",
        ],
        "prevention": [
            "Use disease-free seeds",
            "Avoid overhead watering",
            "Proper field hygiene",
            "Timely roguing of infected plants",
        ],
    },
    "powdery_mildew": {
        "cause": "Fungal infection",
        "treatment": [
            "Spray Sulfur dust",
            "Apply Karathane or Dinocap",
            "Improve air circulation",
            "Morning sprayings are effective",
        ],
        "prevention": [
            "Proper spacing between plants",
            "Avoid excessive nitrogen",
            "Regular monitoring",
            "Plant resistant varieties",
        ],
    },
    "blight": {
        "cause": "Phytophthora infestans",
        "treatment": [
            "Remove affected plant parts immediately",
            "Spray Mancozeb or Metalaxyl fungicide",
            "Improve drainage",
            "Avoid overhead irrigation",
        ],
        "prevention": [
            "Use certified seed material",
            "Proper crop rotation",
            "Adequate spacing",
            "Monitor weather conditions",
        ],
    },
    "wilt": {
        "cause": "Vascular fungal infection",
        "treatment": [
            "Remove and destroy infected plants",
            "Apply Trichoderma to soil",
            "Improve soil drainage",
            "Solarize infected soil",
        ],
        "prevention": [
            "Use resistant varieties",
            "Crop rotation (3+ years)",
            "Treat seeds with fungicides",
            "Maintain soil health",
        ],
    },
    "healthy": {
        "cause": "No disease detected",
        "treatment": [
            "Continue regular monitoring",
            "Maintain proper fertilization",
            "Monitor for pest activity",
            "Scout crop daily",
        ],
        "prevention": [
            "Maintain preventive sprays",
            "Regular scouting",
            "Proper agronomic practices",
            "Monitor weather",
        ],
    },
}


def _extract_field(text: str, key: str) -> str:
    pattern = rf"^{re.escape(key)}\s*:\s*(.+)$"
    match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else ""


def _extract_block(text: str, start_key: str, end_key: str = "") -> str:
    start_pattern = rf"{re.escape(start_key)}\s*:"
    start_match = re.search(start_pattern, text, flags=re.IGNORECASE)
    if not start_match:
        return ""

    start_index = start_match.end()
    if end_key:
        end_pattern = rf"\n\s*{re.escape(end_key)}\s*:"
        end_match = re.search(end_pattern, text[start_index:], flags=re.IGNORECASE)
        end_index = start_index + end_match.start() if end_match else len(text)
    else:
        end_index = len(text)

    return text[start_index:end_index].strip()


def _normalize_disease_name(value: str) -> str:
    normalized = value.lower().replace("-", "_").replace(" ", "_").strip("_")
    aliases = {
        "leafspot": "leaf_spot",
        "powdery_mildew": "powdery_mildew",
        "powdery": "powdery_mildew",
        "late_blight": "blight",
        "blight": "blight",
        "rust": "rust",
        "wilt": "wilt",
        "healthy": "healthy",
    }
    if normalized in DISEASE_TREATMENT_DB:
        return normalized
    if normalized in aliases:
        return aliases[normalized]
    for key in DISEASE_TREATMENT_DB.keys():
        if key in normalized or normalized in key:
            return key
    return "healthy"


def _normalize_severity(value: str) -> str:
    val = value.lower().strip()
    allowed = {"mild", "moderate", "severe", "healthy"}
    if val in allowed:
        return val
    if "mild" in val:
        return "mild"
    if "moderate" in val:
        return "moderate"
    if "severe" in val or "high" in val:
        return "severe"
    return "healthy"


def detect_disease(
    image_data: str,
    crop: str,
    image_mime_type: str = "image/jpeg",
) -> DiseaseDetectionResult:
    """Detect disease from uploaded crop image with multilingual reporting."""

    prompt = f"""Analyze this uploaded crop image for {crop} disease detection and provide output in EXACT format:

DISEASE: disease name or healthy
CONFIDENCE: integer 0-100
SEVERITY: one of healthy/mild/moderate/severe
ACTION: one of monitor/treat/urgent treatment
ENGLISH_REPORT:
Farmer-friendly explanation with:
- likely disease summary
- severity understanding
- immediate next steps
GUJARATI_REPORT:
Same report in Gujarati.
HINDI_REPORT:
Same report in Hindi.

Important:
- Do not return JSON.
- Keep advice practical for Indian farm conditions.
"""

    response = generate_vision_response(
        prompt=prompt,
        image_base64=image_data,
        image_mime_type=image_mime_type,
        system_prompt="You are an expert in crop disease identification for Indian farms.",
    )

    disease_raw = _extract_field(response, "DISEASE")
    confidence_raw = _extract_field(response, "CONFIDENCE")
    severity_raw = _extract_field(response, "SEVERITY")
    action_raw = _extract_field(response, "ACTION")

    if not disease_raw or not confidence_raw or not severity_raw or not action_raw:
        raise ValueError("Vision response missing required disease fields.")

    disease_name = _normalize_disease_name(disease_raw)

    confidence_match = re.search(r"\d+", confidence_raw)
    if not confidence_match:
        raise ValueError("Vision response missing confidence score.")
    confidence_val = int(confidence_match.group(0))
    confidence = min(100, max(30, confidence_val)) / 100.0

    severity = _normalize_severity(severity_raw)
    action = action_raw.lower().strip()

    english_report = _extract_block(response, "ENGLISH_REPORT", "GUJARATI_REPORT")
    gujarati_report = _extract_block(response, "GUJARATI_REPORT", "HINDI_REPORT")
    hindi_report = _extract_block(response, "HINDI_REPORT")

    if not english_report or not gujarati_report or not hindi_report:
        raise ValueError("Vision response missing one or more language reports.")

    disease_info = DISEASE_TREATMENT_DB.get(disease_name, DISEASE_TREATMENT_DB["healthy"])

    action_messages = {
        "healthy": "Crop looks healthy. Continue monitoring.",
        "monitor": "Monitor closely for any changes.",
        "treat": "Treatment recommended within 3 to 5 days.",
        "urgent": "Urgent treatment required immediately.",
        "urgent treatment": "Urgent treatment required immediately.",
    }

    detailed_report = (
        f"English:\n{english_report}\n\n"
        f"Gujarati:\n{gujarati_report}\n\n"
        f"Hindi:\n{hindi_report}"
    )

    return DiseaseDetectionResult(
        disease_detected=disease_name.replace("_", " ").title(),
        confidence_score=confidence,
        treatment_suggestions=disease_info["treatment"],
        severity_level=severity,
        action_required=action_messages.get(action, "Monitor and assess crop condition."),
        detailed_report=detailed_report,
        report_en=english_report,
        report_gu=gujarati_report,
        report_hi=hindi_report,
    )


def get_treatment_cost_estimate(disease: str, farm_size_acres: float = 1) -> dict:
    """Estimate treatment cost."""
    treatment_costs = {
        "rust": 1500,
        "leaf_spot": 1800,
        "powdery_mildew": 1200,
        "blight": 2000,
        "wilt": 2500,
        "healthy": 0,
    }

    cost_per_acre = treatment_costs.get(disease.lower().replace(" ", "_"), 1500)
    total_cost = cost_per_acre * farm_size_acres

    return {
        "disease": disease,
        "cost_per_acre": cost_per_acre,
        "farm_size": farm_size_acres,
        "total_estimated_cost": total_cost,
        "materials_needed": [
            "Fungicide/Pesticide",
            "Spraying equipment",
            "Labor for spraying (2-3 days)",
            "Protective equipment",
        ],
        "notes": "Cost varies by local market rates. Consult with agricultural dealer for exact pricing.",
    }


def get_resistant_varieties(crop: str, disease: str) -> list:
    """Suggest disease-resistant crop varieties."""
    resistant_varieties = {
        "wheat": ["PBW 723", "DBW 187", "VL Gehun 51"],
        "rice": ["Samba Hindu", "IR 64", "PR 2062"],
        "cotton": ["H 1098", "Modern Shankar I", "Ankur 651"],
        "maize": ["Kaveri 9", "Syngenta MH 2110", "ICI 8249"],
    }

    return resistant_varieties.get(crop.lower(), ["Consult local agricultural department"])
