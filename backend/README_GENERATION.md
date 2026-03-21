# 🚀 Pixel Pirates - Complete Content Generation System

## Overview

This comprehensive system generates all learning content for **200 programming topics** including:
- 🎥 **600+ YouTube Videos** (highly recommended, 3 per topic)
- 📚 **800 Explanations** (4 styles: visual, simplified, logical, analogy)
- 📄 **200 PDF Study Guides** (professional quality)
- ✅ **1,600+ Mock Questions** (8 per topic)
- 🛡️ **Anti-Cheat System** (11-warning enforcement)

All content is automatically stored in MongoDB and accessible via REST APIs.

---

## Quick Start (5 minutes)

### 1. Check Prerequisites
```bash
cd backend
python verify_setup.py
```

### 2. Run Generation (Fully Automated)
```bash
python generate_all_content.py
```

This single command will:
1. Verify/create 200 base topics
2. Generate YouTube videos
3. Generate 4-type explanations
4. Generate PDFs
5. Generate mock tests
6. Store everything in MongoDB

**Estimated time: 50-100 minutes**

### 3. Start the Backend
```bash
python main.py
```

### 4. Access API
- Base URL: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`

---

## What Gets Generated

### Per Topic

```
1 Topic
├── 3 YouTube Videos
│   ├── youtubeId
│   ├── title
│   ├── thumbnail
│   └── channel
│
├── 4 Explanations
│   ├── Visual (📊) - Diagrams and structures
│   ├── Simplified (🎯) - Beginner language
│   ├── Logical (🧠) - Step-by-step reasoning
│   └── Analogy (🎭) - Real-world comparisons
│
├── 1 PDF Study Guide
│   ├── Overview
│   ├── Detailed explanations
│   ├── Practice questions
│   └── Answer key
│
└── 8 Mock Test Questions
    ├── Multiple choice
    ├── Correct answer
    └── Explanation
```

### Across 200 Topics

```
Total Coverage: 20 Languages × 10 Topics Each

Python (10)        JavaScript (10)      Java (10)
C++ (10)           C (10)               TypeScript (10)
Go (10)            Rust (10)            PHP (10)
C# (10)            Ruby (10)            Swift (10)
SQL (10)           Kotlin (10)          Dart (10)
+ 5 more languages: Lua, R, Perl, Scala, Elixir
```

---

## API Endpoints

### Get Complete Topic Data (Most Useful)
```
GET /api/content/complete/{topic_id}
```
Returns: Videos + Explanations + PDF + Mock Test (all in one call)

### Get Videos
```
GET /api/content/videos/{topic_id}
GET /api/content/videos/search?topic_name=Python
```

### Get Explanations
```
GET /api/content/explanations/{topic_id}
GET /api/content/explanations/{topic_id}?style=visual
GET /api/content/explanations/by-style/visual?language=Python
```

### Get PDFs
```
GET /api/content/pdf/{topic_id}
GET /api/content/pdf/download/{topic_id}  # Download file
```

### Get Mock Tests
```
GET /api/content/mock-tests/{topic_id}
GET /api/content/mock-tests/search?topic_name=Python
```

### Get Statistics
```
GET /api/content/statistics
```
Returns: Total topics, videos, explanations, PDFs, tests generated

---

## Frontend Components

Three React components handle mock tests:

### 1. MockTestRules
- Shows test rules before starting
- Anti-cheat policy enforcement
- User acknowledgment required

### 2. MockTest
- Full test interface with timer
- Question navigation (50 questions example)
- Flag for review feature
- Auto-save every 30 seconds
- Anti-cheat monitoring

### 3. MockTestResults
- Results dashboard with score
- Performance charts
- Question review (expandable)
- Download report option

---

## Database Schema

### Topics Collection
```json
{
  "_id": "python_1",
  "topicName": "History & Philosophy",
  "language": "Python",
  "difficulty": "Beginner",
  "overview": "...",
  
  "recommendedVideos": [...],
  "explanations": [
    {"style": "visual", "content": "..."},
    {"style": "simplified", "content": "..."},
    {"style": "logical", "content": "..."},
    {"style": "analogy", "content": "..."}
  ],
  "mockQuestions": [...],
  "pdfPath": "storage/pdfs/...",
  "contentStatus": "complete",
  "contentGeneratedAt": "2026-03-21T..."
}
```

### Mock Tests Collection
```json
{
  "_id": ObjectId,
  "topicId": "python_1",
  "topicName": "History & Philosophy",
  "questions": [...],
  "totalQuestions": 8,
  "duration": 16,
  "difficulty": "mixed"
}
```

---

## Configuration

### Environment Variables (.env)

```env
# Required
GEMINI_API_KEY=your_api_key_here

# Optional (defaults provided)
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DATABASE=pixel_pirates
YOUTUBE_API_KEY=IzaSyA3_26DIrG1LvgJEAlhr05QXcB-tFks4Mc
```

### Generation Settings

**Concurrency**: Edit `generate_complete_content.py`
```python
sem = asyncio.Semaphore(2)  # Process 2 topics at a time
```

**Retry Logic**: Configure in generation script
```python
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
```

---

## Common Commands

### Run verification
```bash
python verify_setup.py
```

### Generate topics only
```bash
python verify_and_generate_topics.py
```

### Generate all content
```bash
python generate_complete_content.py
```

### Full automated pipeline
```bash
python generate_all_content.py
```

### Start backend
```bash
python main.py
```

### Check database status
```bash
python -c "
import asyncio
from app.core.database import db, connect_to_mongo
from app.core.config import settings

async def check():
    await connect_to_mongo(settings)
    total = db.database['topics'].count_documents({})
    complete = db.database['topics'].count_documents({'contentStatus': 'complete'})
    print(f'Topics: {total}')
    print(f'Complete: {complete}')

asyncio.run(check())
"
```

---

## Performance Metrics

### Generation Speed
- Per topic: 15-30 seconds
- 200 topics: 50-100 minutes
- Bottlenecks: YouTube search (2-3s), Gemini calls (3-5s), PDF generation (2-3s)

### Generated Data Size
- MongoDB: 500-800 MB
- PDF files: 500 MB
- Total: 1-1.5 GB

### API Response Times
- Videos endpoint: 50-100ms
- Explanations endpoint: 50-100ms
- PDF download: 200-500ms
- Complete topic data: 100-200ms

---

## Troubleshooting

### MongoDB Connection Failed
```bash
# Start MongoDB
mongod

# Or use cloud: Update .env to MongoDB Atlas URL
```

### YouTube API Quota Exceeded
```bash
# Wait 24 hours for reset or use different API key
# Reduce concurrency in script
sem = asyncio.Semaphore(1)
```

### Gemini API Rate Limit
```bash
# Add delays
await asyncio.sleep(2)  # Between calls
# Reduce concurrency
# Check quota: https://makersuite.google.com
```

### PDFs Not Generating
```bash
# Check directory exists
mkdir -p storage/pdfs

# Check permissions and disk space
df -h
```

### Package Installation Issues
```bash
# Install all requirements
pip install -r requirements.txt

# Or specific packages
pip install google-generativeai httpx reportlab
```

---

## Success Checklist

After `generate_all_content.py` completes:

- ✅ 200 topics in MongoDB
- ✅ 600+ videos retrieved
- ✅ 800 explanations generated (4 types)
- ✅ 200 PDFs created in `storage/pdfs/`
- ✅ 200 mock tests with 1,600+ questions
- ✅ All content indexed in database
- ✅ API endpoints responding with data

Verify:
```bash
curl http://localhost:8000/api/content/statistics
```

---

## Next Steps

1. **Setup**: `python verify_setup.py` ✓
2. **Generate**: `python generate_all_content.py` ⏳ (50-100 min)
3. **Start Backend**: `python main.py`
4. **Start Frontend**: `npm run dev` (in frontend dir)
5. **Access**: `http://localhost:5173`

---

## Files Created

### Scripts
- `generate_complete_content.py` - Main generation engine
- `verify_and_generate_topics.py` - Topic verification
- `generate_all_content.py` - Master orchestrator
- `verify_setup.py` - Pre-flight checks

### Routes
- `app/routes/content_delivery.py` - Content API endpoints

### Components (Frontend)
- `MockTestRules.tsx` - Rules dialog
- `MockTest.tsx` - Test interface
- `MockTestResults.tsx` - Results dashboard

### Documentation
- `CONTENT_GENERATION_GUIDE.md` - Comprehensive guide
- `README.md` - This file

---

## Support

### Check Logs
```bash
python generate_all_content.py 2>&1 | tee generation.log
tail -f generation.log
```

### Debug Database
```bash
# Connect to MongoDB
mongosh  # or mongo

# List databases
show dbs

# Use pixel_pirates
use pixel_pirates

# Check collections
show collections

# Count topics
db.topics.count()

# View one topic
db.topics.findOne()
```

### Monitor Generation
```bash
# In separate terminal
watch -n 5 'python -c "..."'  # Run status check every 5s
```

---

## API Documentation

Full API docs available at: `http://localhost:8000/docs`

Interactive Swagger UI with all endpoints, requests, and responses.

---

## License & Credits

- **YouTube API**: Google
- **Gemini API**: Google DeepMind
- **MongoDB**: MongoDB Inc.
- **Frontend**: React + TypeScript
- **Backend**: FastAPI + Python

---

## Questions?

Refer to:
1. `CONTENT_GENERATION_GUIDE.md` - Detailed guide
2. `http://localhost:8000/docs` - API documentation
3. Check logs for error messages

---

**🎉 Ready to generate awesome learning content!**

```bash
python generate_all_content.py
```
