"""
Comprehensive API Endpoint Testing Script
Tests all endpoints with proper request/response validation
"""

import requests
import json
import sys

BASE = "http://localhost:8000"
TOKEN = None
PASS = 0
FAIL = 0
RESULTS = []

def log(method, path, status, ok, note=""):
    global PASS, FAIL
    icon = "PASS" if ok else "FAIL"
    if ok:
        PASS += 1
    else:
        FAIL += 1
    RESULTS.append((icon, method, path, status, note))
    print(f"  [{icon}] {method:6s} {path:40s} -> {status} {note}")

def get(path, headers=None, params=None, expect=200):
    try:
        r = requests.get(f"{BASE}{path}", headers=headers, params=params, timeout=30)
        ok = r.status_code == expect
        body = r.json() if r.headers.get("content-type","").startswith("application/json") else {}
        log("GET", path, r.status_code, ok, json.dumps(body)[:120] if not ok else "")
        return r, body
    except Exception as e:
        log("GET", path, 0, False, str(e)[:120])
        return None, {}

def post(path, data=None, headers=None, expect=200):
    try:
        r = requests.post(f"{BASE}{path}", json=data, headers=headers, timeout=30)
        ok = r.status_code == expect
        body = r.json() if r.headers.get("content-type","").startswith("application/json") else {}
        log("POST", path, r.status_code, ok, json.dumps(body)[:120] if not ok else "")
        return r, body
    except Exception as e:
        log("POST", path, 0, False, str(e)[:120])
        return None, {}

def put(path, data=None, headers=None, expect=200):
    try:
        r = requests.put(f"{BASE}{path}", json=data, headers=headers, timeout=30)
        ok = r.status_code == expect
        body = r.json() if r.headers.get("content-type","").startswith("application/json") else {}
        log("PUT", path, r.status_code, ok, json.dumps(body)[:120] if not ok else "")
        return r, body
    except Exception as e:
        log("PUT", path, 0, False, str(e)[:120])
        return None, {}

def delete(path, headers=None, expect=200):
    try:
        r = requests.delete(f"{BASE}{path}", headers=headers, timeout=30)
        ok = r.status_code == expect
        body = r.json() if r.headers.get("content-type","").startswith("application/json") else {}
        log("DELETE", path, r.status_code, ok, json.dumps(body)[:120] if not ok else "")
        return r, body
    except Exception as e:
        log("DELETE", path, 0, False, str(e)[:120])
        return None, {}

def auth_header():
    return {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

# ═══════════════════════════════════════════════
print("=" * 70)
print("  PIXEL PIRATES API - COMPREHENSIVE ENDPOINT TEST")
print("=" * 70)

# ──── ROOT / HEALTH ────
print("\n[1] ROOT & HEALTH ENDPOINTS")
get("/")
get("/api")
get("/health")

# ──── DATABASE ────
print("\n[2] DATABASE ENDPOINTS")
get("/api/database/health")
get("/api/database/test-connection")

# ──── AUTH: SIGNUP ────
print("\n[3] AUTH ENDPOINTS")
import random, string
rand_email = f"test_{''.join(random.choices(string.ascii_lowercase, k=6))}@pixelpirates.com"
r, body = post("/api/auth/signup", {
    "name": "Test User",
    "email": rand_email,
    "password": "testpass123"
})
if body.get("access_token"):
    TOKEN = body["access_token"]
    print(f"       -> Got token: {TOKEN[:30]}...")
else:
    # user might already exist, try login
    print("       -> Signup may have returned conflict, trying login...")

# ──── AUTH: LOGIN ────
r, body = post("/api/auth/login", {
    "email": "alex@edutwin.com",
    "password": "password123"
})
if body.get("access_token"):
    TOKEN = body["access_token"]
    print(f"       -> Got token: {TOKEN[:30]}...")
else:
    print(f"       -> Login response: {json.dumps(body)[:200]}")

# ──── AUTH: LOGIN (wrong password) ────
post("/api/auth/login", {
    "email": "alex@edutwin.com",
    "password": "wrongpassword"
}, expect=401)

# ──── AUTH: ME ────
get("/api/auth/me", headers=auth_header())

# ──── AUTH: REFRESH ────
post("/api/auth/refresh", headers=auth_header())

# ──── AUTH: LOGOUT ────
post("/api/auth/logout", headers=auth_header())

# ──── AUTH: No token (should 401 or 403) ────
get("/api/auth/me", expect=401)

# ──── USERS ────
print("\n[4] USER ENDPOINTS")
get("/api/users/profile", headers=auth_header())
put("/api/users/profile", {"name": "Alex Updated"}, headers=auth_header())
get("/api/users/stats", headers=auth_header())
get("/api/users/user-1/analytics")

# ──── TOPICS ────
print("\n[5] TOPICS ENDPOINTS")
get("/api/topics", headers=auth_header())
get("/api/topics?language=Python", headers=auth_header())
get("/api/topics/topic-1", headers=auth_header())
get("/api/topics/topic-2", headers=auth_header())
get("/api/topics/nonexistent", headers=auth_header(), expect=404)
get("/api/topics/topic-1/explanation", headers=auth_header())
get("/api/topics/topic-1/explanation?style=simplified", headers=auth_header())
get("/api/topics/topic-1/quiz")

# ──── TOPIC STATUS UPDATE ────
put("/api/topics/topic-2/status", {
    "topic_id": "topic-2",
    "status": "in-progress"
}, headers=auth_header())

# ──── QUIZ ────
print("\n[6] QUIZ ENDPOINTS")
post("/api/quiz/submit", {
    "topic_id": "topic-1",
    "answers": [
        {"question_id": "q1", "selected_answer": 0},
        {"question_id": "q2", "selected_answer": 2}
    ],
    "time_taken": 120
}, headers=auth_header())

# Quiz adaptive
post("/api/quiz/adaptive?topic_id=topic-1&question_count=5", headers=auth_header())

# Quiz mock test
post("/api/quiz/mock-test", {
    "topics": ["Python Loops", "Java OOP"],
    "difficulty_mix": {"Beginner": 5, "Intermediate": 3, "Advanced": 2},
    "total_questions": 10
}, headers=auth_header())

# Quiz results
get("/api/quiz/results/topic-1", headers=auth_header())

# Performance analysis
get("/api/quiz/performance-analysis", headers=auth_header())

# ──── VIDEOS ────
print("\n[7] VIDEO ENDPOINTS")
get("/api/videos/search?q=python+loops", headers=auth_header())
get("/api/videos/recommendations", headers=auth_header())
get("/api/videos/watched", headers=auth_header())

# Mark video watched
post("/api/videos/watch", {
    "video_id": "vid-test-1",
    "youtube_id": "dQw4w9WgXcQ",
    "title": "Test Video",
    "duration": "10:00",
    "time_watched": "5:00",
    "language": "Python"
}, headers=auth_header())

# Trending videos
get("/api/videos/trending/Python")

# ──── LEADERBOARD ────
print("\n[8] LEADERBOARD ENDPOINTS")
get("/api/leaderboard", headers=auth_header())
get("/api/leaderboard/top/5")
get("/api/leaderboard/user-rank", headers=auth_header())
get("/api/leaderboard/language/Python")

# ──── ANALYTICS ────
print("\n[9] ANALYTICS ENDPOINTS")
get("/api/analytics/dashboard", headers=auth_header())
get("/api/analytics/progress?period=7d", headers=auth_header())
get("/api/analytics/performance", headers=auth_header())
get("/api/analytics/streaks", headers=auth_header())

# ──── SEARCH ────
print("\n[10] SEARCH ENDPOINTS")
get("/api/search/suggestions?q=python")
get("/api/search/global?q=python")
get("/api/search/global?q=loops&category=topics")
get("/api/search/trending")
get("/api/search/recent", headers=auth_header())
post("/api/search", {"query": "python loops test"}, headers=auth_header())
delete("/api/search/recent", headers=auth_header())

# ═══════════════════════════════════════════════
print("\n" + "=" * 70)
print(f"  RESULTS: {PASS} PASSED | {FAIL} FAILED | {PASS + FAIL} TOTAL")
print("=" * 70)

if FAIL > 0:
    print("\n  FAILED ENDPOINTS:")
    for icon, method, path, status_code, note in RESULTS:
        if icon == "FAIL":
            print(f"    {method:6s} {path:40s} -> {status_code}  {note}")

print()
