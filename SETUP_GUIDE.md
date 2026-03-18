# KISAN SAATHI - Setup & Deployment Guide

## 🚀 Local Development Setup

### Step 1: Clone & Prepare

```bash
# Navigate to your project
cd "Kisan-Saathi"

# Create virtual environment for backend
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

#### Backend
```bash
# From backend directory with venv activated
pip install --upgrade pip
pip install -r requirements.txt
```

#### Frontend
```bash
# From root directory
npm install
```

### Step 3: Configure Environment Variables

```bash
# In backend directory, create .env file
cp .env.example .env

# Edit .env and add your API keys:
# - GROQ_API_KEY (required for chat)
# - OPENWEATHER_API_KEY (optional for real weather)
# - TWILIO_* (optional for WhatsApp)
```

**Get Free API Keys:**
1. **Groq API** (REQUIRED for LLM):
   - Visit: https://console.groq.com
   - Sign up with email
   - Create API key
   - Copy key to GROQ_API_KEY

2. **OpenWeather** (Optional for real weather data):
   - Visit: https://openweathermap.org/api
   - Sign up
   - Get API key
   - Free tier: 60 calls/minute

3. **Twilio** (Optional for WhatsApp):
   - Visit: https://www.twilio.com/try-twilio
   - Get free trial credits
   - Create WhatsApp Sandbox

### Step 4: Run Servers

#### Terminal 1 - Backend
```bash
cd backend
python main.py

# Should show:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

#### Terminal 2 - Frontend
```bash
npm run dev

# Should show:
# ▲ Next.js 16.1.7
# - Local:        http://localhost:3000
```

### Step 5: Test

1. Open http://localhost:3000
2. Try the chatbot: "Tell me about farming in Gujarat"
3. Visit /weather, /market, /soil, /disease pages
4. Test all features

---

## 📱 WhatsApp Setup (Optional)

### Prerequisites
- Twilio account (free trial available)
- Backend running on accessible URL

### Setup Steps

1. **Create Twilio Account**
   - Go to https://www.twilio.com/try-twilio
   - Sign up
   - Verify phone number

2. **Access WhatsApp Sandbox**
   - Go to Twilio Console
   - Navigate to Messaging → WhatsApp Sandbox
   - Note your sandbox number

3. **Message Sandbox to Join**
   - Send from your phone: `join <code>`
   - (Code shown in Twilio Console)

4. **Configure Webhook**
   - In Twilio Console, find WhatsApp Sandbox settings
   - Set Webhook URL:
     ```
     http://yourdomain.com/api/whatsapp/webhook
     ```
   - Method: POST

5. **Test Webhook**
   - Send message from WhatsApp
   - Should receive Kisan Saathi response

---

## 🐳 Docker Deployment

### Docker Setup

```bash
# Build images
docker build -t kisan-saathi-backend ./backend
docker build -t kisan-saathi-frontend .

# Run with docker-compose
docker-compose up
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - OPENWEATHER_API_KEY=${OPENWEATHER_API_KEY}
    volumes:
      - ./backend:/app

  frontend:
    build: .
    ports:
      - "3000:3000"
    depends_on:
      - backend
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## ☁️ Cloud Deployment (Heroku/AWS Example)

### Heroku Deployment

#### Backend
```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create kisan-saathi-api

# Set environment variables
heroku config:set GROQ_API_KEY=your_key

# Deploy from backend directory  
heroku git:remote -a kisan-saathi-api
git push heroku main

# View logs
heroku logs --tail
```

#### Frontend
```bash
# Create Next.js app on Vercel
vercel

# Set environment variables in Vercel dashboard
NEXT_PUBLIC_API_URL=https://kisan-saathi-api.herokuapp.com

# Deploy
vercel --prod
```

### AWS Deployment

#### Backend (EC2)
```bash
# Launch EC2 instance
# Connect via SSH

# Install dependencies
sudo apt update
sudo apt install python3-pip
pip3 install -r requirements.txt

# Run with systemd
sudo nano /etc/systemd/system/kisan-saathi.service
```

#### Frontend (S3 + CloudFront)
```bash
# Build
npm run build

# Deploy to S3
aws s3 sync ./out s3://your-bucket/

# Install CloudFront
aws cloudfront create-distribution --origin-domain-name your-bucket.s3.amazonaws.com
```

---

## 📊 Database Setup (Optional)

### PostgreSQL Setup
```bash
# Install PostgreSQL
# macOS: brew install postgresql
# Ubuntu: sudo apt install postgresql
# Windows: Download from postgresql.org

# Create database
createdb kisan_saathi

# Update .env
DATABASE_URL=postgresql://user:password@localhost:5432/kisan_saathi
```

### Models (if database is added)
```python
# In backend/models/database.py
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Farmer(Base):
    __tablename__ = "farmers"
    id = Column(String, primary_key=True)
    name = Column(String)
    location = Column(String)
    crops = Column(String)  # JSON
    language = Column(String, default='en')
    created_at = Column(DateTime)
```

---

## 🔒 Security Checklist

- [ ] Store all API keys in `.env` (never commit)
- [ ] Use HTTPS in production
- [ ] Enable CORS only for known origins
- [ ] Add rate limiting to API endpoints
- [ ] Validate all user inputs
- [ ] Use environment-specific configs
- [ ] Encrypt sensitive database data
- [ ] Setup error logging (not exposing details)
- [ ] Use strong passwords for accounts
- [ ] Regular security updates

---

## 🧪 Testing

### Backend Tests
```bash
# Create test file: backend/test_api.py
python -m pytest test_api.py -v
```

### Frontend Tests
```bash
# Run linters
npm run lint

# Build for production
npm run build
```

---

## 📈 Performance Optimization

### Backend
```python
# Add caching
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_function():
    return result

# Add rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.get("/api/endpoint")
@limiter.limit("30/minute")
async def endpoint():
    pass
```

### Frontend
```bash
# Enable image optimization
npm install next-image-export-optimizer

# Use dynamic imports for code splitting
dynamic(() => import('../components/Heavy'), { ssr: false })

# Enable gzip compression in next.config.ts
compress: true
```

---

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Check if port is in use
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # macOS/Linux

# Use different port
python main.py --port 8001

# Check Python version
python --version  # Must be 3.8+
```

### CORS Errors
```python
# In main.py, add your frontend URL
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://yourdomain.com"
]
```

### API Key Issues
```bash
# Verify .env is in backend directory
# Check spelling of keys
# Ensure no extra spaces in .env

# Test with simple request
curl http://localhost:8000/

# Should return health status
```

### Database Connection
```bash
# Check PostgreSQL is running
psql -U postgres

# Verify DATABASE_URL in .env
# Format: postgresql://user:password@host:port/dbname
```

---

## 📚 Project Structure

```
Kisan-Saathi/
├── app/                           # Next.js Frontend
│   ├── components/
│   │   ├── Navbar.tsx
│   │   └── common.tsx
│   ├── page.tsx                   # Home/Chat
│   ├── weather/page.tsx
│   ├── soil/page.tsx
│   ├── disease/page.tsx
│   ├── market/page.tsx
│   ├── crops/page.tsx
│   └── globals.css
├── backend/                       # FastAPI Backend
│   ├── main.py
│   ├── models/
│   │   └── schemas.py
│   ├── routes/
│   │   ├── chat.py
│   │   ├── weather.py
│   │   ├── soil.py
│   │   ├── disease.py
│   │   ├── market.py
│   │   ├── crops.py
│   │   └── whatsapp.py
│   ├── services/
│   │   ├── groq_client.py
│   │   ├── weather_service.py
│   │   ├── soil_analyzer.py
│   │   ├── disease_detector.py
│   │   ├── crop_advisor.py
│   │   ├── market_insights.py
│   │   ├── whatsapp_service.py
│   │   ├── translation_service.py
│   │   └── stage*.py
│   ├── requirements.txt
│   └── .env.example
├── package.json
└── README.md
```

---

## 🎯 Next Steps

1. ✅ Setup local environment
2. ✅ Add your API keys
3. ✅ Test all features locally
4. ✅ Deploy to production
5. ✅ Configure WhatsApp
6. ✅ Monitor performance
7. ✅ Gather farmer feedback
8. ✅ Iterate and improve

---

## 📞 Support & Help

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check README.md for API docs
- **Troubleshooting**: See section above
- **Community**: Connect with other developers

---

**Happy Farming! 🚜**
