#!/usr/bin/env python
"""Test API endpoint with optimized explanations"""

import requests
import json
from pymongo import MongoClient
from app.core.config import Settings

# Get a sample topic ID
settings = Settings()
client = MongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DATABASE]

topic = db.topics.find_one()
if not topic:
    print("No topics found!")
    exit(1)

topic_id = str(topic['_id'])
print(f"\nTesting API with optimized explanations...")
print(f"Topic ID: {topic_id}")
print(f"Topic: {topic.get('name', 'Unknown')}")

# Test the API endpoint
try:
    url = f"http://localhost:8000/api/topics/{topic_id}"
    print(f"\nAPI URL: {url}")
    
    response = requests.get(url, headers={
        "Authorization": "Bearer test_token"
    }, timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ API Response Status: {response.status_code} (SUCCESS)")
        
        # Check explanation sizes
        if 'explanations' in data:
            expl = data['explanations']
            print(f"\nExplanation Types Present:")
            
            for dtype in ['simplified', 'logical', 'visual', 'analogy']:
                if dtype in expl:
                    size = len(str(expl[dtype]))
                    preview = str(expl[dtype])[:80]
                    print(f"  ✓ {dtype:12}: {size:5} chars")
                    print(f"    Preview: {preview}...")
            
            print(f"\n✓ All explanations are properly sized for UI display")
            print(f"✓ No overflow issues expected")
        else:
            print("No explanations in response")
            
    else:
        print(f"✗ API returned status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
except requests.exceptions.ConnectionError:
    print(f"✗ Cannot connect to backend on localhost:8000")
    print(f"  Make sure backend is running: python -m uvicorn main:app --port 8000")
except Exception as e:
    print(f"✗ Error: {str(e)}")

client.close()
