"""Quick verification of all API endpoints against running backend."""
import requests

BASE = "http://localhost:5000"

# Login
r = requests.post(f"{BASE}/api/auth/login", json={"email": "dharikha@edutwin.com", "password": "password123"})
assert r.status_code == 200, f"Login failed: {r.text}"
token = r.json()["access_token"]
h = {"Authorization": f"Bearer {token}"}
print("LOGIN OK")

# Topics
r = requests.get(f"{BASE}/api/topics", headers=h)
assert r.status_code == 200
topics = r.json()["data"]["topics"]
print(f"\nTOPICS ({len(topics)}):")
for t in topics:
    print(f"  {t['topicName']:30s} [{t['language']:12s}] status={t['status']:12s} score={t['score']}")

# Stats
r = requests.get(f"{BASE}/api/users/stats", headers=h)
assert r.status_code == 200
s = r.json()["data"]["stats"]
print(f"\nSTATS: avgScore={s['avgScore']} streak={s['streak']} hours={s['totalHours']} badges={len(s['badges'])} langs={len(s['languages'])}")
for b in s["badges"]:
    print(f"  {b['icon']} {b['name']} earned={b['earned']}")
for l in s["languages"]:
    print(f"  {l['name']}: level {l['level']}")

# Leaderboard
r = requests.get(f"{BASE}/api/leaderboard/top/8")
assert r.status_code == 200
print(f"\nLEADERBOARD:")
for e in r.json()["data"]["topUsers"]:
    print(f"  #{e['rank']} {e['name']:20s} score={e['score']} completed={e['topicsCompleted']}")

# Search history
r = requests.get(f"{BASE}/api/search/recent", headers=h)
assert r.status_code == 200
searches = r.json()["data"]["searches"]
print(f"\nSEARCH HISTORY ({len(searches)}):")
for s in searches:
    print(f"  '{s['query']}' — {s['time']}")

# Dashboard analytics
r = requests.get(f"{BASE}/api/analytics/dashboard", headers=h)
assert r.status_code == 200
ov = r.json()["data"]["analytics"]["overview"]
print(f"\nDASHBOARD: total={ov['totalTopics']} completed={ov['completedTopics']} avg={ov['averageScore']} streak={ov['currentStreak']} hours={ov['totalStudyTime']}")

# Streaks
r = requests.get(f"{BASE}/api/analytics/streaks", headers=h)
assert r.status_code == 200
st = r.json()["data"]["streaks"]
print(f"STREAKS: current={st['currentStreak']} longest={st['longestStreak']} consistency={st['consistency']['consistencyRate']}%")

# Performance
r = requests.get(f"{BASE}/api/analytics/performance", headers=h)
assert r.status_code == 200
perf = r.json()["data"]["performance"]
print(f"\nPERFORMANCE by language:")
for l in perf["byLanguage"]:
    print(f"  {l['language']:12s} avg={l['averageScore']} completed={l['topicsCompleted']}")

# Videos watched
r = requests.get(f"{BASE}/api/videos/watched", headers=h)
assert r.status_code == 200
vids = r.json()["data"]
print(f"\nVIDEOS WATCHED: {vids['totalWatched']}")
for v in vids["watchedVideos"]:
    print(f"  {v['title']} ({v['language']}) — {v['duration']}")

print("\n✅ ALL ENDPOINTS VERIFIED!")
