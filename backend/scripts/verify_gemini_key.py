"""
Verify Gemini API Key Setup
Run this after updating your API key in .env
"""

import os
import sys
from dotenv import load_dotenv
import httpx
import asyncio

print("=" * 70)
print("GEMINI API KEY VERIFICATION")
print("=" * 70)

# Load environment
load_dotenv()

# Get API key
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("\n[ERROR] No GEMINI_API_KEY found in .env file")
    print("\nFix: Update .env with: GEMINI_API_KEY=<your-key>")
    sys.exit(1)

print(f"\n[OK] API Key found: {api_key[:25]}...")

async def test_api():
    """Test Gemini API connectivity"""
    print("\n[TEST] Connecting to Gemini API...")
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    params = {"key": api_key}
    
    payload = {
        "contents": [{
            "parts": [{"text": "Say 'Pixel Pirates AI is working!'" }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 50
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, params=params, json=payload)
            
            print(f"[HTTP] Status: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                if "candidates" in data and len(data["candidates"]) > 0:
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    print(f"[OK] Response: {text}")
                    return True
                else:
                    print("[ERROR] Invalid response format")
                    return False
            
            elif resp.status_code == 403:
                error = resp.json()
                print(f"[ERROR] 403 - API Key Issue")
                print(f"Message: {error.get('error', {}).get('message', 'Unknown error')}")
                print("\nFix: Generate new key from https://makersuite.google.com/app/apikey")
                return False
            
            elif resp.status_code == 429:
                print("[WARN] Rate limited - try again in a moment")
                return False
            
            else:
                print(f"[ERROR] {resp.status_code}: {resp.text[:200]}")
                return False
                
    except asyncio.TimeoutError:
        print("[ERROR] API timeout (try again)")
        return False
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        return False

# Run test
success = asyncio.run(test_api())

print("\n" + "=" * 70)
if success:
    print("VERIFICATION PASSED - API is working!")
    print("\nNext: Run test_ai_integration.py to test all endpoints")
else:
    print("VERIFICATION FAILED - Check error above")
    print("\nCommon fixes:")
    print("1. Generate new key: https://makersuite.google.com/app/apikey")
    print("2. Update .env file with new key")
    print("3. Restart backend")
    print("4. Run this verification again")
print("=" * 70)

sys.exit(0 if success else 1)
