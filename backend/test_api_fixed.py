#!/usr/bin/env python
"""Test API response with correct endpoint formats"""
import requests
import json

print('Testing API endpoint...')
print('=' * 60)

# Login
login = requests.post('http://localhost:5000/api/auth/login', json={'email': 'alex@edutwin.com', 'password': 'password123'})
print(f'Login response code: {login.status_code}')

if login.status_code != 200:
    print(f'❌ Login failed: {login.text[:300]}')
else:
    data = login.json()
    # Try different token formats
    token = data.get('access_token') or data.get('data', {}).get('token') or data.get('token')
    
    if not token:
        print(f'❌ No token found in response')
        print(f'Response keys: {list(data.keys())}')
    else:
        print(f'✅ Logged in')
        
        # Get topic with correct Bearer format
        headers = {'Authorization': f'Bearer {token}'}
        r = requests.get('http://localhost:5000/api/topics/1', headers=headers)
        print(f'\nTopic request Status: {r.status_code}')
        
        if r.status_code == 200:
            response = r.json()
            topic = response.get('data', {})
            print(f'Topic: {topic.get("topicName")}')
            print(f'Has recommendedVideos: {"recommendedVideos" in topic}')
            
            videos = topic.get('recommendedVideos', [])
            print(f'Videos count: {len(videos)}')
            
            if videos:
                print(f'\n✅ First 2 videos:')
                for i, v in enumerate(videos[:2], 1):
                    print(f'  {i}. ID: {v.get("youtubeId")} | {v.get("title")}')
            else:
                print(f'\n❌ NO VIDEOS!')
                print(f'Response keys: {list(topic.keys())}')
                print(f'Full response: {json.dumps(topic, indent=2)[:500]}')
        else:
            print(f'❌ Error: {r.status_code}')
            print(f'Response: {r.text[:200]}')
