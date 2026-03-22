# 🎯 Custom Topic AI Quiz Generation - Complete Guide

## Overview
Users can now generate AI-powered quiz questions for **ANY topic they want** - not limited to pre-defined topics in the database!

### What's New?
✅ **Free-form topic input** - Type any topic name (e.g., "Quantum Physics", "Victorian Literature", "Blockchain")  
✅ **Instant AI generation** - Questions are generated on-the-fly using Gemini AI  
✅ **Multiple question types** - MCQ, Fill-in-the-Blanks, Written Answers  
✅ **Customizable parameters** - Choose 5, 10, 15, or 20 questions  
✅ **Difficulty levels** - Mixed difficulty for balanced challenge  

---

## How It Works

### User Flow
```
1. User navigates to Mock Test page
2. Enters ANY custom topic (e.g., "Machine Learning Basics")
3. Selects number of questions (5, 10, 15, 20)
4. Selects test duration (10, 15, 20, 30 minutes)
5. Selects question types (MCQ, Fill-up, Written)
6. Clicks "Start Mock Test"
7. ✨ AI generates topic-specific questions instantly!
```

### Architecture Flow
```
User Input (Custom Topic)
    ↓
Frontend: /ai/quiz/custom-topic (POST)
    ↓
Backend Endpoint: POST /api/ai/quiz/custom-topic
    ↓
AI Service: Custom Topic Generator
    ↓
Gemini 2.5 Flash API
    ↓
Formatted Questions (JSON)
    ↓
Frontend: QuizPage displays questions
    ↓
User takes quiz
```

---

## Implementation Details

### Frontend Changes

#### 1. **Updated API Service** (`frontend/src/services/api.ts`)
```typescript
// New method in aiAPI
customTopicQuiz: (topicName: string, questionCount?: number, difficulty?: string) =>
    api.post(`/ai/quiz/custom-topic`, null, {
        params: {
            topic_name: topicName,
            question_count: questionCount || 5,
            difficulty: difficulty || 'medium'
        }
    }),
```

#### 2. **Enhanced MockTest Component** (`frontend/src/pages/MockTest.tsx`)
- Added import for `aiAPI`
- Modified `startTest()` function to:
  - **First attempt**: Call `aiAPI.customTopicQuiz()` for AI generation
  - **On success**: Format and display AI-generated questions
  - **On failure**: Fallback to traditional mock test API
  - **Logging**: Console logs show which endpoint is being used

**Key code snippet:**
```typescript
const res = await aiAPI.customTopicQuiz(topicFilter, questionCount, 'mixed');
console.log(`✅ Received ${aiQuestions.length} AI-generated questions for "${topicFilter}"`);
```

### Backend Changes

#### 1. **New API Endpoint** (`backend/app/routes/ai_quiz.py`)
```python
@router.post("/custom-topic", response_model=SuccessResponse)
async def generate_custom_topic_quiz(
    topic_name: str = Query(..., description="Any topic name"),
    question_count: int = Query(5, ge=1, le=20),
    difficulty: str = Query("medium", regex="^(easy|medium|hard|mixed)$"),
    current_user: dict = Depends(get_current_user_from_token)
)
```

**Features:**
- ✅ No database topic lookup required
- ✅ Accepts ANY topic name as free-form text
- ✅ Returns 1-20 questions
- ✅ Supports difficulty: easy, medium, hard, mixed
- ✅ Proper error handling with fallback
- ✅ Detailed logging for debugging

**Response Format:**
```json
{
  "success": true,
  "message": "Generated 5 AI quiz questions for 'Python Decorators'",
  "data": {
    "topicName": "Python Decorators",
    "questions": [
      {
        "question": "...",
        "options": ["...", "...", "...", "..."],
        "correctAnswer": "...",
        "explanation": "...",
        "type": "mcq",
        "points": 10
      },
      ...
    ],
    "totalQuestions": 5,
    "difficulty": "mixed",
    "isAIGenerated": true,
    "isCustomTopic": true
  }
}
```

---

## API Endpoint Specification

### Endpoint: `POST /api/ai/quiz/custom-topic`

#### Parameters (Query String)
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `topic_name` | string | Yes | - | Any topic to generate questions for |
| `question_count` | integer | No | 5 | Number of questions (1-20) |
| `difficulty` | string | No | "medium" | easy, medium, hard, or mixed |

#### Headers
```
Authorization: Bearer {user_token}
Content-Type: application/json
```

#### Example Request
```bash
curl -X POST "http://localhost:5000/api/ai/quiz/custom-topic" \
  -H "Authorization: Bearer eyJ..." \
  -G \
  --data-urlencode "topic_name=Photosynthesis" \
  --data-urlencode "question_count=10" \
  --data-urlencode "difficulty=mixed"
```

#### Success Response (200)
```json
{
  "success": true,
  "message": "Generated 10 AI quiz questions for 'Photosynthesis'",
  "data": {
    "topicName": "Photosynthesis",
    "totalQuestions": 10,
    "questions": [...],
    "isAIGenerated": true,
    "isCustomTopic": true
  }
}
```

#### Error Response (400/500)
```json
{
  "success": false,
  "detail": "Topic name cannot be empty"
}
```

---

## Testing the Feature

### Test 1: UI Test (Browser)
1. Open http://localhost:5173
2. Navigate to "Mock Test"
3. In "Test Settings", enter a custom topic:
   - Try: "Artificial Intelligence"
   - Try: "Ancient Roman History"
   - Try: "Quantum Entanglement"
4. Select number of questions
5. Click "Start Mock Test"
6. ✅ Questions should be generated for your topic!

### Test 2: API Test (Command Line)
```bash
# Make sure you have a valid auth token
export TOKEN="your_bearer_token"

curl -X POST "http://localhost:5000/api/ai/quiz/custom-topic" \
  -H "Authorization: Bearer $TOKEN" \
  -G \
  --data-urlencode "topic_name=Machine Learning" \
  --data-urlencode "question_count=5" \
  --data-urlencode "difficulty=hard"
```

### Test 3: Monitor Logs
Watch the backend terminal for:
```
✅ Successfully generated 5 AI questions for topic: Machine Learning
```

---

## Fallback Behavior

### What if AI Generation Fails?
The system implements a graceful fallback:

1. **AI Custom Topic API** (Primary)
   - Fastest response
   - Most customizable
   - Best for unique topics

2. **Generic Mock Test API** (Fallback)
   - Used if AI custom fails
   - Still quality questions
   - From database + sampled

3. **Sample Questions** (Last Resort)
   - Predefined questions
   - Always available
   - Good for testing

**Frontend Logging:**
```javascript
// Success
✅ AI quiz generated successfully

// Fallback triggered
⚠️ AI quiz failed, trying regular API: [error message]

// Final fallback
❌ Both AI and regular quiz failed
```

---

## Configuration

### Environment Variables Needed
In `backend/.env.local`:
```env
GEMINI_API_KEY=AIzaSyBEd2lFjAW1oivAXhpEN4LRcCcSjkhj_wM
GEMINI_MODEL=gemini-2.5-flash
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
```

### Question Generation Parameters
- **Temperature**: 0.7 (moderate randomness)
- **Max Tokens**: 2048 (sufficient for detailed questions)
- **Retries**: 3 attempts with exponential backoff
- **Timeout**: 30 seconds per request

---

## Performance Considerations

### Response Times
| Scenario | Time | Notes |
|----------|------|-------|
| AI Generation | 5-15 seconds | Depends on API latency |
| Fallback Mock Test | 2-5 seconds | Database queries |
| Sample Questions | <100ms | Instant local data |

### Optimization Tips
1. **Batch requests**: If possible, pre-generate for common topics
2. **Caching**: Results can be cached per topic for 1 hour
3. **Rate limiting**: Gemini API has quotas (adjust difficulty for cost optimization)

---

## Troubleshooting

### Issue: "Unable to generate quiz questions"
**Solution:**
- Verify Gemini API key is valid
- Check API quota hasn't been exceeded
- Try a simpler topic name
- Check backend logs: `python main.py`

### Issue: Questions take too long to appear
**Solution:**
- First request to Gemini is slower (~15s)
- Verify internet connection
- Check if Gemini API is responding: `curl https://generativelanguage.googleapis.com/`

### Issue: Questions are generic/wrong for topic
**Solution:**
- Try rephrasing the topic name
- Use more specific topic names (e.g., "React Hooks" instead of "React")
- Clear browser cache: Ctrl+Shift+Del

### Issue: Backend returning 401 errors
**Solution:**
- Verify user is logged in
- Check token hasn't expired
- Try logging out and back in

---

## Future Enhancements

🚀 **Planned Features:**
- [ ] Save custom topic quizzes for later review
- [ ] Share custom quizzes with other users
- [ ] Categories for custom topics (Science, History, etc.)
- [ ] Difficulty adjustment based on performance
- [ ] Multi-language support
- [ ] Bulk custom topic quiz generation
- [ ] Quiz result analytics per custom topic

---

## Summary

✨ **You now have:**
- ✅ Free-form topic input for any subject
- ✅ Instant AI-powered question generation
- ✅ Smart fallback system for reliability
- ✅ Full logging and error handling
- ✅ Browser-based testing interface
- ✅ API endpoint for programmatic access

**Happy quizzing! 🎉**
