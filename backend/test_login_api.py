import requests
import json

# Test login
url = "http://localhost:5000/api/auth/login"
payload = {
    "email": "alex@edutwin.com",
    "password": "password123"
}

try:
    response = requests.post(url, json=payload, timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
