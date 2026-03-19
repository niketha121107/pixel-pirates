"""Test all available Gemini models to find one with remaining quota."""
import httpx, os
from dotenv import load_dotenv
load_dotenv()

key = os.getenv('GEMINI_API_KEY')
models = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash-001",
    "gemini-2.0-flash-lite-001",
    "gemini-2.5-pro",
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-pro-latest",
    "gemma-3-4b-it",
    "gemma-3-12b-it",
    "gemma-3-27b-it",
    "gemini-2.5-flash-lite-preview-09-2025",
    "gemini-3-flash-preview",
    "gemini-3-pro-preview",
    "gemini-3.1-pro-preview",
    "gemini-3.1-flash-lite-preview",
]

for model in models:
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        r = httpx.post(url, json={"contents": [{"parts": [{"text": "Say hi"}]}]}, timeout=20)
        if r.status_code == 200:
            txt = r.json()["candidates"][0]["content"]["parts"][0]["text"][:50]
            print(f"  ✅ {model}: WORKS! -> {txt}")
        else:
            print(f"  ❌ {model}: {r.status_code}")
    except Exception as e:
        print(f"  ❌ {model}: ERROR {e}")
