import requests
import json

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
TOPICS_URL = f"{BASE_URL}/api/topics"

credentials = {
    "email": "alex@edutwin.com",
    "password": "password123"
}

try:
    print("[1] Logging in...")
    login_resp = requests.post(LOGIN_URL, json=credentials, timeout=5)
    token_data = login_resp.json()
    token = token_data.get("access_token")
    print("[OK] Login successful\n")
    
    # Get first topic
    print("[2] Getting first topic...")
    headers = {"Authorization": f"Bearer {token}"}
    all_topics_resp = requests.get(TOPICS_URL, headers=headers, timeout=5)
    topics_list = all_topics_resp.json().get("data", {}).get("topics", [])
    first_topic_id = topics_list[0].get("id")
    first_topic_name = topics_list[0].get("topicName")
    
    print(f"[OK] Found first topic: {first_topic_name}\n")
    
    # Get topic detail with new field mapping
    print("[3] Getting topic details...")
    detail_resp = requests.get(f"{TOPICS_URL}/{first_topic_id}", headers=headers, timeout=5)
    response_json = detail_resp.json()
    topic_data = response_json.get("data", {}).get("topic") or response_json.get("data", {})
    
    if topic_data:
        print("[OK] Got topic details\n")
        
        study_material = topic_data.get('studyMaterial', {})
        if study_material:
            print("[OK] Study Material in API Response!")
            print("\nField names being returned:")
            for key in study_material.keys():
                value = study_material.get(key)
                if isinstance(value, list):
                    print(f"  - {key}: [{len(value)} items]")
                elif isinstance(value, dict):
                    print(f"  - {key}: {{...}}")
                else:
                    chars = len(str(value))
                    print(f"  - {key}: {chars} chars")
            
            print("\n=== VERIFYING FRONTEND EXPECTS THESE FIELDS ===")
            expected = ['title', 'overview', 'explanation', 'syntax', 'codeExample', 'implementation', 'advantages', 'disadvantages', 'keyPoints']
            print("\nExpected by frontend:")
            for field in expected:
                if field in study_material:
                    value = study_material.get(field)
                    if isinstance(value, list):
                        status = f"[OK] {len(value)} items"
                    else:
                        status = f"[OK] {len(str(value)) if value else 0} chars"
                    print(f"  [YES] {field}: {status}")
                else:
                    print(f"  [MISSING] {field}")
            
            print("\n=== SAMPLE CONTENT ===")
            print(f"\nTitle: {study_material.get('title', '')}")
            print(f"\nOverview (first 150 chars):")
            print(study_material.get('overview', '')[:150])
            print(f"\nImplementation array (first 3 items):")
            impl = study_material.get('implementation', [])
            for i, item in enumerate(impl[:3]):
                print(f"  {i+1}. {item[:80]}...")
            print(f"\nAdvantages array (first 3 items):")
            advs = study_material.get('advantages', [])
            for i, item in enumerate(advs[:3]):
                print(f"  {i+1}. {item[:80]}...")
        else:
            print("[ERROR] Study Material NOT returned from API")
    else:
        print("[ERROR] No topic data in response")

except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
