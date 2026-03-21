#!/usr/bin/env python
"""Test the topics API to see what data it returns"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

# First, get a token by logging in
print("1. Logging in...")
resp = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "test@example.com",
    "password": "test123"
})

if resp.status_code == 200:
    data = resp.json()
    token = data.get("data", {}).get("access_token", "")
    print(f"   ✓ Got token: {token[:20]}...")
else:
    print(f"   ✗ Login failed: {resp.status_code}")
    print(f"   Response: {resp.text}")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# Get all topics to find a topic ID
print("\n2. Getting topics list...")
resp = requests.get(f"{BASE_URL}/topics", headers=headers)
if resp.status_code != 200:
    print(f"   ✗ Failed to get topics: {resp.status_code}")
    print(f"   Response: {resp.text}")
    exit(1)

topics = resp.json().get("data", {}).get("topics", [])
print(f"   ✓ Got {len(topics)} topics")

if not topics:
    print("   ✗ No topics found!")
    exit(1)

# Pick the first topic
topic_summary = topics[0]
print(f"\n3. Sample topic from list:")
print(f"   ID: {topic_summary.get('id')}")
print(f"   topicName: {topic_summary.get('topicName')}")
print(f"   Language: {topic_summary.get('language')}")

# Now get the detailed topic
topic_id = topic_summary.get("id")
print(f"\n4. Getting detailed topic data for {topic_id}...")
resp = requests.get(f"{BASE_URL}/topics/{topic_id}", headers=headers)

if resp.status_code != 200:
    print(f"   ✗ Failed: {resp.status_code}")
    print(f"   Response: {resp.text}")
    exit(1)

topic_detail = resp.json().get("data", {}).get("topic", {})

print("\n5. DETAILED TOPIC DATA:")
print(f"   topicName: {topic_detail.get('topicName')}")
print(f"   language: {topic_detail.get('language')}")
print(f"   difficulty: {topic_detail.get('difficulty')}")
print(f"   overview: {topic_detail.get('overview', '')[:100]}...")

# Check explanations
explanations = topic_detail.get("explanations", [])
print(f"\n6. EXPLANATIONS ({len(explanations)} total):")
if explanations:
    for exp in explanations:
        print(f"   - {exp.get('style')}: {len(exp.get('content', ''))} chars")
else:
    print("   ✗ NO EXPLANATIONS!")

# Check videos
videos = topic_detail.get("recommendedVideos", [])
print(f"\n7. VIDEOS ({len(videos)} total):")
if videos:
    for vid in videos[:3]:
        print(f"   - {vid.get('title', 'N/A')}")
        print(f"     youtubeId: {vid.get('youtubeId', 'N/A')}")
else:
    print("   ✗ NO VIDEOS!")

# Check study material
study_material = topic_detail.get("studyMaterial", {})
print(f"\n8. STUDY MATERIAL:")
if study_material and study_material.get("notes"):
    notes = study_material.get("notes", "")
    print(f"   ✓ Present: {len(notes)} chars")
    print(f"     First 100 chars: {notes[:100]}...")
else:
    print("   ✗ NO STUDY MATERIAL!")

print("\n✅ RESPONSE SUMMARY:")
print(f"   Explanations: {len(explanations)}")
for exp in explanations:
    has_content = bool(exp.get('content'))
    print(f"     - {exp.get('style')}: {'✓' if has_content else '✗'}")
print(f"   Videos: {len(videos)}")
print(f"   Study Material: {'✓' if study_material.get('notes') else '✗'}")
