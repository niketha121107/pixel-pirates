import os
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # YouTube API Configuration
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    YOUTUBE_API_SERVICE_NAME: str = "youtube"
    YOUTUBE_API_VERSION: str = "v3"
    
    # OpenRouter API Configuration
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct")
    
    # JWT Authentication Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "fallback-secret-key-change-this")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 1440))
    
    # Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fallback-secret-key")
    
    # Application Configuration
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:5000")
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./pixel_pirates.db")
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "pixel_pirates")
    
    # Learning Algorithm Configuration
    PASSING_SCORE_THRESHOLD: float = 0.70  # 70% to pass
    ADAPTIVE_DIFFICULTY_ENABLED: bool = True
    MAX_QUIZ_QUESTIONS: int = 15
    MIN_QUIZ_QUESTIONS: int = 5
    
    # Video Search Configuration
    MAX_VIDEO_RESULTS: int = 10
    VIDEO_DURATION_PREFERENCE: str = "medium"  # short, medium, long
    
    def validate_settings(self) -> bool:
        """Validate that all required settings are present"""
        required_settings = [
            ("YOUTUBE_API_KEY", self.YOUTUBE_API_KEY),
            ("OPENROUTER_API_KEY", self.OPENROUTER_API_KEY),
            ("JWT_SECRET_KEY", self.JWT_SECRET_KEY),
        ]
        
        missing = []
        for name, value in required_settings:
            if not value or value.startswith("fallback"):
                missing.append(name)
        
        if missing:
            print(f"⚠️  Missing required environment variables: {', '.join(missing)}")
            return False
        
        return True

settings = Settings()