#!/usr/bin/env python3
"""
Test the new custom topic AI quiz endpoint
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

BASE_URL = "http://localhost:5000/api"
API_KEY = os.getenv('GEMINI_API_KEY')

async def test_custom_topic_quiz():
    """Test generating quiz questions for a custom topic"""
    
    print("\n" + "="*70)
    print("🚀 TESTING CUSTOM TOPIC AI QUIZ ENDPOINT")
    print("="*70 + "\n")
    
    # First, get a test user token (create a test account)
    test_email = "test_custom@example.com"
    test_password = "TestPass123!"
    
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            # Try to signup
            print("📝 Signing up test user...")
            signup_res = await client.post(
                f"{BASE_URL}/auth/signup",
                json={
                    "name": "Test User",
                    "email": test_email,
                    "password": test_password
                }
            )
            
            if signup_res.status_code == 200:
                print("✅ Signup successful")
                user_data = signup_res.json()
                token = user_data.get('data', {}).get('token', '')
            elif signup_res.status_code == 400:
                # User already exists, try login
                print("📝 User exists, logging in...")
                login_res = await client.post(
                    f"{BASE_URL}/auth/login",
                    json={
                        "email": test_email,
                        "password": test_password
                    }
                )
                if login_res.status_code == 200:
                    print("✅ Login successful")
                    user_data = login_res.json()
                    token = user_data.get('data', {}).get('token', '')
                else:
                    print(f"❌ Login failed: {login_res.status_code}")
                    return
            else:
                print(f"❌ Signup failed: {signup_res.status_code}")
                print(signup_res.text[:200])
                return
            
            if not token:
                print("❌ No token received")
                return
            
            print(f"🔐 Token: {token[:20]}...")
            
            # Now test the custom topic endpoint
            print("\n" + "-"*70)
            print("📚 Testing Custom Topic Quiz Generation")
            print("-"*70)
            
            test_topics = [
                "Quantum Physics",
                "Machine Learning Basics",
                "Renaissance Art History",
                "Python Data Structures"
            ]
            
            for topic in test_topics:
                print(f"\n🔍 Topic: '{topic}'")
                print(f"   Parameters: 5 questions, mixed difficulty")
                
                headers = {"Authorization": f"Bearer {token}"}
                
                res = await client.post(
                    f"{BASE_URL}/ai/quiz/custom-topic",
                    params={
                        "topic_name": topic,
                        "question_count": 5,
                        "difficulty": "mixed"
                    },
                    headers=headers
                )
                
                if res.status_code == 200:
                    data = res.json()
                    questions = data.get('data', {}).get('questions', [])
                    print(f"   ✅ Success! Generated {len(questions)} questions")
                    
                    if questions and len(questions) > 0:
                        q1 = questions[0]
                        print(f"   📝 Sample Q1: {q1.get('question', '')[:60]}...")
                        if q1.get('options'):
                            print(f"   📋 Options: {len(q1.get('options', []))} options provided")
                
                else:
                    print(f"   ❌ Failed with status {res.status_code}")
                    print(f"   Error: {res.text[:150]}")
            
            print("\n" + "="*70)
            print("✅ CUSTOM TOPIC ENDPOINT TEST COMPLETE")
            print("="*70 + "\n")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_custom_topic_quiz())
