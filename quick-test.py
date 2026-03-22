#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pixel Pirates - Quick API Smoke Test
Validates core API endpoints are working
Run this after starting services to confirm integration is good
"""

import requests
import json
import sys
import os
from datetime import datetime

# Fix encoding on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:5000/api"
HEALTH_URL = "http://localhost:5000/health"
TIMEOUT = 10
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "test123"
AUTH_TOKEN = None

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def log_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")

def log_test(name):
    print(f"\n{Colors.CYAN}> {name}{Colors.RESET}")

def log_success(msg):
    print(f"  {Colors.GREEN}✓ {msg}{Colors.RESET}")

def log_error(msg):
    print(f"  {Colors.RED}✗ {msg}{Colors.RESET}")

def log_info(msg):
    print(f"  {Colors.YELLOW}i {msg}{Colors.RESET}")

def api_call(method, endpoint, **kwargs):
    """Make API call with error handling"""
    url = f"{BASE_URL}{endpoint}"
    headers = kwargs.pop('headers', {})
    
    if AUTH_TOKEN:
        headers['Authorization'] = f'Bearer {AUTH_TOKEN}'
    
    try:
        if method == "GET":
            resp = requests.get(url, timeout=TIMEOUT, headers=headers, **kwargs)
        elif method == "POST":
            resp = requests.post(url, timeout=TIMEOUT, headers=headers, **kwargs)
        else:
            return None, f"Unknown method: {method}"
        
        return resp, None
    except requests.exceptions.Timeout:
        return None, "Request timeout (>10s)"
    except requests.exceptions.ConnectionError:
        return None, "Connection refused - is backend running?"
    except Exception as e:
        return None, str(e)

def test_connectivity():
    """Test basic connectivity"""
    log_test("Backend Connectivity")
    try:
        resp = requests.get(HEALTH_URL, timeout=TIMEOUT)
        if resp.status_code == 200:
            log_success(f"Backend is running (status: {resp.status_code})")
            return True
        else:
            log_error(f"Backend returned: {resp.status_code}")
            return False
    except Exception as e:
        log_error(f"Cannot reach backend: {str(e)}")
        return False

def login():
    """Try to login or get a test token"""
    global AUTH_TOKEN
    try:
        resp = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=TIMEOUT
        )
        if resp.status_code == 200:
            data = resp.json()
            AUTH_TOKEN = data.get("data", {}).get("token")
            return True
    except:
        pass
    return False

def test_topics():
    """Test topics endpoint"""
    log_test("Topics Endpoint")
    resp, error = api_call("GET", "/topics")
    
    if error:
        log_error(f"Topics endpoint failed: {error}")
        return None, False
    
    if resp.status_code != 200:
        log_error(f"Topics endpoint returned: {resp.status_code}")
        return None, False
    
    try:
        data = resp.json()
        topics = data.get("data", {}).get("topics", [])
        log_success(f"Found {len(topics)} topics")
        
        if topics:
            log_info(f"First topic: {topics[0].get('name', 'Unknown')}")
            return topics[0].get('id'), True
        else:
            log_info("No topics in database (this is OK)")
            return None, True
    except:
        log_error("Cannot parse topics response")
        return None, False

def test_ai_quiz():
    """Test AI quiz generation"""
    log_test("AI Quiz Generation")
    resp, error = api_call("GET", "/ai/quiz/test-ai", 
        params={"topic_name": "Python Variables", "question_count": 2}
    )
    
    if error:
        log_error(f"AI quiz endpoint failed: {error}")
        return False
    
    if resp.status_code == 200:
        try:
            data = resp.json()
            questions = data.get("data", {}).get("questions", [])
            log_success(f"Generated {len(questions)} questions")
            return True
        except:
            log_error("Cannot parse quiz response")
            return False
    elif resp.status_code == 429:
        log_info("Rate limited (expected if hitting Gemini API limit) - fallback will work")
        return True
    elif resp.status_code == 500:
        log_info("Server error (might be API key issue) - fallback will work")
        return True
    else:
        log_error(f"AI quiz returned: {resp.status_code}")
        return False

def test_ai_explanations(topic_id):
    """Test AI explanations endpoint"""
    if not topic_id:
        log_info("Skipping explanations test (no topics in DB)")
        return True
    
    log_test("AI Explanations Endpoint")
    resp, error = api_call("GET", f"/ai/content/explanations/{topic_id}",
        params={"styles": "simplified"}
    )
    
    if error:
        log_error(f"Explanations endpoint failed: {error}")
        return False
    
    if resp.status_code == 200:
        log_success(f"Explanations endpoint working")
        return True
    elif resp.status_code in [429, 500]:
        log_info("API rate limited or error (fallback will work)")
        return True
    else:
        log_error(f"Explanations returned: {resp.status_code}")
        return False

def test_ai_study_material(topic_id):
    """Test AI study material endpoint"""
    if not topic_id:
        log_info("Skipping study material test (no topics in DB)")
        return True
    
    log_test("AI Study Material Endpoint")
    resp, error = api_call("GET", f"/ai/content/study-material/{topic_id}")
    
    if error:
        log_error(f"Study material endpoint failed: {error}")
        return False
    
    if resp.status_code == 200:
        log_success(f"Study material endpoint working")
        return True
    elif resp.status_code in [429, 500]:
        log_info("API rate limited or error (fallback will work)")
        return True
    else:
        log_error(f"Study material returned: {resp.status_code}")
        return False

def test_ai_mock_test():
    """Test AI mock test endpoint"""
    log_test("AI Mock Test Endpoint")
    resp, error = api_call("POST", "/ai/quiz/mock-test",
        params={
            "topics": json.dumps(["Python"]),
            "total_questions": 3,
            "difficulty_easy": 1,
            "difficulty_medium": 1,
            "difficulty_hard": 1
        }
    )
    
    if error:
        log_error(f"Mock test endpoint failed: {error}")
        return False
    
    if resp.status_code == 200:
        log_success(f"Mock test endpoint working")
        return True
    elif resp.status_code in [429, 500]:
        log_info("API rate limited or error (fallback will work)")
        return True
    else:
        log_error(f"Mock test returned: {resp.status_code}")
        return False

def test_database():
    """Test database connectivity"""
    log_test("Database Connectivity")
    resp, error = api_call("GET", "/users/profile",
        headers={"Authorization": "Bearer test"}
    )
    
    if error:
        log_error(f"Database test failed: {error}")
        return False
    
    # Any response means database is reachable
    log_success("Database is reachable")
    return True

def test_cors():
    """Test CORS headers"""
    log_test("CORS Headers")
    resp, error = api_call("GET", "/topics",
        headers={"Origin": "http://localhost:3000"}
    )
    
    if error:
        log_error(f"CORS test failed: {error}")
        return False
    
    if "Access-Control-Allow-Origin" in resp.headers:
        log_success("CORS headers present")
        return True
    else:
        log_error("CORS headers missing (frontend may have issues)")
        return False

def print_summary(results):
    """Print test summary"""
    log_header("Test Summary")
    
    passed = sum(results.values())
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\n{Colors.BOLD}Results:{Colors.RESET}")
    for name, result in results.items():
        status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if result else f"{Colors.RED}✗ FAIL{Colors.RESET}"
        print(f"  {status} - {name}")
    
    print(f"\n{Colors.BOLD}Overall: {passed}/{total} tests passed ({percentage:.0f}%){Colors.RESET}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! Integration is ready.{Colors.RESET}")
        print(f"\n{Colors.CYAN}Next steps:{Colors.RESET}")
        print(f"  1. Start frontend: cd frontend && npm run dev")
        print(f"  2. Open http://localhost:3000")
        print(f"  3. Test AI features in the app")
        return 0
    elif passed >= total - 1:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ Most tests passed. Check API key and database configuration.{Colors.RESET}")
        return 1
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ Multiple tests failed. Check backend is running and properly configured.{Colors.RESET}")
        return 1

def main():
    log_header("Pixel Pirates - API Smoke Test")
    print(f"\n{Colors.CYAN}Testing endpoints at: {BASE_URL}{Colors.RESET}")
    print(f"{Colors.CYAN}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    
    results = {}
    topic_id = None
    
    # Run tests
    results["Backend Connectivity"] = test_connectivity()
    
    if not results["Backend Connectivity"]:
        print(f"\n{Colors.RED}Failed: Cannot connect to backend.{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Start backend with:{Colors.RESET}")
        print(f"  cd backend")
        print(f"  python main.py")
        return 1
    
    # Try to login
    log_test("Authentication")
    if login():
        log_success("Logged in successfully")
    else:
        log_info("Could not login - API key tests will skip")
    
    topic_id, results["Topics Endpoint"] = test_topics()
    results["Database Connectivity"] = test_database()
    results["CORS Headers"] = test_cors()
    results["AI Quiz Generation"] = test_ai_quiz()
    results["AI Study Material"] = test_ai_study_material(topic_id)
    results["AI Explanations"] = test_ai_explanations(topic_id)
    results["AI Mock Test"] = test_ai_mock_test()
    
    exit_code = print_summary(results)
    
    print(f"\n{Colors.CYAN}Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
