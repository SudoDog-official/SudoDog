#!/bin/bash
# FIXED SudoDog Platform Setup Script - Version 2
set -e

echo "🐕 Creating SudoDog Platform..."

# Choose location
read -p "Create in which directory? (press Enter for ~/projects): " DIR
DIR=${DIR:-~/projects}
mkdir -p "$DIR"
cd "$DIR"

# Remove if exists
if [ -d "sudodog-platform" ]; then
    echo "Removing existing sudodog-platform directory..."
    rm -rf sudodog-platform
fi

# Create root directory and navigate into it
mkdir sudodog-platform
cd sudodog-platform

# Store the root path
ROOT_DIR=$(pwd)
echo "Working in: $ROOT_DIR"

echo "Creating directory structure..."

# Create ALL directories with explicit full paths
mkdir -p "$ROOT_DIR/backend/api/routes"
mkdir -p "$ROOT_DIR/backend/database"
mkdir -p "$ROOT_DIR/backend/ml"
mkdir -p "$ROOT_DIR/backend/workers"
mkdir -p "$ROOT_DIR/frontend/dashboard/src/pages"
mkdir -p "$ROOT_DIR/infrastructure"

# Verify critical directories exist
if [ ! -d "$ROOT_DIR/backend/workers" ]; then
    echo "ERROR: Failed to create backend/workers directory"
    exit 1
fi

echo "✓ All directories created successfully"
echo "Now creating files..."

# Create .gitignore
cat > "$ROOT_DIR/.gitignore" << 'ENDFILE'
__pycache__/
*.py[cod]
venv/
env/
.env
node_modules/
dist/
*.pkl
*.joblib
.DS_Store
.venv
.env.local
ENDFILE

# Create README
cat > "$ROOT_DIR/README.md" << 'ENDFILE'
# SudoDog Platform - Private Repository

**⚠️ PRIVATE - Proprietary Code**

Backend API, ML pipeline, and Web dashboard for SudoDog paid tier.

## Quick Start
```bash
./quick-start.sh
```

See START_HERE.md for complete documentation.
ENDFILE

# Backend requirements.txt
cat > "$ROOT_DIR/backend/requirements.txt" << 'ENDFILE'
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
celery==5.3.4
redis==5.0.1
scikit-learn==1.3.2
pandas==2.1.3
numpy==1.26.2
joblib==1.3.2
python-dotenv==1.0.0
pytest==7.4.3
ENDFILE

# Backend __init__.py
cat > "$ROOT_DIR/backend/__init__.py" << 'ENDFILE'
"""SudoDog Platform Backend"""
__version__ = "1.0.0"
ENDFILE

# API __init__.py
cat > "$ROOT_DIR/backend/api/__init__.py" << 'ENDFILE'
"""FastAPI Application"""
ENDFILE

# API config
cat > "$ROOT_DIR/backend/api/config.py" << 'ENDFILE'
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://sudodog:password@localhost:5432/sudodog_platform"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "your-secret-key-change-this"
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "http://localhost:5173"
    
    class Config:
        env_file = ".env"

def get_settings():
    return Settings()
ENDFILE

# API main
cat > "$ROOT_DIR/backend/api/main.py" << 'ENDFILE'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.config import get_settings

settings = get_settings()

app = FastAPI(
    title="SudoDog Platform API",
    description="Proprietary API for paid tier features",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "SudoDog Platform API", "version": "1.0.0"}
ENDFILE

# API routes __init__
cat > "$ROOT_DIR/backend/api/routes/__init__.py" << 'ENDFILE'
"""API Routes"""
ENDFILE

# Telemetry route
cat > "$ROOT_DIR/backend/api/routes/telemetry.py" << 'ENDFILE'
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class TelemetryEvent(BaseModel):
    user_id: str
    event_type: str
    timestamp: datetime
    data: dict

class TelemetryResponse(BaseModel):
    status: str
    message: str

@router.post("/", response_model=TelemetryResponse, status_code=202)
async def receive_telemetry(event: TelemetryEvent, background_tasks: BackgroundTasks):
    """Receive telemetry from free tier CLI"""
    print(f"Received telemetry: {event.event_type} from {event.user_id}")
    return TelemetryResponse(status="accepted", message="Telemetry received")
ENDFILE

# Auth route
cat > "$ROOT_DIR/backend/api/routes/auth.py" << 'ENDFILE'
from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
async def login():
    return {"message": "Login endpoint - TODO"}

@router.post("/register")
async def register():
    return {"message": "Register endpoint - TODO"}
ENDFILE

# Agents route
cat > "$ROOT_DIR/backend/api/routes/agents.py" << 'ENDFILE'
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_agents():
    return {"agents": []}

@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    return {"agent_id": agent_id, "status": "active"}
ENDFILE

# Analytics route
cat > "$ROOT_DIR/backend/api/routes/analytics.py" << 'ENDFILE'
from fastapi import APIRouter

router = APIRouter()

@router.get("/anomalies")
async def get_anomalies():
    return {"anomalies": []}

@router.get("/insights")
async def get_insights():
    return {"insights": []}
ENDFILE

# Database __init__
cat > "$ROOT_DIR/backend/database/__init__.py" << 'ENDFILE'
"""Database Models"""
ENDFILE

# Database models
cat > "$ROOT_DIR/backend/database/models.py" << 'ENDFILE'
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    tier = Column(String, default="pro")
    created_at = Column(DateTime, server_default=func.now())

class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    status = Column(String, default="active")
    created_at = Column(DateTime, server_default=func.now())

class TelemetryEvent(Base):
    __tablename__ = "telemetry_events"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    event_type = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    data = Column(JSON)

class Anomaly(Base):
    __tablename__ = "anomalies"
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    detected_at = Column(DateTime, server_default=func.now())
    anomaly_score = Column(Float)
    description = Column(String)
    data = Column(JSON)
ENDFILE

# ML __init__
cat > "$ROOT_DIR/backend/ml/__init__.py" << 'ENDFILE'
"""Machine Learning Pipeline - THE MOAT"""
ENDFILE

# ML anomaly detection
cat > "$ROOT_DIR/backend/ml/anomaly_detection.py" << 'ENDFILE'
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib

class AnomalyDetector:
    """ML-based anomaly detection - THE COMPETITIVE MOAT"""
    
    def __init__(self):
        self.model = None
    
    def train(self, training_data: pd.DataFrame):
        """Train on community telemetry data"""
        features = training_data[['cpu_usage', 'memory_usage', 'api_calls', 'duration']]
        
        self.model = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.model.fit(features)
        return self
    
    def predict(self, agent_data: pd.DataFrame) -> tuple:
        """Detect anomalies"""
        if self.model is None:
            raise ValueError("Model not trained")
        
        features = agent_data[['cpu_usage', 'memory_usage', 'api_calls', 'duration']]
        predictions = self.model.predict(features)
        scores = self.model.score_samples(features)
        
        return predictions, scores
    
    def save_model(self, path: str):
        joblib.dump(self.model, path)
    
    def load_model(self, path: str):
        self.model = joblib.load(path)
        return self
ENDFILE

# Workers __init__ - THIS IS THE FILE THAT WAS FAILING
cat > "$ROOT_DIR/backend/workers/__init__.py" << 'ENDFILE'
"""Celery Workers for Background Processing"""
ENDFILE

# Celery app
cat > "$ROOT_DIR/backend/workers/celery_app.py" << 'ENDFILE'
from celery import Celery

celery_app = Celery(
    "sudodog_workers",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

@celery_app.task(name="tasks.process_telemetry")
def process_telemetry_task(event_data: dict):
    """Process telemetry events"""
    print(f"Processing: {event_data}")
    return {"status": "processed"}

@celery_app.task(name="tasks.train_ml_model")
def train_ml_model_task():
    """Train ML models"""
    print("Training ML model...")
    return {"status": "trained"}
ENDFILE

# Frontend package.json
cat > "$ROOT_DIR/frontend/dashboard/package.json" << 'ENDFILE'
{
  "name": "sudodog-dashboard",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "@tanstack/react-query": "^5.8.0",
    "recharts": "^2.10.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.2.2",
    "vite": "^5.0.0",
    "tailwindcss": "^3.3.5",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.31"
  }
}
ENDFILE

# Vite config
cat > "$ROOT_DIR/frontend/dashboard/vite.config.ts" << 'ENDFILE'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173
  },
})
ENDFILE

# TypeScript config
cat > "$ROOT_DIR/frontend/dashboard/tsconfig.json" << 'ENDFILE'
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM"],
    "module": "ESNext",
    "jsx": "react-jsx",
    "strict": true,
    "moduleResolution": "bundler",
    "skipLibCheck": true
  },
  "include": ["src"]
}
ENDFILE

# HTML
cat > "$ROOT_DIR/frontend/dashboard/index.html" << 'ENDFILE'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>SudoDog Platform Dashboard</title>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.tsx"></script>
</body>
</html>
ENDFILE

# React main
cat > "$ROOT_DIR/frontend/dashboard/src/main.tsx" << 'ENDFILE'
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
ENDFILE

# CSS
cat > "$ROOT_DIR/frontend/dashboard/src/index.css" << 'ENDFILE'
@tailwind base;
@tailwind components;
@tailwind utilities;
ENDFILE

# React App
cat > "$ROOT_DIR/frontend/dashboard/src/App.tsx" << 'ENDFILE'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import AgentsView from './pages/AgentsView'
import AnalyticsView from './pages/AnalyticsView'
import LoginView from './pages/LoginView'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/agents" element={<AgentsView />} />
        <Route path="/analytics" element={<AnalyticsView />} />
        <Route path="/login" element={<LoginView />} />
      </Routes>
    </BrowserRouter>
  )
}
ENDFILE

# Dashboard page
cat > "$ROOT_DIR/frontend/dashboard/src/pages/Dashboard.tsx" << 'ENDFILE'
export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-3xl font-bold mb-4">🐕 SudoDog Platform</h1>
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white p-6 rounded shadow">
          <h3 className="text-gray-500">Active Agents</h3>
          <p className="text-4xl font-bold">0</p>
        </div>
        <div className="bg-white p-6 rounded shadow">
          <h3 className="text-gray-500">Anomalies Detected</h3>
          <p className="text-4xl font-bold">0</p>
        </div>
        <div className="bg-white p-6 rounded shadow">
          <h3 className="text-gray-500">Events Today</h3>
          <p className="text-4xl font-bold">0</p>
        </div>
      </div>
    </div>
  )
}
ENDFILE

# Other pages
cat > "$ROOT_DIR/frontend/dashboard/src/pages/AgentsView.tsx" << 'ENDFILE'
export default function AgentsView() {
  return <div className="p-8"><h1 className="text-2xl">Agents</h1></div>
}
ENDFILE

cat > "$ROOT_DIR/frontend/dashboard/src/pages/AnalyticsView.tsx" << 'ENDFILE'
export default function AnalyticsView() {
  return <div className="p-8"><h1 className="text-2xl">Analytics</h1></div>
}
ENDFILE

cat > "$ROOT_DIR/frontend/dashboard/src/pages/LoginView.tsx" << 'ENDFILE'
export default function LoginView() {
  return <div className="p-8"><h1 className="text-2xl">Login</h1></div>
}
ENDFILE

# Docker compose
cat > "$ROOT_DIR/infrastructure/docker-compose.yml" << 'ENDFILE'
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: sudodog
      POSTGRES_PASSWORD: password
      POSTGRES_DB: sudodog_platform
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  postgres_data:
ENDFILE

# Dockerfile
cat > "$ROOT_DIR/infrastructure/Dockerfile.backend" << 'ENDFILE'
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ ./backend/
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
ENDFILE

# .env.example
cat > "$ROOT_DIR/infrastructure/.env.example" << 'ENDFILE'
DATABASE_URL=postgresql://sudodog:password@localhost:5432/sudodog_platform
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=change-this-to-a-random-secret-key
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:5173
ENDFILE

# START_HERE.md
cat > "$ROOT_DIR/START_HERE.md" << 'ENDFILE'
# 🐕 SudoDog Platform - Private Repository

## What's This?

Your proprietary paid tier features:
- Backend API (FastAPI) - Receives telemetry from free CLI
- ML Pipeline (scikit-learn) - THE MOAT
- Web Dashboard (React) - Monitor all agents

## Quick Start
```bash
./quick-start.sh
```

## Business Model

Free Tier (Open Source) → Paid Tier (This Repo)
- CLI on GitHub → Backend API
- Sends telemetry → Processes with ML
- 1,000+ users → Gets better with scale
- Provides training data → THE COMPETITIVE MOAT

## Revenue Model

Free → Pro ($29/mo) → Enterprise ($99/mo)
1,000 free users → 50 paid → $1,450/month
ML models improve with scale

## Next Steps

1. ✅ Repository created
2. Push to GitHub
3. Read SETUP_GUIDE.md for local development
4. Read DEPLOYMENT.md when ready to deploy

The moat is in `backend/ml/anomaly_detection.py` 🔥
ENDFILE

# quick-start.sh
cat > "$ROOT_DIR/quick-start.sh" << 'ENDFILE'
#!/bin/bash
echo "🐕 SudoDog Platform Quick Start"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Starting PostgreSQL and Redis..."
cd infrastructure
docker-compose up -d postgres redis
echo "✓ Services started"
echo ""
echo "Next steps:"
echo "  cd backend"
echo "  python3 -m venv venv"
echo "  source venv/bin/activate"
echo "  pip install -r requirements.txt"
echo "  uvicorn api.main:app --reload"
echo ""
echo "API will be at: http://localhost:8000"
ENDFILE

chmod +x "$ROOT_DIR/quick-start.sh"

# Initialize Git
cd "$ROOT_DIR"
git init
git add .
git commit -m "Initial setup: Backend API, ML pipeline, Frontend dashboard"
git branch -M main
git config commit.gpgsign false

# Final message
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ SUCCESS! Repository created"
echo ""
echo "Location: $ROOT_DIR"
echo "Files: $(find . -type f | wc -l) files created"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "NEXT: Push to GitHub"
echo ""
echo "Run these commands:"
echo ""
echo "  git remote add origin git@github.com:SudoDog-official/sudodog-platform.git"
echo "  git push -u origin main"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
