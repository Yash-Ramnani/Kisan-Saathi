import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import chat, whatsapp


# ─── Daily Report Scheduler ──────────────────────────────────────

async def daily_report_scheduler():
    """Fires daily morning reports every day at 7:00 AM IST."""
    while True:
        now = datetime.now()
        target = now.replace(hour=7, minute=0, second=0, microsecond=0)
        if now >= target:
            target += timedelta(days=1)
        wait_seconds = (target - now).total_seconds()
        print(f"⏰ Daily report scheduled in {wait_seconds/3600:.1f} hours (next 7 AM)")
        await asyncio.sleep(wait_seconds)
        try:
            await whatsapp.send_daily_morning_reports()
        except Exception as e:
            print(f"Daily scheduler error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the daily scheduler in background on startup
    scheduler_task = asyncio.create_task(daily_report_scheduler())
    print("🌾 Kisan Saathi started | Daily scheduler active ✅")
    yield
    scheduler_task.cancel()
    print("🛑 Kisan Saathi stopped")


# ─── FastAPI App ──────────────────────────────────────────────────

app = FastAPI(
    title="Kisan Saathi API",
    description=(
        "AI-powered hyper-local farming advisor for Indian farmers.\n"
        "Delivers real-time weather, crop advisory, mandi prices & govt schemes via WhatsApp."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "✅ Kisan Saathi v2.0 is running",
        "features": [
            "AI Crop Advisory", "Real-time Weather", "5-Day Forecast",
            "Mandi Prices", "Crop Calendar", "Govt Schemes",
            "Fertilizer Advisor", "Pest & Disease Help",
            "Farmer Profile Memory", "Daily Morning Reports",
        ],
        "endpoints": {
            "whatsapp_webhook": "/webhook",
            "web_chat_api": "/api/chat",
            "api_docs": "/docs",
        }
    }

# Routes
app.include_router(chat.router, prefix="/api", tags=["Web Chat API"])
app.include_router(whatsapp.router, tags=["WhatsApp Bot"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
