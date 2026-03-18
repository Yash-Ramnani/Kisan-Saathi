"""Routes for Soil Analysis API"""

from fastapi import APIRouter, HTTPException, File, Form, UploadFile
from models.schemas import SoilAnalysisRequest, SoilAnalysisResult
from services.soil_analyzer import analyze_soil_image, get_soil_improvement_plan
import base64

router = APIRouter()

@router.post("/soil/analyze", response_model=SoilAnalysisResult)
async def analyze_soil(request: SoilAnalysisRequest):
    """Analyze soil from uploaded image."""
    
    try:
        result = analyze_soil_image(request.image_data, request.location)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Soil analysis failed: {str(e)}")

@router.post("/soil/upload")
async def upload_soil_image(
    farmer_id: str = Form(...),
    location: str = Form(...),
    file: UploadFile = File(...),
):
    """Upload and analyze soil image."""
    
    try:
        # Read file
        contents = await file.read()
        
        # Convert to base64
        image_data = base64.b64encode(contents).decode('utf-8')
        
        # Analyze
        result = analyze_soil_image(
            image_data=image_data,
            location=location,
            image_mime_type=file.content_type or "image/jpeg",
        )
        
        return {
            "farmer_id": farmer_id,
            "location": location,
            "filename": file.filename,
            "analysis": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File upload failed: {str(e)}")

@router.get("/soil/improvement-plan/{soil_type}/{fertility_level}")
async def get_improvement_plan(soil_type: str, fertility_level: str):
    """Get soil improvement recommendations."""
    
    try:
        plan = get_soil_improvement_plan(soil_type, fertility_level)
        return {
            "soil_type": soil_type,
            "fertility_level": fertility_level,
            "improvement_plan": plan
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
