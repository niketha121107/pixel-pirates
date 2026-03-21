import requests
import json

# Test API endpoint to see if study material is returned
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
TOPICS_URL = f"{BASE_URL}/api/topics"

# Test credentials (from your existing data)
credentials = {
    "email": "alex@edutwin.com",
    "password": "password123"
}

try:
    # Login first to get token
    print("🔐 Logging in...")
    login_resp = requests.post(LOGIN_URL, json=credentials, timeout=5)
    
    print(f"Login response status: {login_resp.status_code}")
    print(f"Login response: {login_resp.json()}")
    
    if login_resp.status_code != 200:
        print(f"❌ Login failed: {login_resp.status_code}")
    else:
        resp_data = login_resp.json()
        # Try different response formats
        token = resp_data.get("token") or resp_data.get("data", {}).get("token") or resp_data.get("access_token")
        
        if not token:
            print(f"❌ No token found in response: {resp_data}")
        else:
            print(f"✓ Logged in successfully, token: {token[:20]}...")
        
        # Get first topic to check study material
        print("\n📚 Fetching first topic...")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get all topics first to find a topic_id
        all_topics_resp = requests.get(TOPICS_URL, headers=headers, timeout=5)
        if all_topics_resp.status_code == 200:
            topics_list = all_topics_resp.json().get("data", {}).get("topics", [])
            if topics_list:
                first_topic_id = topics_list[0].get("id")
                print(f"✓ Found first topic: {topics_list[0].get('topicName')} (ID: {first_topic_id})")
                
                # Get detailed topic
                detail_resp = requests.get(f"{TOPICS_URL}/{first_topic_id}", headers=headers, timeout=5)
                if detail_resp.status_code == 200:
                    full_response = detail_resp.json()
                    response_data = full_response.get("data", {})
                    
                    # Extract topic from data
                    topic_data = response_data.get("topic") if isinstance(response_data, dict) and "topic" in response_data else response_data
                    
                    if topic_data:
                        print("\n=== TOPIC DETAILS ===")
                        print(f"Topic: {topic_data.get('topicName')}")
                        print(f"Language: {topic_data.get('language')}")
                        print(f"Difficulty: {topic_data.get('difficulty')}")
                    
                    # Check study material
                    study_material = topic_data.get('studyMaterial', {})
                    if study_material:
                        print(f"\n✓ Study Material Found! Sections:")
                        for section in ['overview', 'explanation', 'syntax', 'example', 'domain_usage', 'advantages', 'disadvantages']:
                            content = study_material.get(section, '')
                            chars = len(str(content))
                            if content:
                                preview = str(content)[:60] + "..." if len(str(content)) > 60 else str(content)
                                print(f"  ✓ {section}: {chars} chars - {preview}")
                            else:
                                print(f"  ✗ {section}: MISSING")
                    else:
                        print(f"\n✗ Study Material NOT returned from API")
                else:
                    print(f"❌ Failed to get topic details: {detail_resp.status_code}")
        else:
            print(f"❌ Failed to get topics list: {all_topics_resp.status_code}")
            print(all_topics_resp.text)

except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to backend on port 8000")
    print("Make sure the backend is running: python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
except Exception as e:
    print(f"❌ Error: {e}")
