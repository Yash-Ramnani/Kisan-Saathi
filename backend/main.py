from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import chat, soil, weather, crops, disease, market, whatsapp

app = FastAPI(
    title="Kisan Saathi - Smart Farming Intelligence System",
    description="AI-powered agricultural platform for Indian farmers",
    version="1.0.0"
)

# Setup CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint for health check
@app.get("/")
def read_root():
    return {
        "status": "Kisan Saathi API is running",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "soil": "/api/soil",
            "weather": "/api/weather",
            "crops": "/api/crops",
            "disease": "/api/disease",
            "market": "/api/market",
            "whatsapp": "/api/whatsapp"
        }
    }

# Register all routes
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(soil.router, prefix="/api", tags=["Soil Analysis"])
app.include_router(weather.router, prefix="/api", tags=["Weather"])
app.include_router(crops.router, prefix="/api", tags=["Crop Advisory"])
app.include_router(disease.router, prefix="/api", tags=["Disease Detection"])
app.include_router(market.router, prefix="/api", tags=["Market Insights"])
app.include_router(whatsapp.router, prefix="/api", tags=["WhatsApp Integration"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
