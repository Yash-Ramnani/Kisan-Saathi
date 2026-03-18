from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Chat Models
class ChatRequest(BaseModel):
    message: str
    language: str = "en"  # en or gu
    farmer_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    location: Optional[str] = None
    weather_summary: Optional[str] = None
    risk_scores: Optional[dict] = None
    decisions: Optional[List[str]] = None
    action_plan: Optional[List[str]] = None
    reason: Optional[str] = None
    original_message: str

# Soil Analysis Models
class SoilAnalysisRequest(BaseModel):
    farmer_id: str
    location: str
    image_data: str  # Base64 encoded image

class SoilAnalysisResult(BaseModel):
    soil_type: str
    fertility_level: str
    moisture_condition: str
    ph_level: Optional[float] = None
    recommended_crops: List[str]
    fertilizer_suggestions: List[str]
    detailed_report: str
    report_en: Optional[str] = None
    report_gu: Optional[str] = None
    report_hi: Optional[str] = None
    confidence_score: float

# Crop Advisory Models
class CropAdvisoryRequest(BaseModel):
    crop: str
    location: str
    soil_type: str
    weather_data: Optional[dict] = None

class CropAdvisoryResponse(BaseModel):
    crop: str
    growth_stage: str
    irrigation_plan: List[str]
    fertilizer_plan: List[str]
    pest_risks: List[str]
    disease_risks: List[str]
    next_actions: List[str]

# Disease Detection Models
class DiseaseDetectionRequest(BaseModel):
    farmer_id: str
    crop: str
    image_data: str  # Base64 encoded

class DiseaseDetectionResult(BaseModel):
    disease_detected: str
    confidence_score: float
    treatment_suggestions: List[str]
    severity_level: str
    action_required: str
    detailed_report: Optional[str] = None
    report_en: Optional[str] = None
    report_gu: Optional[str] = None
    report_hi: Optional[str] = None

# Market Insights Models
class MarketInsightResponse(BaseModel):
    crop: str
    current_price: float
    week_ago_price: float
    trend: str  # up, down, stable
    nearby_prices: dict
    best_mandi: str
    recommendation: str

# Farmer Profile
class FarmerProfile(BaseModel):
    farmer_id: str
    name: str
    location: str
    region: str
    crops: List[str]
    farm_size: float  # in acres
    language_preference: str  # en or gu
    phone: Optional[str] = None

# Internal Models
class NormalizedInput(BaseModel):
    crop: str
    action: str
    location: str
    intent: str
    is_valid_agri_query: bool

class ClimateData(BaseModel):
    location: str
    temperature: float
    rainfall: float
    humidity: float
    wind_speed: float
    weather_condition: str
    feels_like: float
    visibility: float
    uv_index: Optional[float] = None

class RiskScores(BaseModel):
    disease_risk: int  # 0-100
    irrigation_need: int  # 0-100
    spray_effectiveness: int  # 0-100
    frost_risk: int = 0
    pest_risk: int = 0

class DecisionData(BaseModel):
    decisions: List[str]
    action_plan: List[str]
    reason: str

# Notification Models
class NotificationMessage(BaseModel):
    farmer_id: str
    type: str  # weather, pest, disease, irrigation, market
    title: str
    message: str
    priority: str  # low, medium, high
    created_at: datetime = datetime.now()
    read: bool = False

# WhatsApp Integration Models
class WhatsAppMessage(BaseModel):
    from_number: str
    message_text: str
    timestamp: datetime
    media_url: Optional[str] = None
