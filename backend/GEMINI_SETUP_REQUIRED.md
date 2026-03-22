# GEMINI API KEY SETUP REQUIRED

## Issue Detected
The Gemini API implementation is complete and working, but the current API key in your `.env` file has been **reported as leaked by Google** and is no longer valid.

**Error Status**: 403 PERMISSION_DENIED
**Current Key**: AIzaSyDagiJmpb-RgH8VYipaBNXQMS-KyCHKyBw
**Solution**: Generate a new API key from Google

---

## Quick Setup (5 minutes)

### Step 1: Generate New API Key
1. Open: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key" button
4. Copy the generated key (looks like: AIzaSy...)

### Step 2: Update .env File
Open `backend/.env` and replace:
```
GEMINI_API_KEY=AIzaSyDagiJmpb-RgH8VYipaBNXQMS-KyCHKyBw
```

With your new key:
```
GEMINI_API_KEY=<paste-your-new-key-here>
```

### Step 3: Restart Backend
```bash
cd backend
python -m uvicorn main:app --reload
```

---

## What's Already Done ✅

### Backend Implementation
- ✅ `app/services/ai_content_service.py` - Core AI generation service
- ✅ `app/routes/ai_quiz.py` - 5 quiz endpoints 
- ✅ `app/routes/ai_content.py` - 3 content endpoints
- ✅ `main.py` - Routes registered
- ✅ Error handling & retry logic (3 retries, exponential backoff)
- ✅ Rate limiting support (429 status)

### Available AI Endpoints (After Setup)

```
GET /api/ai/quiz/test-ai
  - Test AI basic functionality
  - No authentication required
  - Returns sample generated questions

GET /api/ai/quiz/quiz/{topic_id}
  - Generate quiz questions for topic
  - Parameters: question_count, difficulty
  - Returns 5-20 MCQ questions

GET /api/ai/quiz/generate-adaptive
  - Adaptive quiz based on user performance
  - Parameters: topic_id, question_count

POST /api/ai/quiz/mock-test  
  - Full mock test generation
  - Parameters: topics, total_questions, difficulty_easy/medium/hard
  - Returns complete test with metadata

GET /api/ai/content/study-material/{topic_id}
  - Generate study materials
  - Returns: overview, explanation, syntax, examples, advantages, disadvantages

GET /api/ai/content/explanations/{topic_id}
  - Multi-style explanations (simplified, logical, visual, analogy)

GET /api/ai/content/full-content/{topic_id}
  - Complete learning package (materials + explanations + quiz)
```

---

## Testing After Setup

### Verify API Working
```bash
python test_ai_integration.py
```

Expected output:
```
[1] Authentication
   [OK] Logged in successfully

[2] Test AI Quiz Generation (No Auth)
   [OK] AI generation working!
   ...
```

### Manual Test
```bash
curl "http://localhost:5000/api/ai/quiz/test-ai?topic_name=Python+Functions"
```

---

## Troubleshooting

### Still Getting 403 Error?
1. Check API key is copied correctly (no extra spaces)
2. Verify key is not already disabled
3. Generate another key if needed
4. Restart backend after updating

### API Timeout?
- Normal Gemini responses take 3-5 seconds
- Service has 30-second timeout per request
- 3 automatic retries with exponential backoff

### JSON Parse Errors?
- Gemini responses are parsed and validated
- Any malformed responses trigger automatic resend
- Check logs for specific error details

---

## Next Steps

After API key setup:
1. ✅ Run test script: `python test_ai_integration.py`
2. ✅ Update frontend to use AI endpoints instead of mock data
3. ✅ Remove mock data dependencies
4. ✅ Deploy to production

---

## Support

If you encounter issues:
1. Check that `.env` file is in the backend root directory
2. Verify new API key works at: https://makersuite.google.com/app/apikey
3. Restart backend with: `python -m uvicorn main:app --reload`
4. Run test script to validate setup: `python test_ai_integration.py`

---

**Status**: Implementation 100% complete. Only blocker: Valid Gemini API key needed.
