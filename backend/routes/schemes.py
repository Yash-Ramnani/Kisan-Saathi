"""Routes for Government Farmer Schemes API"""

from fastapi import APIRouter, HTTPException
from services.scheme_fetcher import fetch_live_farmer_schemes

router = APIRouter()


@router.get("/schemes/current")
async def get_current_farmer_schemes(refresh: bool = False):
    """Get currently discoverable farmer schemes from government websites."""
    try:
        return fetch_live_farmer_schemes(force_refresh=refresh)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not fetch schemes: {exc}")
