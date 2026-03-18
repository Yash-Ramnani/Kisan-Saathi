"""Routes for Crop Advisory API"""

from fastapi import APIRouter, HTTPException
from models.schemas import CropAdvisoryResponse, ClimateData
from services.crop_advisor import get_crop_advice, suggest_companion_crops, get_disease_management
from services.weather_service import fetch_weather

router = APIRouter()

@router.get("/crops/advisory/{crop}/{location}/{soil_type}", response_model=CropAdvisoryResponse)
async def get_crop_advisory(crop: str, location: str, soil_type: str):
    """Get crop advisory for specific conditions."""
    
    try:
        climate = fetch_weather(location)
        advice = get_crop_advice(crop, location, soil_type, climate)
        return advice
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/crops/companions/{crop}")
async def get_companion_crops(crop: str):
    """Get companion crops for intercropping."""
    
    try:
        companions = suggest_companion_crops(crop)
        return {
            "main_crop": crop,
            "companion_crops": companions
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/crops/disease-management/{crop}/{disease}")
async def get_disease_management_plan(crop: str, disease: str):
    """Get disease management strategy."""
    
    try:
        management = get_disease_management(crop, disease)
        return management
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
