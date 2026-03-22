# AI Integration Tests - Quick Reference

## ✅ New Test Locations

All AI integration tests have been moved to `tests/ai/` directory for better organization.

---

## Running Tests

### From Backend Root Directory

```bash
cd backend
```

### Run All AI Tests

```bash
# Option 1: Run individual test file (recommended for debugging)
python tests/ai/test_ai_integration.py

# Option 2: Use pytest (requires: pip install pytest)
pytest tests/ai/ -v
```

### Run Specific Tests

```bash
# Full end-to-end integration test
python tests/ai/test_ai_integration.py

# Debug quiz JSON responses
python tests/ai/test_quiz_debug.py

# Debug explanation generation
python tests/ai/test_explanation_debug.py

# Test service layer directly
python tests/ai/test_service_direct.py

# Test backend endpoints directly
python tests/ai/test_backend_direct.py
```

---

## Test Descriptions

| Test File | Purpose | Run When |
|-----------|---------|----------|
| `test_ai_integration.py` | Full end-to-end test of all AI endpoints | Before deployment, after changes |
| `test_quiz_debug.py` | Debug Gemini's quiz response format | Quiz generation issues |
| `test_explanation_debug.py` | Debug Gemini's explanation format | Explanation generation issues |
| `test_service_direct.py` | Test AIContentGenerator service directly | Service-level debugging |
| `test_backend_direct.py` | Test backend endpoints directly | Route/endpoint debugging |

---

## Complete Test Workflow

### 1. Verify API Key Setup
```bash
python scripts/verify_gemini_key.py
```
Expected output: `VERIFICATION PASSED - API is working!`

### 2. Run Service Tests
```bash
python tests/ai/test_service_direct.py
```
Expected: Service methods return data without HTTP errors

### 3. Run Backend Tests
```bash
python tests/ai/test_backend_direct.py
```
Expected: All endpoints respond with correct status codes

### 4. Run Full Integration Test
```bash
python tests/ai/test_ai_integration.py
```
Expected: All 8 steps complete successfully

### 5. Check Specific Features
```bash
# Quiz generation
python tests/ai/test_quiz_debug.py

# Explanations
python tests/ai/test_explanation_debug.py
```

---

## Test Requirements

### Before Running Tests

1. **Backend must be running**
   ```bash
   # In separate terminal
   cd backend
   python main.py
   ```

2. **API key must be configured**
   - Check `.env` file has `GEMINI_API_KEY`
   - Verify with: `python scripts/verify_gemini_key.py`

3. **Database must have topics**
   - Run: `python seed_database.py` (if needed)

### Dependencies

All required in `requirements.txt`:
- `requests` - HTTP client
- `httpx` - Async HTTP client
- `python-dotenv` - Environment variables
- `fastapi` - Web framework
- `motor` - MongoDB async driver

Install with:
```bash
pip install -r requirements.txt
```

---

## Expected Test Outputs

### ✅ Successful Run

```
================================================================================
AI INTEGRATION END-TO-END TEST
================================================================================

[1] Authentication
   [OK] Logged in successfully
   Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

[2] Test AI Quiz Generation (No Auth)
   [OK] AI generation working!
   Topic: Python Variables
   Questions generated: 2
   Sample question: What does a Python variable do?...

[3] Get Topics
   [OK] Found 200 topics
   Using topic: Python Basics

[4] AI Study Material for Python Basics
   [OK] Study material generated!
   Overview: Variables are containers for storing data...
   Has explanation: True
   Has code example: True

[5] AI Explanations for Python Basics
   [OK] Generated 4 explanations
      - simplified: 145 chars
      - logical: 182 chars
      - visual: 198 chars
      - analogy: 167 chars

[6] AI Quiz for Python Basics
   [OK] Generated 3 quiz questions
      Q1: What is a variable in Python?...
      Options: 4 choices
      Difficulty: easy

[7] AI Mock Test
   [OK] Generated mock test with 5 questions
      Test title: Python Basics Mock Test
      Estimated time: 15 minutes

[8] Full AI Content Package for Python Basics
   [OK] Complete content package generated!
      Study material: OK
      Explanations: OK (4 styles)
      Quiz: OK (4 questions)

================================================================================
TEST SUMMARY
================================================================================
Status: All endpoints responding

Available AI Endpoints:
  - GET /api/ai/quiz/test-ai - Test AI generation
  - GET /api/ai/quiz/quiz/{topic_id} - Generate quiz questions
  - GET /api/ai/quiz/generate-adaptive - Adaptive quiz
  - POST /api/ai/quiz/mock-test - Full mock test
  - GET /api/ai/content/study-material/{topic_id} - Study materials
  - GET /api/ai/content/explanations/{topic_id} - Multi-style explanations
  - GET /api/ai/content/full-content/{topic_id} - Complete content package

Status: READY FOR DEPLOYMENT
================================================================================
```

### ⚠️ Rate Limited (Expected)

```
Status: 429
Error: Too many requests

This is expected on free tier. Wait 2-5 minutes and retry.
```

### ❌ Common Errors

**Error**: `Login failed: 401`
- **Fix**: Check database has user with email `alex@edutwin.com`

**Error**: `No module named 'app'`
- **Fix**: Run from `backend/` directory: `cd backend && python tests/ai/test_*.py`

**Error**: `GEMINI_API_KEY not found`
- **Fix**: Update `.env` file with valid API key

---

## Debugging Guide

### Test Fails at Step 2
```bash
# Debug quiz generation directly
python tests/ai/test_quiz_debug.py

# Check service layer
python tests/ai/test_service_direct.py
```

### Test Fails at Step 4
```bash
# Debug explanations
python tests/ai/test_explanation_debug.py

# Check if service is responding
python tests/ai/test_backend_direct.py
```

### API Key Issues
```bash
# Verify setup
python scripts/verify_gemini_key.py

# Output should be:
# [OK] API Key found: AIzaSyBEd2lFjAW1oiv...
# [TEST] Connecting to Gemini API...
# [OK] Response: Pixel Pirates AI is working!
# VERIFICATION PASSED - API is working!
```

---

## File Locations Reference

```
backend/
├── tests/ai/
│   ├── test_ai_integration.py        ← Main test
│   ├── test_quiz_debug.py            ← Quiz debugging
│   ├── test_explanation_debug.py     ← Explanation debugging
│   ├── test_service_direct.py        ← Service testing
│   └── test_backend_direct.py        ← Endpoint testing
│
├── scripts/
│   └── verify_gemini_key.py          ← Verify setup
│
└── main.py                            ← Start backend
```

---

## Running Tests from IDEs

### VS Code

1. Open terminal in VS Code: `Ctrl + ~`
2. Navigate: `cd backend`
3. Run: `python tests/ai/test_ai_integration.py`

### PyCharm

1. Right-click test file: `tests/ai/test_ai_integration.py`
2. Select: "Run"
3. Watch output in Run panel

### Command Line

```bash
cd backend
python tests/ai/test_ai_integration.py
```

---

## Continuous Integration (CI/CD)

### Run Tests Automatically

```yaml
# .github/workflows/test-ai.yml
name: AI Integration Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r backend/requirements.txt
      - run: cd backend && python tests/ai/test_service_direct.py
```

---

## Summary

✅ **Tests organized by purpose in `tests/ai/`**
✅ **Quick reference for running each test**
✅ **Clear expected outputs**
✅ **Debugging guidance for failures**
✅ **Integration with external tools**

## Next: Run Full Integration Test

```bash
cd backend
python tests/ai/test_ai_integration.py
```
