#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import sys

# Force reload
load_dotenv()

key = os.getenv("YOUTUBE_API_KEY", "NOT_FOUND")
print(f"Loaded YouTube API Key: {key[:30]}...")

# Also check directly from app settings
sys.path.insert(0, ".")
from app.core.config import settings
print(f"Settings key: {settings.YOUTUBE_API_KEY[:30]}...")
