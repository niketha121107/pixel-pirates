#!/usr/bin/env python3
"""Quick test of fresh videos endpoint"""

import asyncio
import httpx

async def test():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Login
        r1 = await client.post(
            "http://localhost:5000/api/auth/login",
            json={"email": "alex@edutwin.com", "password": "password123"}
        )
        print(f"Login: {r1.status_code}")
        token = r1.json()["access_token"]
        
        # Get topic
        r2 = await client.get(
            "http://localhost:5000/api/topics",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"Get topics: {r2.status_code}")
        topic_id = r2.json()["data"]["topics"][0]["id"]
        print(f"Topic ID: {topic_id}")
        
        # Try fresh videos
        print(f"\nCalling /api/topics/{topic_id}/fresh-videos...")
        try:
            r3 = await client.get(
                f"http://localhost:5000/api/topics/{topic_id}/fresh-videos",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            print(f"Fresh videos: {r3.status_code}")
            print(f"Response: {r3.text[:500]}")
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")

asyncio.run(test())
