"""Routes for Market Insights API"""

from fastapi import APIRouter, HTTPException
from models.schemas import MarketInsightResponse
from services.market_insights import get_market_insights, get_price_history, get_seasonal_advice, compare_mandis, get_price_forecast

router = APIRouter()

@router.get("/market/insights/{crop}", response_model=MarketInsightResponse)
async def get_market_insight(crop: str):
    """Get current market insights for a crop."""
    
    try:
        insights = get_market_insights(crop)
        return insights
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/market/price-history/{crop}/{days}")
async def get_price_trend(crop: str, days: int = 30):
    """Get historical price data for a crop."""
    
    try:
        if days < 7 or days > 365:
            raise ValueError("Days must be between 7 and 365")
        
        history = get_price_history(crop, days)
        return history
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/market/seasonal-advice/{crop}")
async def get_seasonal_pricing_advice(crop: str):
    """Get seasonal advice for selling."""
    
    try:
        advice = get_seasonal_advice(crop)
        return advice
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/market/compare-mandis/{crop}")
async def compare_mandi_prices(crop: str):
    """Compare prices across multiple mandis."""
    
    try:
        comparison = compare_mandis(crop)
        return comparison
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/market/price-forecast/{crop}/{days}")
async def get_price_prediction(crop: str, days: int = 7):
    """Get simple price forecast for next few days."""
    
    try:
        if days < 1 or days > 30:
            raise ValueError("Days must be between 1 and 30")
        
        forecast = get_price_forecast(crop, days)
        return forecast
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
