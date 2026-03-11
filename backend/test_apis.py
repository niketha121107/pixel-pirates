"""Quick test of Gemini + YouTube APIs."""
import httpx, os, json
from dotenv import load_dotenv
load_dotenv()

# Test Gemini  
key = os.getenv("GEMINI_API_KEY", "")

# Try multiple models to find one with remaining quota
models_to_try = ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite"]
for model in models_to_try:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    resp = httpx.post(url, json={"contents": [{"parts": [{"text": "Say hello"}]}]}, timeout=30)
    print(f"  {model}: {resp.status_code}")
    if resp.status_code == 200:
        txt = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        print(f"    Response: {txt[:100]}")
        break

prompt = 'Return a JSON object with keys "title" and "overview" about the topic Python Variables. ONLY valid JSON, no markdown fences.'
print("\nGemini model tests:")

# Test YouTube
yt_key = os.getenv("YOUTUBE_API_KEY", "")
yt_resp = httpx.get("https://www.googleapis.com/youtube/v3/search", params={
    "key": yt_key, "q": "Python variables tutorial", "part": "id", "maxResults": 1, "type": "video"
})
print("\nYouTube status:", yt_resp.status_code)
if yt_resp.status_code == 200:
    print("YouTube works! Items:", len(yt_resp.json().get("items", [])))
else:
    err = yt_resp.json().get("error", {})
    print("YouTube error:", err.get("message", yt_resp.text[:300]))
