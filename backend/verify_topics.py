import requests
# Sign up a test user first, then get topics
base = "http://localhost:8000/api"

# Try to sign up
r = requests.post(f"{base}/auth/signup", json={"name": "Test User", "email": "test_verify@test.com", "password": "Test1234!"})
if r.status_code == 200:
    token = r.json().get("data", {}).get("token", "")
elif r.status_code == 400:
    # Already exists, login
    r = requests.post(f"{base}/auth/login", json={"email": "test_verify@test.com", "password": "Test1234!"})
    token = r.json().get("data", {}).get("token", "")
else:
    print(f"Auth failed: {r.status_code} {r.text[:200]}")
    exit()

# Get topics
r = requests.get(f"{base}/topics", headers={"Authorization": f"Bearer {token}"})
data = r.json()
topics = data.get("data", {}).get("topics", [])
print(f"API returns {len(topics)} topics")

# Check all have videos
no_vids = [t['topicName'] for t in topics if not any(v.get('youtubeId') for v in t.get('recommendedVideos', []))]
print(f"Topics without videos: {no_vids}")

# Show languages
langs = {}
for t in topics:
    lang = t.get('language', '?')
    langs[lang] = langs.get(lang, 0) + 1
for lang, count in sorted(langs.items()):
    print(f"  {lang}: {count} topics")
