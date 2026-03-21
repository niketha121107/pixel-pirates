#!/usr/bin/env python
"""Test API response with real topic ID"""
import requests
import json

print('Testing API with real topic ID...')
print('=' * 60)

# Login
login = requests.post('http://localhost:5000/api/auth/login', json={'email': 'alex@edutwin.com', 'password': 'password123'})
print(f'Login response code: {login.status_code}')

if login.status_code != 200:
    print(f'❌ Login failed')
else:
    data = login.json()
    token = data.get('access_token')
    
    if not token:
        print(f'❌ No token found')
    else:
        print(f'✅ Logged in')
        
        # Test with real topic ID
        headers = {'Authorization': f'Bearer {token}'}
        topic_id = '69be3230d65766f43d9e6ae8'  # First topic
        
        r = requests.get(f'http://localhost:5000/api/topics/{topic_id}', headers=headers)
        print(f'Topic request Status: {r.status_code}')
        
        if r.status_code == 200:
            response = r.json()
            print(f'Response keys: {list(response.keys())}')
            print(f'Response data keys: {list(response.get("data", {}).keys())}')
            
            # Navigate the response structure
            if isinstance(response, dict) and 'data' in response:
                data = response['data']
                if 'topic' in data:
                    topic = data['topic']
                else:
                    topic = data
            else:
                topic = response
            
            print(f'\nTopic: {topic.get("topicName") or topic.get("name")}')
            
            # Check different possible video field names
            videos = None
            for field_name in ['recommendedVideos', 'videos', 'video']:
                if field_name in topic:
                    videos = topic[field_name]
                    print(f'Found videos in field: {field_name}')
                    break
            
            if videos is None:
                print(f'❌ NO VIDEOS FOUND!')
                print(f'Available keys in topic: {list(topic.keys())}')
            else:
                print(f'Videos count: {len(videos)}')
                if videos:
                    print(f'\nFirst 2 videos:')
                    for i, v in enumerate(videos[:2], 1):
                        vid_id = v.get("youtubeId") if isinstance(v, dict) else v
                        title = v.get("title", "") if isinstance(v, dict) else ""
                        print(f'  {i}. ID: {vid_id} | {title}')
                else:
                    print(f'Videos list is empty!')
        else:
            print(f'❌ Error: {r.status_code}')
            print(f'Response: {r.text[:300]}')
