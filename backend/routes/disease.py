"""Routes for Disease Detection API"""

from fastapi import APIRouter, HTTPException, File, Form, UploadFile
from models.schemas import DiseaseDetectionRequest, DiseaseDetectionResult
from services.disease_detector import detect_disease, get_treatment_cost_estimate, get_resistant_varieties
from services.groq_client import GROQ_VISION_MODEL
import base64

router = APIRouter()

@router.post("/disease/detect", response_model=DiseaseDetectionResult)
async def detect_crop_disease(request: DiseaseDetectionRequest):
    """Detect disease from uploaded crop image."""
    
    try:
        result = detect_disease(request.image_data, request.crop)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Disease detection failed: {str(e)}")

@router.post("/disease/upload")
async def upload_disease_image(
    farmer_id: str = Form(...),
    crop: str = Form(...),
    file: UploadFile = File(...),
):
    """Upload and analyze crop image for diseases."""
    
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
        
        # Detect disease
        result = detect_disease(
            image_data=image_data,
            crop=crop,
            image_mime_type=content_type or "image/jpeg",
        )
        
        return {
            "farmer_id": farmer_id,
            "crop": crop,
            "filename": file.filename,
            "model_used": GROQ_VISION_MODEL,
            "disease_analysis": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File upload failed: {str(e)}")

@router.get("/disease/treatment-cost/{disease}/{farm_size}")
async def get_treatment_cost(disease: str, farm_size: float = 1.0):
    """Get treatment cost estimate."""
    
    try:
        cost = get_treatment_cost_estimate(disease, farm_size)
        return cost
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/disease/resistant-varieties/{crop}/{disease}")
async def get_resistant_crop_varieties(crop: str, disease: str):
    """Get disease-resistant crop varieties."""
    
    try:
        varieties = get_resistant_varieties(crop, disease)
        return {
            "crop": crop,
            "disease": disease,
            "resistant_varieties": varieties
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
