#!/usr/bin/env python
"""Test API connectivity"""
import httpx
import asyncio

async def test_connection():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Test backend
            backend_resp = await client.get('http://localhost:8000/docs')
            print(f"✅ Backend responding: {backend_resp.status_code}")
            
            # Test login endpoint (to verify it exists)
            login_test = await client.post('http://localhost:8000/auth/login', json={
                "email": "test@test.com", 
                "password": "wrong"
            })
            print(f"✅ API endpoint reachable: {login_test.status_code} (expected auth failure is OK)")
            return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

asyncio.run(test_connection())
