# SudoDog Platform - Private Repository

**⚠️ PRIVATE - Proprietary Code**

This repository contains the paid tier features for SudoDog:
- Backend API (FastAPI)
- ML anomaly detection (THE MOAT)
- Web dashboard (React)

## Quick Start

```bash
./quick-start.sh
See START_HERE.md for complete documentation.

Tech Stack
Backend: FastAPI, PostgreSQL, Redis, Celery
ML: scikit-learn (Isolation Forest)
Frontend: React, TypeScript, Tailwind CSS
Infrastructure: Docker Compose
Documentation
START_HERE.md - Overview and getting started
SETUP_GUIDE.md - Local development setup
DEPLOYMENT.md - Production deployment
Business Model: Open Core (Free CLI + Paid Platform)
The Moat: ML models trained on community telemetry data ENDFILE

backend/requirements.txt
cat > backend/requirements.txt << 'ENDFILE'

Backend Dependencies
fastapi==0.104.1 uvicorn[standard]==0.24.0 pydantic==2.5.0 pydantic-settings==2.1.0 sqlalchemy==2.0.23 psycopg2-binary==2.9.9 python-jose[cryptography]==3.3.0 passlib[bcrypt]==1.7.4 celery==5.3.4 redis==5.0.1 scikit-learn==1.3.2 pandas==2.1.3 numpy==1.26.2 joblib==1.3.2 sentry-sdk[fastapi]==1.38.0 python-dotenv==1.0.0 sendgrid==6.10.0 pytest==7.4.3 black==23.11.0 ENDFILE

backend/init.py
echo '"""SudoDog Platform Backend""" version = "1.0.0"' > backend/init.py

backend/api/init.py
touch backend/api/init.py

backend/api/config.py
cat > backend/api/config.py << 'ENDFILE' from pydantic_settings import BaseSettings

class Settings(BaseSettings): DATABASE_URL: str = "postgresql://sudodog:password@localhost:5432/sudodog_platform" REDIS_URL: str = "redis://localhost:6379/0" SECRET_KEY: str = "your-secret-key-change-this" ENVIRONMENT: str = "development" CORS_ORIGINS: str = "http://localhost:5173"

class Config:
    env_file = ".env"
def get_settings(): return Settings() ENDFILE

backend/api/main.py
cat > backend/api/main.py << 'ENDFILE' from fastapi import FastAPI from fastapi.middleware.cors import CORSMiddleware from backend.api.config import get_settings

settings = get_settings()

app = FastAPI( title="SudoDog Platform API", description="Proprietary API for paid tier features", version="1.0.0", )

app.add_middleware( CORSMiddleware, allow_origins=settings.CORS_ORIGINS.split(","), allow_credentials=True, allow_methods=[""], allow_headers=[""], )

@app.get("/health") async def health_check(): return {"status": "healthy"}

@app.get("/") async def root(): return {"message": "SudoDog Platform API", "version": "1.0.0"} ENDFILE

backend/api/routes/init.py
touch backend/api/routes/init.py

backend/api/routes/telemetry.py
cat > backend/api/routes/telemetry.py << 'ENDFILE' from fastapi import APIRouter, BackgroundTasks from pydantic import BaseModel from datetime import datetime

router = APIRouter()

class TelemetryEvent(BaseModel): user_id: str event_type: str timestamp: datetime data: dict

class TelemetryResponse(BaseModel): status: str message: str

@router.post("/", response_model=TelemetryResponse, status_code=202) async def receive_telemetry(event: TelemetryEvent, background_tasks: BackgroundTasks): """Receive telemetry from free tier CLI""" # TODO: Store in database, process with ML print(f"Received telemetry: {event.event_type} from {event.user_id}") return TelemetryResponse(status="accepted", message="Telemetry received") ENDFILE

backend/api/routes/auth.py
cat > backend/api/routes/auth.py << 'ENDFILE' from fastapi import APIRouter

router = APIRouter()

@router.post("/login") async def login(): """User login - TODO: Implement JWT""" return {"message": "Login endpoint - not implemented yet"}

@router.post("/register") async def register(): """User registration - TODO: Implement""" return {"message": "Register endpoint - not implemented yet"} ENDFILE

backend/api/routes/agents.py
cat > backend/api/routes/agents.py << 'ENDFILE' from fastapi import APIRouter

router = APIRouter()

@router.get("/") async def list_agents(): """List all agents for authenticated user""" return {"agents": []}

@router.get("/{agent_id}") async def get_agent(agent_id: str): """Get specific agent details""" return {"agent_id": agent_id, "status": "active"} ENDFILE

backend/api/routes/analytics.py
cat > backend/api/routes/analytics.py << 'ENDFILE' from fastapi import APIRouter

router = APIRouter()

@router.get("/anomalies") async def get_anomalies(): """Get ML-detected anomalies""" return {"anomalies": []}

@router.get("/insights") async def get_insights(): """Get ML-powered insights""" return {"insights": []} ENDFILE

backend/database/init.py
touch backend/database/init.py

backend/database/models.py
cat > backend/database/models.py << 'ENDFILE' from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float, Boolean from sqlalchemy.ext.declarative import declarative_base from sqlalchemy.sql import func

Base = declarative_base()

class User(Base): tablename = "users" id = Column(Integer, primary_key=True) email = Column(String, unique=True, nullable=False) hashed_password = Column(String, nullable=False) tier = Column(String, default="pro") # pro, enterprise created_at = Column(DateTime, server_default=func.now())

class Agent(Base): tablename = "agents" id = Column(Integer, primary_key=True) user_id = Column(Integer, ForeignKey("users.id")) name = Column(String, nullable=False) status = Column(String, default="active") created_at = Column(DateTime, server_default=func.now())

class TelemetryEvent(Base): tablename = "telemetry_events" id = Column(Integer, primary_key=True) user_id = Column(String) # Anonymous for free users agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True) event_type = Column(String, nullable=False) timestamp = Column(DateTime, nullable=False) data = Column(JSON)

class Anomaly(Base): tablename = "anomalies" id = Column(Integer, primary_key=True) agent_id = Column(Integer, ForeignKey("agents.id")) detected_at = Column(DateTime, server_default=func.now()) anomaly_score = Column(Float) description = Column(String) data = Column(JSON) ENDFILE

backend/ml/init.py
touch backend/ml/init.py

backend/ml/anomaly_detection.py
cat > backend/ml/anomaly_detection.py << 'ENDFILE' import pandas as pd import numpy as np from sklearn.ensemble import IsolationForest import joblib

class AnomalyDetector: """ML-based anomaly detection - THE MOAT"""

def __init__(self):
    self.model = None
    self.scaler = None

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
    """Save trained model"""
    joblib.dump(self.model, path)

def load_model(self, path: str):
    """Load trained model"""
    self.model = joblib.load(path)
    return self
