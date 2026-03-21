#!/usr/bin/env python3
"""Test API with authentication"""
import requests
import json

# First, login to get a token
login_data = {
    "email": "alex@edutwin.com",
    "password": "password123"
}

print("Step 1: Logging in...")
login_response = requests.post("http://127.0.0.1:8000/api/auth/login", json=login_data)
print(f"Login status: {login_response.status_code}")

if login_response.status_code == 200:
    token = login_response.json().get("access_token")
    print(f"Got token: {token[:20]}...")
    
    # Now test the topic endpoint with auth header
    headers = {"Authorization": f"Bearer {token}"}
    topic_id = "69be3230d65766f43d9e6ae8"  # Python - Syntax & Variables
    url = f"http://127.0.0.1:8000/api/topics/{topic_id}"
    
    print(f"\nStep 2: Getting topic details...")
    response = requests.get(url, headers=headers)
    print(f"Topic API status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        topic = data.get("data", {}).get("topic", {})
        
        study_mat = topic.get("studyMaterial", {})
        print(f"\n✅ studyMaterial structure:")
        if isinstance(study_mat, dict):
            print(f"  Type: dict with {len(study_mat)} keys")
            print(f"  Keys: {list(study_mat.keys())}")
            for k in study_mat.keys():
                v = study_mat[k]
                if isinstance(v, str):
                    print(f"    {k}: {len(v)} chars")
                else:
                    print(f"    {k}: {v}")
        else:
            print(f"  Type: {type(study_mat).__name__}")
            print(f"  Value: {str(study_mat)[:100]}")
            
        print("\n📺 recommendedVideos:")
        videos = topic.get("recommendedVideos", [])
        for i, video in enumerate(videos[:2]):
            print(f"  Video {i+1}:")
            print(f"    youtubeId: {video.get('youtubeId')}")
            print(f"    title: {video.get('title')[:50]}")
            
        print("\n📝 explanations:")
        expls = topic.get("explanations", [])
        for expl in expls:
            style = expl.get('style')
            content_len = len(expl.get('content', ''))
            print(f"  {style}: {content_len} chars")
    else:
        print(f"Error: {response.status_code}")
        print(response.text[:300])
else:
    print(f"Login failed: {response.status_code}")
    print(login_response.text[:200])
