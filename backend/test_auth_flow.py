#!/usr/bin/env python3
"""Test authentication flow"""

import sys
sys.path.insert(0, ".")

import httpx
import asyncio

async def test_auth():
    print("Testing Authentication Flow")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        # Test 1: Check if backend is responding
        print("\n1. Checking backend connectivity...")
        try:
            response = await client.get("http://localhost:5000/docs", timeout=3.0)
            print(f"   ✅ Backend responding (status: {response.status_code})")
        except Exception as e:
            print(f"   ❌ Backend not responding: {e}")
            return False
        
        # Test 2: Try login with valid user
        print("\n2. Testing login endpoint...")
        try:
            login_data = {
                "email": "alex@edutwin.com",
                "password": "password123"  # Need to verify this
            }
            
            response = await client.post(
                "http://localhost:5000/api/auth/login",
                json=login_data,
                timeout=5.0
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            
            if response.status_code == 200:
                print("   ✅ Login successful")
                return True
            else:
                print(f"   ⚠️  Login failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

if __name__ == "__main__":
    asyncio.run(test_auth())
