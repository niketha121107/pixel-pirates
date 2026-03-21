#!/usr/bin/env python
"""Test signup endpoint with correct /api path"""

import httpx
import asyncio
import json

async def test_signup():
    async with httpx.AsyncClient(timeout=10.0) as client:
        payload = {
            "name": "test3",
            "email": "test3@gmail.com",
            "password": "password123"
        }
        
        print("Testing signup endpoint at /api/auth/signup...")
        
        try:
            response = await client.post(
                'http://localhost:8000/api/auth/signup',
                json=payload
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print("✅ Signup successful!")
                data = response.json()
                print(f"  Token: {data.get('access_token', 'N/A')[:50]}...")
                print(f"  User: {data.get('user', {}).get('email')}")
            elif response.status_code == 409:
                print("⚠️  User already exists (409)")
                print(f"  Details: {response.json()}")
            else:
                print(f"❌ Failed with status {response.status_code}")
                print(f"  Response: {response.json()}")
                    
        except Exception as e:
            print(f"❌ Request failed: {e}")

asyncio.run(test_signup())
