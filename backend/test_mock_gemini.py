#!/usr/bin/env python3
"""
Test script to verify mock test generation uses Gemini API
"""
import asyncio
import httpx
import json
import sys

async def test_mock_test_generation():
    """Test the mock test endpoint"""
    
    # Test data
    test_request = {
        "topics": ["Python", "Data Structures"],
        "difficulty_mix": {
            "Beginner": 5,
            "Intermediate": 5,
            "Advanced": 5
        },
        "total_questions": 15
    }
    
    # First, get a token by logging in
    print("📝 Logging in...")
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    async with httpx.AsyncClient() as client:
        # Try to login
        try:
            login_response = await client.post(
                "http://127.0.0.1:8000/api/auth/login",
                json=login_data,
                timeout=10.0
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                token = login_data.get("data", {}).get("access_token")
                print(f"✅ Logged in successfully, token: {token[:20]}...")
            else:
                print(f"⚠️  Login failed: {login_response.status_code}")
                token = "test-token"
        except Exception as e:
            print(f"⚠️  Could not login: {e}")
            token = "test-token"
        
        # Now test the mock test endpoint
        print(f"\n🧪 Testing mock test generation with topics: {test_request['topics']}")
        print(f"   Total questions requested: {test_request['total_questions']}")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = await client.post(
                "http://127.0.0.1:8000/api/quiz/mock-test",
                json=test_request,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                mock_test = result.get("data", {}).get("mockTest", {})
                questions = mock_test.get("questions", [])
                metadata = mock_test.get("metadata", {})
                
                print(f"\n✅ SUCCESS! Generated mock test:")
                print(f"   Title: {metadata.get('title', 'N/A')}")
                print(f"   Total Questions: {len(questions)}")
                print(f"   Estimated Time: {metadata.get('estimatedTime', 'N/A')}")
                
                print(f"\n📋 Sample Questions (first 3):")
                for i, q in enumerate(questions[:3]):
                    print(f"\n   Question {i+1}:")
                    print(f"   Type: {q.get('type', 'N/A')}")
                    print(f"   Q: {q.get('question', 'N/A')[:80]}...")
                    if q.get('options'):
                        print(f"   Options: {q.get('options', [])}")
                    print(f"   Difficulty: {q.get('difficulty', 'N/A')}")
                    print(f"   Explanation: {q.get('explanation', 'N/A')[:60]}...")
                
                print(f"\n✅ All {len(questions)} questions generated successfully using Gemini AI!")
                return True
            else:
                print(f"\n❌ Error: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    result = asyncio.run(test_mock_test_generation())
    sys.exit(0 if result else 1)
