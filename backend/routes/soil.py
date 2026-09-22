"""Routes for Soil Analysis API"""

from fastapi import APIRouter, HTTPException, File, Form, UploadFile
from models.schemas import SoilAnalysisRequest, SoilAnalysisResult
from services.soil_analyzer import analyze_soil_image, get_soil_improvement_plan
from services.groq_client import GROQ_VISION_MODEL
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
        content_type = (file.content_type or "").lower()
        allowed_types = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
        if content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use JPG, PNG, or WEBP.")

        # Read file
        contents = await file.read()
        max_size_bytes = 8 * 1024 * 1024
        if len(contents) > max_size_bytes:
            raise HTTPException(status_code=400, detail="Image too large. Max allowed size is 8 MB.")

        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        
        # Convert to base64
        image_data = base64.b64encode(contents).decode('utf-8')
        
        # Analyze
        result = analyze_soil_image(
            image_data=image_data,
            location=location,
            image_mime_type=content_type or "image/jpeg",
        )
        
        return {
            "farmer_id": farmer_id,
            "location": location,
            "filename": file.filename,
            "model_used": GROQ_VISION_MODEL,
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
