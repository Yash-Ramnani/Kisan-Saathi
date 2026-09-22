# Kisan Saathi

Kisan Saathi is an AI-powered farming assistant for Indian farmers. It combines a Next.js frontend with a FastAPI backend to help with crop advice, weather, soil analysis, disease detection, market pricing, government schemes, and WhatsApp-based assistance.

The app is designed to work in demo mode even when some external API keys are missing, so the core experience remains usable during development.

## What This Project Can Do

- Chat with a farming-focused AI assistant in English or Gujarati.
- Get weather, forecast, irrigation, and spraying advice for a location.
- Upload soil images and receive a structured soil report with crop suggestions.
- Upload crop images and detect likely disease, severity, and treatment steps.
- Check crop-specific advisory based on crop, location, and soil type.
- View mandi-style market insights, price trends, and selling recommendations.
- Browse live government scheme links fetched from official sources.
- Use WhatsApp-style farmer messaging and alerts through Twilio integration.
- Switch between a dashboard overview and dedicated analysis pages for each module.

## Main Features

### AI Chat Dashboard
- Farm-focused conversational assistant
- Supports English and Gujarati input/output
- Returns structured advice blocks when available
- Includes quick prompts and direct links to key modules

### Weather and Climate Intelligence
- Current weather by location
- 5-day forecast
- Irrigation recommendations
- Spraying suitability guidance based on wind, humidity, and rainfall

### Soil Analysis
- Upload a soil photo for analysis
- Detect soil type, fertility, moisture, and pH estimate
- Suggest suitable crops and fertilizer actions
- Shows multilingual report output in English, Gujarati, and Hindi

### Crop Advisory
- Crop, soil type, and location-based recommendations
- Irrigation and fertilizer schedules
- Pest and disease risk lists
- Immediate action plan and companion crop suggestions

### Disease Detection
- Upload crop images for disease diagnosis
- Confidence score and severity level
- Treatment suggestions and prevention guidance
- Multilingual reports for farmer-friendly understanding

### Market Insights
- Crop price overview
- Week-on-week trend signals
- Nearby mandi price comparison
- Best mandi and selling-time recommendation

### Government Schemes
- Live scheme discovery from government websites
- Refreshable scheme list
- Direct external links to official sources

### WhatsApp Integration
- Twilio WhatsApp webhook support
- Farmer profile tracking
- Language preference updates
- Alert delivery for weather, pest, disease, irrigation, and market events

## Tech Stack

- Frontend: Next.js 16, React 19, TypeScript, Tailwind CSS
- UI: Lucide icons, chart libraries, toast support
- Backend: FastAPI, Pydantic, Uvicorn
- AI: Groq LLM and Groq vision model integration
- External services: Weather API, OpenWeather fallback, Twilio WhatsApp

## Project Structure

```text
Kisan-Saathi/
├── app/                     # Next.js app router pages and shared UI
│   ├── page.tsx             # Main AI chat dashboard
│   ├── dashboard/page.tsx   # Module overview dashboard
│   ├── weather/page.tsx     # Weather and climate insights
│   ├── soil/page.tsx        # Soil image analysis
│   ├── crops/page.tsx       # Crop advisory
│   ├── disease/page.tsx     # Disease detection
│   ├── market/page.tsx      # Market insights
│   ├── schemes/page.tsx     # Government schemes
│   └── components/          # Navbar and reusable cards/alerts
├── backend/                 # FastAPI application
│   ├── main.py              # API entry point
│   ├── routes/              # Chat, weather, soil, crops, disease, market, schemes, WhatsApp
│   ├── services/            # AI, weather, soil, disease, market, translation, WhatsApp logic
│   └── models/              # Pydantic schemas
├── public/                  # Sample images and static assets
└── README.md                # Project documentation
```

## API Modules

- `POST /api/chat`
- `GET /api/weather/{location}`
- `GET /api/weather/forecast/{location}`
- `GET /api/weather/irrigation-advice/{location}`
- `GET /api/weather/spray-recommendations/{location}`
- `POST /api/soil/analyze`
- `POST /api/soil/upload`
- `GET /api/crops/advisory/{crop}/{location}/{soil_type}`
- `GET /api/crops/companions/{crop}`
- `GET /api/crops/disease-management/{crop}/{disease}`
- `POST /api/disease/detect`
- `POST /api/disease/upload`
- `GET /api/market/insights/{crop}`
- `GET /api/market/price-history/{crop}/{days}`
- `GET /api/market/seasonal-advice/{crop}`
- `GET /api/market/compare-mandis/{crop}`
- `GET /api/market/price-forecast/{crop}/{days}`
- `GET /api/schemes/current`
- `POST /api/whatsapp/webhook`
- `POST /api/whatsapp/send-alert/{farmer_phone}`
- `GET /api/whatsapp/farmer-profile/{farmer_phone}`
- `PUT /api/whatsapp/farmer-language/{farmer_phone}/{language}`

## Prerequisites

- Node.js 18+
- Python 3.10+
- npm

Optional API keys:

- `GROQ_API_KEY` for AI chat and vision analysis
- `WEATHERAPI_API_KEY` or `OPENWEATHER_API_KEY` for real weather data
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_NUMBER` for WhatsApp delivery

## Local Setup

### 1. Install Backend Dependencies

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file inside `backend/` and add the keys you want to use.

```env
GROQ_API_KEY=your_groq_key
WEATHERAPI_API_KEY=your_weatherapi_key
OPENWEATHER_API_KEY=your_openweather_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

### 3. Start the Backend

```bash
cd backend
python main.py
```

The API runs on `http://localhost:8000` and the OpenAPI docs are available at `http://localhost:8000/docs`.

### 4. Install Frontend Dependencies

```bash
npm install
```

### 5. Start the Frontend

```bash
npm run dev
```

Open `http://localhost:3000` in your browser.

## Useful Commands

```bash
npm run dev
npm run build
npm run start
npm run lint
```

## Notes

- The backend includes mock fallbacks for several services, so the app can still demonstrate core flows without every external key.
- Soil and disease image uploads are limited to common image formats and an 8 MB max size.
- The chat assistant routes some requests through a structured decision pipeline and others through Groq-generated responses.

## License

No license file is currently included in this repository.