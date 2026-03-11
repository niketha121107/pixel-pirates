import requests, json

BASE = "http://localhost:5002"
r = requests.post(f"{BASE}/api/auth/login", json={"email":"dharikha@edutwin.com","password":"password123"})
token = r.json()["access_token"]
h = {"Authorization": f"Bearer {token}"}

# Test topic-1
r2 = requests.get(f"{BASE}/api/topics/topic-1", headers=h)
topic = r2.json()["data"]["topic"]

print("=== VISUAL EXPLANATION ===")
for exp in topic.get("explanations", []):
    if exp["style"] == "visual":
        content = exp["content"]
        print(f"Has FLOWCHART prefix: {content.startswith('[FLOWCHART]')}")
        if content.startswith("[FLOWCHART]"):
            fc = json.loads(content.replace("[FLOWCHART]", ""))
            print(f"Flowchart nodes: {len(fc['nodes'])}")
            for n in fc["nodes"]:
                print(f"  {n['type']:10s} | {n['label']}")
        break

print()
print("=== RECOMMENDED VIDEOS ===")
vids = topic.get("recommendedVideos", [])
print(f"Count: {len(vids)}")
for v in vids:
    ytid = v.get("youtubeId", "N/A")
    title = v.get("title", "N/A")
    print(f"  {ytid} - {title}")

print()
print("=== ALL ENDPOINTS ===")
endpoints = [
    ("/api/topics", "Topics"),
    ("/api/topics/topic-1", "Topic1"),
    ("/api/users/stats", "Stats"),
    ("/api/analytics/dashboard", "Dashboard"),
    ("/api/leaderboard", "Leaderboard"),
]
for path, name in endpoints:
    r = requests.get(f"{BASE}{path}", headers=h)
    print(f"  {r.status_code} {name}")
