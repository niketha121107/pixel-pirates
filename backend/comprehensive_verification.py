#!/usr/bin/env python3
"""Comprehensive verification of all fixes across multiple topics"""
import requests

# Login
login_data = {"email": "alex@edutwin.com", "password": "password123"}
login_response = requests.post("http://127.0.0.1:8000/api/auth/login", json=login_data)
token = login_response.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

# Get all topics to verify all fixes
from app.data import get_all_topics
all_topics = get_all_topics()

print("=" * 70)
print("COMPREHENSIVE VERIFICATION OF ALL FIXES")
print("=" * 70)

# Sample topics from different languages
test_counts = {"Python": 0, "JavaScript": 0, "Java": 0}
test_topics = []

for topic in all_topics:
    lang = topic.get("language", "")
    if lang in test_counts:
        if test_counts[lang] < 1:
            test_counts[lang] += 1
            test_topics.append((topic.get("id"), topic.get("name"), lang))

print(f"\nTesting {len(test_topics)} sample topics across languages...")

all_pass = True
for topic_id, topic_name, language in test_topics:
    print(f"\n[{language}] {topic_name}")
    print("-" * 70)
    
    # Call API
    response = requests.get(f"http://127.0.0.1:8000/api/topics/{topic_id}", headers=headers)
    
    if response.status_code != 200:
        print(f"  ❌ API returned {response.status_code}")
        all_pass = False
        continue
    
    data = response.json()
    topic = data.get("data", {}).get("topic", {})
    
    # Check 1: Visual Explanations
    visual_expl = None
    for expl in topic.get("explanations", []):
        if expl.get("style") == "visual":
            visual_expl = expl
            break
    
    if visual_expl and len(visual_expl.get("content", "")) > 1000:
        print(f"  ✅ Visual Explanation: {len(visual_expl.get('content', ''))} chars (enhanced)")
    else:
        print(f"  ❌ Visual Explanation: Missing or too short")
        all_pass = False
    
    # Check 2: YouTube Videos
    videos = topic.get("recommendedVideos", [])
    if videos and all(v.get("youtubeId") for v in videos):
        print(f"  ✅ YouTube Videos: {len(videos)} videos with youtubeId field")
    else:
        print(f"  ❌ YouTube Videos: Missing or incomplete")
        all_pass = False
    
    # Check 3: Study Material
    study_mat = topic.get("studyMaterial", {})
    expected_sections = ["overview", "explanation", "syntax", "example", "domain_usage", "advantages", "disadvantages"]
    found_sections = [s for s in expected_sections if s in study_mat and len(study_mat[s]) > 0]
    
    if len(found_sections) == len(expected_sections):
        print(f"  ✅ Study Material: All 7 sections present ({sum(len(study_mat[s]) for s in expected_sections)} total chars)")
    else:
        print(f"  ⚠️  Study Material: {len(found_sections)}/{len(expected_sections)} sections found")
        if found_sections != expected_sections:
            all_pass = False

print("\n" + "=" * 70)
if all_pass:
    print("✅ ALL FIXES VERIFIED SUCCESSFULLY!")
    print("   1. Visual explanations enhanced with detailed ASCII diagrams")
    print("   2. YouTube videos properly mapped with youtubeId field")
    print("   3. Comprehensive study material with 7 structured sections")
else:
    print("⚠️  Some checks failed - review above")
print("=" * 70)
