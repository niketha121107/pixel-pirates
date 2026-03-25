import os
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables from .env file
# Try several paths to be sure
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(project_root, ".env")
load_dotenv(env_path)
load_dotenv() # Also load from CWD

class Settings:
    # YouTube API Configuration
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    YOUTUBE_API_SERVICE_NAME: str = "youtube"
    YOUTUBE_API_VERSION: str = "v3"
    
    # OpenRouter API Configuration
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct")

    # Ollama (Llama) local chatbot fallback
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1")

    # Gemini API Configuration (used for adaptive quiz + quiz evaluation)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_BASE_URL: str = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
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

# Debug print to verify loading (only shows first/last few chars for security)
key = settings.GEMINI_API_KEY
if key:
    print(f"✅ Gemini API Key loaded: {key[:5]}...{key[-5:]}")
else:
    print("❌ Gemini API Key NOT found in environment")