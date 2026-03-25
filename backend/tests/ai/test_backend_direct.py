#!/usr/bin/env python
"""Test backend AI endpoints directly"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

# Step 1: Login
print("[1] Login...")
login_resp = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"email": "alex@edutwin.com", "password": "password123"}
)
if login_resp.status_code != 200:
    print(f"Login failed: {login_resp.status_code}")
    exit(1)

token = login_resp.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}
print(f"Token: {token[:30]}...")

# Step 2: Get a topic
print("\n[2] Get first topic...")
resp = requests.get(f"{BASE_URL}/api/topics", headers=headers)
topics = resp.json().get("data", {}).get("topics", [])
if not topics:
    print("No topics found")
    exit(1)

topic_id = topics[0].get("id")
topic_name = topics[0].get("topicName")
print(f"Topic: {topic_name} (ID: {topic_id})")

# Step 3: Test study material
print("\n[3] Testing study material endpoint...")
resp = requests.get(
    f"{BASE_URL}/api/ai/content/study-material/{topic_id}",
    headers=headers
)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"Response: {json.dumps(data, indent=2)[:500]}")
else:
    print(f"Error: {resp.text[:500]}")

# Step 4: Test explanations
print("\n[4] Testing explanations endpoint...")
resp = requests.get(
    f"{BASE_URL}/api/ai/content/explanations/{topic_id}",
    headers=headers,
    params={"styles": "simplified"}
)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"Success: {data.get('success')}")
    explanations = data.get('data', {}).get('explanations', [])
    for exp in explanations:
        print(f"  Style: {exp.get('style')}, Content length: {len(exp.get('content', ''))}")
else:
    print(f"Error: {resp.text[:300]}")

# Step 5: Test quiz
print("\n[5] Testing quiz endpoint...")
resp = requests.get(
    f"{BASE_URL}/api/ai/quiz/quiz/{topic_id}",
    headers=headers,
    params={"question_count": 2}
)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"Success: {data.get('success')}")
    questions = data.get('data', {}).get('questions', [])
    print(f"Questions generated: {len(questions)}")
    if questions:
        print(f"Q1: {questions[0].get('question', '')[:100]}")
else:
    print(f"Error: {resp.text[:300]}")
