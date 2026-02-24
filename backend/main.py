from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import uvicorn
from app.models import *
from app.data import get_mock_data, initialize_data
from app.routes import auth, users, topics, quiz, videos, leaderboard, analytics, search
from app.routes import database as db_routes
from app.core.config import Settings
from app.core.database import connect_to_mongo, close_mongo_connection

settings = Settings()

# Initialize data with proper password hashing
initialize_data()

app = FastAPI(
    title="Pixel Pirates API",
    description="Educational platform API for Pixel Pirates with AI-powered learning and YouTube integration",
    version="2.0.0"
)

# Configure CORS using environment variables
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection events
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    print("🚀 Starting Pixel Pirates API...")
    
    # Initialize mock data (temporary until full migration)
    initialize_data()
    
    # Connect to MongoDB
    print("📦 Connecting to MongoDB...")
    connection_success = await connect_to_mongo(settings)
    
    if connection_success:
        print("✅ MongoDB connected successfully!")
    else:
        print("⚠️  MongoDB connection failed - continuing with mock data")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connection on shutdown"""
    print("🔄 Shutting down Pixel Pirates API...")
    await close_mongo_connection()
    print("✅ Database connection closed")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "detail": str(exc) if settings.API_BASE_URL.startswith("http://localhost") else "Something went wrong"
        }
    )

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(topics.router, prefix="/api/topics", tags=["topics"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["quiz"])
app.include_router(videos.router, prefix="/api/videos", tags=["videos"])
app.include_router(leaderboard.router, prefix="/api/leaderboard", tags=["leaderboard"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(db_routes.router, prefix="/api/database", tags=["database"])

@app.get("/")
async def read_root():
    return {
        "message": "🏴‍☠️ Welcome to Pixel Pirates API", 
        "version": "2.0.0",
        "features": [
            "JWT Authentication",
            "AI-Powered Learning (Mistral 7B)",
            "YouTube Video Integration",
            "Adaptive Quizzes",
            "Progress Analytics"
        ],
        "docs": f"{settings.API_BASE_URL}/docs"
    }

@app.get("/api")
async def api_info():
    return {
        "message": "Pixel Pirates API v2.0.0", 
        "endpoints": {
            "auth": "/api/auth (login, signup, logout, refresh)",
            "users": "/api/users (profile, stats)",
            "topics": "/api/topics (learning content)",
            "quiz": "/api/quiz (adaptive quizzes, mock tests)",
            "videos": "/api/videos (YouTube integration)",
            "leaderboard": "/api/leaderboard (rankings)",
            "analytics": "/api/analytics (progress tracking)",
            "search": "/api/search (content search)"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "environment": "development" if settings.API_BASE_URL.startswith("http://localhost") else "production"
    }

if __name__ == "__main__":
    # Validate settings before starting
    if not settings.validate_settings():
        print("❌ Configuration validation failed. Please check your .env file.")
        exit(1)
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=5000,
        reload=True,
        log_level="info"
    )
