#!/usr/bin/env python3
"""
Pixel Pirates Backend Startup Script
Integrated with YouTube API and OpenRouter AI
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'google-api-python-client',
        'requests',
        'openai',
        'httpx'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required dependencies:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing dependencies with:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def check_api_keys():
    """Verify API keys are configured"""
    from app.core.config import settings
    
    issues = []
    
    if not settings.YOUTUBE_API_KEY or settings.YOUTUBE_API_KEY == "your_youtube_api_key_here":
        issues.append("YouTube API key not configured")
    
    if not settings.OPENROUTER_API_KEY or settings.OPENROUTER_API_KEY == "your_openrouter_api_key_here":
        issues.append("OpenRouter API key not configured")
    
    if issues:
        print("⚠️  API Configuration Issues:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n🔧 Update API keys in app/core/config.py")
        return False
    
    print("✅ API keys configured")
    return True

def test_api_connections():
    """Test connections to external APIs"""
    print("🔍 Testing API connections...")
    
    # Test YouTube API
    try:
        from app.services.youtube_service import youtube_service
        print("✅ YouTube API service initialized")
    except Exception as e:
        print(f"❌ YouTube API error: {e}")
        return False
    
    # Test OpenRouter API  
    try:
        from app.services.openrouter_service import openrouter_service
        print("✅ OpenRouter API service initialized")
    except Exception as e:
        print(f"❌ OpenRouter API error: {e}")
        return False
    
    return True

def main():
    """Main startup sequence"""
    print("🚀 Pixel Pirates Backend Startup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run checks
    if not check_dependencies():
        sys.exit(1)
    
    if not check_api_keys():
        print("⚠️  Continuing with limited functionality...")
    
    if not test_api_connections():
        print("⚠️  Some API connections failed - check your keys")
    
    print("\n🎯 Starting FastAPI server...")
    print("📍 API will be available at: http://localhost:5000")
    print("📚 API docs at: http://localhost:5000/docs")
    print("🔄 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the server
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=5000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()