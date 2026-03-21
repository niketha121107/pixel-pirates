#!/usr/bin/env python
"""Test signup endpoint to see what error is happening"""

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
        
        print("Testing signup endpoint...")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = await client.post(
                'http://localhost:8000/auth/signup',
                json=payload
            )
            
            print(f"\nStatus Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Body: {response.text}")
            
            if response.status_code == 200:
                print("\n✅ Signup successful!")
                print(f"User data: {response.json()}")
            else:
                print(f"\n❌ Signup failed with status {response.status_code}")
                try:
                    print(f"Error details: {response.json()}")
                except:
                    print(f"Error: {response.text}")
                    
        except Exception as e:
            print(f"\n❌ Request failed: {e}")
            import traceback
            traceback.print_exc()

asyncio.run(test_signup())
