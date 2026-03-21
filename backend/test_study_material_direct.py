import requests
from pymongo import MongoClient
from app.core.config import Settings

# Direct database check first
settings = Settings()
client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
db = client[settings.MONGODB_DATABASE]

# Check one topic 
topic = db.topics.find_one({})
if topic:
    study_material = topic.get("study_material", {})
    print("\n=== DATABASE VERIFICATION ===")
    print("Study Material Exists:", "YES" if study_material else "NO")
    
    if study_material and isinstance(study_material, dict):
        print("\nSections found in database:")
        for section in ['overview', 'explanation', 'syntax', 'example', 'domain_usage', 'advantages', 'disadvantages']:
            content = study_material.get(section, '')
            chars = len(str(content))
            if content:
                print(f"  [OK] {section}: {chars} chars")
            else:
                print(f"  [MISSING] {section}")
                
        print(f"\nSample Overview (first 150 chars):")
        print(study_material.get('overview', '')[:150])

client.close()

# Now test API
print("\n" + "="*70)
print("=== API TEST ===")

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
TOPICS_URL = f"{BASE_URL}/api/topics"

credentials = {
    "email": "alex@edutwin.com",
    "password": "password123"
}

try:
    # Login
    print("\n[1] Logging in...")
    login_resp = requests.post(LOGIN_URL, json=credentials, timeout=5)
    
    if login_resp.status_code != 200:
        print("[ERROR] Login failed:", login_resp.status_code)
    else:
        token_data = login_resp.json()
        token = token_data.get("access_token")
        print("[OK] Login successful")
        
        # Get topics list
        print("\n[2] Getting topics list...")
        headers = {"Authorization": f"Bearer {token}"}
        all_topics_resp = requests.get(TOPICS_URL, headers=headers, timeout=5)
        
        if all_topics_resp.status_code != 200:
            print("[ERROR] Failed to get topics:", all_topics_resp.status_code)
        else:
            topics_list = all_topics_resp.json().get("data", {}).get("topics", [])
            first_topic_id = topics_list[0].get("id") if topics_list else None
            first_topic_name = topics_list[0].get("topicName") if topics_list else None
            
            print(f"[OK] Found {len(topics_list)} topics")
            print(f"[OK] First topic: {first_topic_name} (ID: {first_topic_id})")
            
            # Get topic detail
            if first_topic_id:
                print(f"\n[3] Getting topic details for {first_topic_id}...")
                detail_resp = requests.get(f"{TOPICS_URL}/{first_topic_id}", headers=headers, timeout=5)
                
                if detail_resp.status_code != 200:
                    print("[ERROR] Failed to get topic detail:", detail_resp.status_code)
                else:
                    response_json = detail_resp.json()
                    topic_data = response_json.get("data", {}).get("topic") or response_json.get("data", {})
                    
                    if topic_data:
                        print("[OK] Got topic details")
                        print(f"  Topic Name: {topic_data.get('topicName')}")
                        print(f"  Language: {topic_data.get('language')}")
                        print(f"  Difficulty: {topic_data.get('difficulty')}")
                        
                        # Check study material
                        study_material = topic_data.get('studyMaterial', {})
                        if study_material:
                            print(f"\n[OK] Study Material FOUND in API response!")
                            sections_found = []
                            for section in ['overview', 'explanation', 'syntax', 'example', 'domain_usage', 'advantages', 'disadvantages']:
                                content = study_material.get(section, '')
                                if content:
                                    chars = len(str(content))
                                    sections_found.append(section)
                                    print(f"  [OK] {section}: {chars} chars")
                                else:
                                    print(f"  [MISSING] {section}")
                            
                            print(f"\nTotal sections found: {len(sections_found)}/7")
                            
                            # Show sample content
                            print(f"\n--- Sample: Overview (first 200 chars) ---")
                            overview = study_material.get('overview', '')
                            print(overview[:200])
                        else:
                            print(f"\n[ERROR] Study Material NOT in API response")
                            print(f"Available keys in topic_data: {list(topic_data.keys())}")
                    else:
                        print("[ERROR] No topic data in response")
                        print(f"Response: {response_json}")

except requests.exceptions.ConnectionError:
    print("[ERROR] Cannot connect to backend on port 8000")
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
