import requests
base = 'http://localhost:8000/api'

# Login
r = requests.post(f'{base}/auth/login', json={'email': 'dharikha123@gmail.com', 'password': 'dharikha123'})
if r.status_code != 200:
    # Try signup
    r = requests.post(f'{base}/auth/signup', json={'name': 'Test', 'email': 'apitest@test.com', 'password': 'Test12!'})
    if r.status_code != 200:
        print(f'Auth failed: {r.status_code} {r.text[:200]}')
        # one more try
        r = requests.post(f'{base}/auth/login', json={'email': 'apitest@test.com', 'password': 'Test12!'})
    
token = r.json().get('access_token', '') or r.json().get('data', {}).get('token', '')
if not token:
    print('No token! Response:', r.json())
    exit()

r2 = requests.get(f'{base}/topics', headers={'Authorization': f'Bearer {token}'})
topics = r2.json().get('data', {}).get('topics', [])
print(f'API returns {len(topics)} topics')

# Check all have videos
no_vids = [t['topicName'] for t in topics if not any(v.get('youtubeId') for v in t.get('recommendedVideos', []))]
if no_vids:
    print(f'Topics WITHOUT videos: {len(no_vids)}')
else:
    print('All topics have YouTube videos!')

langs = {}
for t in topics:
    lang = t.get('language', '?')
    langs[lang] = langs.get(lang, 0) + 1
for lang, count in sorted(langs.items()):
    print(f'  {lang}: {count}')
