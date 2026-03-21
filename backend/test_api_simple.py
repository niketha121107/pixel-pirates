#!/usr/bin/env python
"""Test API response"""
import requests
import json

print('Testing API endpoint...')
print('=' * 60)

# Login
login = requests.post('http://localhost:5000/api/auth/login', json={'email': 'alex@edutwin.com', 'password': 'password123'})
print(f'Login response code: {login.status_code}')
print(f'Login response: {login.text[:300]}')

if login.status_code != 200:
    print('❌ Login failed')
else:
    token = login.json().get('data', {}).get('token')
    if not token:
        print('❌ No token in response')
    else:
        print(f'✅ Logged in, token: {token[:30]}...')
    
    # Get topic
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get('http://localhost:5000/api/topics/1', headers=headers)
    print(f'\nStatus: {r.status_code}')
    
    if r.status_code == 200:
        data = r.json()
        topic = data.get('data', {})
        print(f'Topic: {topic.get("topicName")}')
        print(f'Has recommendedVideos: {"recommendedVideos" in topic}')
        videos = topic.get('recommendedVideos', [])
        print(f'Videos count: {len(videos)}')
        if videos:
            print(f'First video: {videos[0]}')
        else:
            print(f'Response keys: {list(topic.keys())}')
    else:
        print(f'Error: {r.text[:200]}')
