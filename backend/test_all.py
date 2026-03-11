import requests

BASE = "http://localhost:5000"

# Login
r = requests.post(f"{BASE}/api/auth/login", json={"email":"dharikha@edutwin.com","password":"password123"})
token = r.json()["access_token"]
h = {"Authorization": f"Bearer {token}"}
print("LOGIN: OK")

endpoints = [
    ("/api/topics", "Topics list"),
    ("/api/topics/topic-1", "Single topic"),
    ("/api/users/stats", "User stats"),
    ("/api/analytics/dashboard", "Dashboard"),
    ("/api/analytics/progress", "Progress"),
    ("/api/analytics/performance", "Performance"),
    ("/api/analytics/streaks", "Streaks"),
    ("/api/leaderboard", "Leaderboard"),
    ("/api/search/recent", "Search history"),
    ("/api/videos/watched", "Watched videos"),
]

all_ok = True
for path, name in endpoints:
    try:
        r = requests.get(f"{BASE}{path}", headers=h)
        if r.status_code == 200:
            print(f"  OK  {name}")
        else:
            print(f"  ERR {name} -> {r.status_code}: {r.text[:100]}")
            all_ok = False
    except Exception as e:
        print(f"  FAIL {name} -> {e}")
        all_ok = False

print()
if all_ok:
    print("ALL ENDPOINTS WORKING!")
else:
    print("SOME ENDPOINTS FAILED!")
