"""Validate all API keys in .env"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("API KEY VALIDATION")
print("=" * 60)

# 1. YouTube API Key
print("\n1. YOUTUBE API KEY")
yt_key = os.getenv("YOUTUBE_API_KEY", "")
print(f"   Key: {yt_key[:10]}...{yt_key[-4:]}" if len(yt_key) > 14 else f"   Key: {yt_key}")
try:
    resp = requests.get(
        "https://www.googleapis.com/youtube/v3/search",
        params={"q": "python tutorial", "part": "snippet", "maxResults": 1, "key": yt_key},
        timeout=10
    )
    if resp.status_code == 200:
        items = resp.json().get("items", [])
        print(f"   ✅ VALID — returned {len(items)} result(s)")
    elif resp.status_code == 403:
        error = resp.json().get("error", {}).get("errors", [{}])[0].get("reason", "unknown")
        if "quotaExceeded" in error:
            print(f"   ⚠️  KEY IS VALID but quota exceeded (daily limit reached)")
        else:
            print(f"   ❌ INVALID — 403 Forbidden: {error}")
    else:
        print(f"   ❌ FAILED — HTTP {resp.status_code}: {resp.text[:100]}")
except Exception as e:
    print(f"   ❌ ERROR — {e}")

# 2. Gemini API Key
print("\n2. GEMINI API KEY")
gemini_key = os.getenv("GEMINI_API_KEY", "")
gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
print(f"   Key: {gemini_key[:10]}...{gemini_key[-4:]}" if len(gemini_key) > 14 else f"   Key: {gemini_key}")
print(f"   Model: {gemini_model}")
try:
    resp = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={gemini_key}",
        json={"contents": [{"parts": [{"text": "Say hello in one word"}]}]},
        timeout=15
    )
    if resp.status_code == 200:
        text = resp.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        print(f"   ✅ VALID — Response: \"{text.strip()[:50]}\"")
    else:
        error_msg = resp.json().get("error", {}).get("message", resp.text[:100])
        print(f"   ❌ FAILED — HTTP {resp.status_code}: {error_msg}")
except Exception as e:
    print(f"   ❌ ERROR — {e}")

# 3. OpenRouter API Key
print("\n3. OPENROUTER API KEY")
or_key = os.getenv("OPENROUTER_API_KEY", "")
or_model = os.getenv("OPENROUTER_MODEL", "")
print(f"   Key: {or_key[:15]}...{or_key[-4:]}" if len(or_key) > 19 else f"   Key: {or_key}")
print(f"   Model: {or_model}")
try:
    resp = requests.get(
        "https://openrouter.ai/api/v1/auth/key",
        headers={"Authorization": f"Bearer {or_key}"},
        timeout=10
    )
    if resp.status_code == 200:
        data = resp.json().get("data", {})
        limit = data.get("limit", "unlimited")
        usage = data.get("usage", 0)
        print(f"   ✅ VALID — Usage: {usage}, Limit: {limit}")
    else:
        print(f"   ❌ FAILED — HTTP {resp.status_code}: {resp.text[:100]}")
except Exception as e:
    print(f"   ❌ ERROR — {e}")

# 4. MongoDB Connection
print("\n4. MONGODB CONNECTION")
mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
print(f"   URL: {mongo_url}")
try:
    from pymongo import MongoClient
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    db = client["pixel_pirates"]
    topic_count = db.topics.count_documents({})
    print(f"   ✅ CONNECTED — {topic_count} topics in database")
except Exception as e:
    print(f"   ❌ FAILED — {e}")

print("\n" + "=" * 60)
print("VALIDATION COMPLETE")
print("=" * 60)
