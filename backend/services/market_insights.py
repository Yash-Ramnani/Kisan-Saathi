"""
Market Insights Service - Provides mandi prices and market recommendations
"""

import random
from datetime import datetime, timedelta
from models.schemas import MarketInsightResponse

# Mock mandi price database (in production, integrate with real mandi APIs)
MANDI_PRICES = {
    "aravali_mandi": {"name": "Aravoli Mandi (Gujarat)", "location": "Surat"},
    "chandni_chowk": {"name": "Chandni Chowk (Delhi)", "location": "Delhi"},
    "apmc_mandi": {"name": "APMC Mandi (Maharashtra)", "location": "Pune"},
    "london_warehouse": {"name": "LONDON Warehouse (Karnataka)", "location": "Bangalore"}
}

CROP_PRICES = {
    "wheat": {"avg": 2400, "variance": 200},
    "rice": {"avg": 3500, "variance": 300},
    "cotton": {"avg": 8500, "variance": 800},
    "maize": {"avg": 2100, "variance": 200},
    "groundnut": {"avg": 7500, "variance": 600},
    "soybean": {"avg": 5500, "variance": 400}
}

def get_market_insights(crop: str) -> MarketInsightResponse:
    """Get current market insights for a crop."""
    
    crop_lower = crop.lower()
    price_data = CROP_PRICES.get(crop_lower, {"avg": 5000, "variance": 500})
    
    # Generate realistic price variation
    current_price = price_data["avg"] + random.randint(-price_data["variance"], price_data["variance"])
    week_ago_price = price_data["avg"] + random.randint(-price_data["variance"], price_data["variance"])
    
    # Calculate trend
    price_change = current_price - week_ago_price
    if price_change > 100:
        trend = "up"
        trend_emoji = "📈"
    elif price_change < -100:
        trend = "down"
        trend_emoji = "📉"
    else:
        trend = "stable"
        trend_emoji = "➡️"
    
    # Get nearby mandi prices
    nearby_mandis = {}
    for mandi_key, mandi_info in list(MANDI_PRICES.items())[:3]:
        mandi_price = current_price + random.randint(-500, 500)
        nearby_mandis[mandi_info["name"]] = mandi_price
    
    # Find best mandi
    best_mandi = max(nearby_mandis.items(), key=lambda x: x[1])
    
    # Generate recommendation
    if trend == "up":
        recommendation = f"{trend_emoji} Prices trending UP! Consider holding for 3-5 more days for better returns."
    elif trend == "down":
        recommendation = f"{trend_emoji} Prices trending DOWN! Sell within 2-3 days to avoid further losses."
    else:
        recommendation = f"{trend_emoji} Prices STABLE. Sell at {best_mandi[0]} for best rates."
    
    return MarketInsightResponse(
        crop=crop,
        current_price=current_price,
        week_ago_price=week_ago_price,
        trend=trend,
        nearby_prices=nearby_mandis,
        best_mandi=best_mandi[0],
        recommendation=recommendation
    )

def get_price_history(crop: str, days: int = 30) -> dict:
    """Get historical price data for a crop."""
    
    crop_lower = crop.lower()
    price_data = CROP_PRICES.get(crop_lower, {"avg": 5000, "variance": 500})
    
    history = {
        "crop": crop,
        "dates": [],
        "prices": []
    }
    
    base_price = price_data["avg"]
    for i in range(days, 0, -1):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        price = base_price + random.randint(-price_data["variance"]*2, price_data["variance"]*2)
        
        history["dates"].append(date)
        history["prices"].append(price)
    
    return history

def get_seasonal_advice(crop: str, current_month: int = None) -> dict:
    """Get seasonal selling advice."""
    
    if current_month is None:
        current_month = datetime.now().month
    
    # Harvest months for different crops
    harvest_months = {
        "wheat": [3, 4, 5],      # Mar-May
        "rice": [10, 11, 12],    # Oct-Dec
        "cotton": [11, 12, 1],   # Nov-Jan
        "maize": [9, 10, 11],    # Sep-Nov
        "groundnut": [8, 9],     # Aug-Sep
        "soybean": [10, 11]      # Oct-Nov
    }
    
    crop_lower = crop.lower()
    harvest = harvest_months.get(crop_lower, [])
    
    if current_month in harvest:
        status = "HARVEST SEASON"
        advice = "🌾 This is peak harvest season. Prices may be lower due to supply surplus. Consider storage if possible."
        action = "Harvest and prepare for market"
    elif current_month in [(m + 1) % 12 or 12 for m in harvest]:
        status = "POST-HARVEST"
        advice = "📦 Prices may rise as market supply decreases. Consider storage for 2-3 months for better returns."
        action = "Store in proper conditions"
    else:
        status = "OFF-SEASON"
        advice = "💰 Off-season pricing is premium. If you have stored produce, this is the best time to sell."
        action = "Sell at market if you have stock"
    
    return {
        "crop": crop,
        "current_status": status,
        "advice": advice,
        "recommended_action": action,
        "estimated_peak_price_month": harvest[0] + 2 if harvest else "unknown"  # Typically 2 months after harvest
    }

def compare_mandis(crop: str, manifesto: str = None) -> dict:
    """Compare prices across multiple mandis."""
    
    prices_by_mandi = {}
    for mandi_key, mandi_info in MANDI_PRICES.items():
        base_price = CROP_PRICES.get(crop.lower(), {"avg": 5000, "variance": 500})
        price = base_price["avg"] + random.randint(-base_price["variance"], base_price["variance"])
        prices_by_mandi[mandi_info["name"]] = {
            "price": price,
            "location": mandi_info["location"]
        }
    
    # Sort by price
    sorted_mandis = sorted(prices_by_mandi.items(), key=lambda x: x[1]["price"], reverse=True)
    
    return {
        "crop": crop,
        "mandis": dict(sorted_mandis),
        "best_mandi": sorted_mandis[0][0],
        "best_price": sorted_mandis[0][1]["price"],
        "worst_mandi": sorted_mandis[-1][0],
        "worst_price": sorted_mandis[-1][1]["price"],
        "price_difference": sorted_mandis[0][1]["price"] - sorted_mandis[-1][1]["price"]
    }

def get_price_forecast(crop: str, days_ahead: int = 7) -> dict:
    """Generate simple price forecast for next few days."""
    
    price_data = CROP_PRICES.get(crop.lower(), {"avg": 5000, "variance": 500})
    current_price = price_data["avg"]
    
    forecast = {
        "crop": crop,
        "days": [],
        "predicted_prices": [],
        "confidence": "Low (requires real data for accuracy)"
    }
    
    for day in range(1, days_ahead + 1):
        date = (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d")
        # Simple trend: slight random walk
        predicted_price = current_price + random.randint(-300, 300)
        current_price = predicted_price
        
        forecast["days"].append(date)
        forecast["predicted_prices"].append(predicted_price)
    
    forecast["recommendation"] = "Monitor actual market prices for accurate decision-making"
    
    return forecast
