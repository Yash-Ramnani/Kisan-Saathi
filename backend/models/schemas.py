from pydantic import BaseModel
from typing import Optional, List

class ChatRequest(BaseModel):
    message: str
    current_location: Optional[str] = None
    known_crops: Optional[List[str]] = None

class ChatResponse(BaseModel):
    reply: str
    location: Optional[str] = None
    weather_summary: Optional[str] = None
    risk_scores: Optional[dict] = None
    decisions: Optional[List[str]] = None
    action_plan: Optional[List[str]] = None
    reason: Optional[str] = None
    original_message: str
    detected_crop: Optional[str] = None

# Internal Models
class NormalizedInput(BaseModel):
    crop: str
    action: str
    location: str
    intent: str
    time_horizon: str = "today"
    is_valid_agri_query: bool

class ClimateData(BaseModel):
    location: str
    temperature: float
    rainfall: float
    humidity: float
    wind_speed: float
    weather_condition: str

class RiskScores(BaseModel):
    disease_risk: int # 0-100
    irrigation_need: int # 0-100
    spray_effectiveness: int # 0-100

class DecisionData(BaseModel):
    decisions: List[str]
    action_plan: List[str]
    reason: str
