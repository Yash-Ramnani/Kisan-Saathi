from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# --- Request / Response Models ---

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    current_location: Optional[str] = None
    known_crops: Optional[List[str]] = None

class ChatResponse(BaseModel):
    reply: str
    location: Optional[str] = None
    weather_summary: Optional[str] = None
    forecast: Optional[List[Dict[str, Any]]] = None
    risk_scores: Optional[dict] = None
    decisions: Optional[List[str]] = None
    action_plan: Optional[List[str]] = None
    reason: Optional[str] = None
    original_message: str
    detected_crop: Optional[str] = None
    season: Optional[str] = None

# --- Internal Pipeline Models ---

class NormalizedInput(BaseModel):
    crop: str
    action: str
    location: str
    intent: str
    time_horizon: str = "today"
    is_valid_agri_query: bool
    pest_concern: Optional[str] = None   # e.g. "aphid", "bollworm"
    disease_concern: Optional[str] = None # e.g. "blight", "rust"

class ClimateData(BaseModel):
    location: str
    temperature: float
    feels_like: float = 0.0
    rainfall: float
    humidity: float
    wind_speed: float
    weather_condition: str
    uv_index: float = 0.0
    visibility: float = 10.0
    forecast: Optional[List[Dict[str, Any]]] = None   # 5-day forecast list

class RiskScores(BaseModel):
    disease_risk: int           # 0-100
    irrigation_need: int        # 0-100
    spray_effectiveness: int    # 0-100
    heat_stress: int            # 0-100
    frost_risk: int             # 0-100
    overall_alert: str          # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"

class DecisionData(BaseModel):
    decisions: List[str]
    action_plan: List[str]
    reason: str
