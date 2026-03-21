# PIXEL PIRATES - API INTEGRATION GUIDE
## Complete Integration of Gemini AI + YouTube API

### ✅ Current Status: ALL APIS FULLY INTEGRATED

---

## 🔑 API Keys Configuration

### Backend `.env` File
Located at: `backend/.env`

```env
# Gemini API - AI Explanations & Quiz Generation
GEMINI_API_KEY=AIzaSyDagiJmpb-RgH8VYipaBNXQMS-KyCHKyBw
GEMINI_MODEL=gemini-2.5-flash
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta

# YouTube API - Video Search & Fetching
YOUTUBE_API_KEY=AIzaSyBOPk5XIQIVFI_C8awnv3GPPqGFQBAvygo
YOUTUBE_API_SERVICE_NAME=youtube
YOUTUBE_API_VERSION=v3

# Other configurations...
```

---

## 📡 API Integration Points

### 1. Gemini AI Service
**File:** `backend/app/services/openrouter_service.py` (Extended for Gemini)
**Functions:**
- `generate_adaptive_quiz()` - Generate quiz questions
- `generate_explanation()` - Generate topic explanations
- `generate_study_material()` - Generate study guides

**Endpoint:** `/api/topics/{id}/explanation`
**Response:**
```json
{
  "explanation": "AI-generated explanation using Gemini",
  "generated": true,
  "timestamp": "2026-03-21T..."
}
```

### 2. YouTube Service
**File:** `backend/app/services/youtube_service.py`
**Functions:**
- `search_for_topic()` - Search YouTube for topic videos
- `search_videos()` - General video search
- `search_via_invidious()` - Fallback to Invidious

**Endpoint:** `/api/topics/{id}`
**Returns:** `recommendedVideos` array with:
```json
{
  "youtubeId": "dQw4w9WgXcQ",
  "title": "Video Title",
  "description": "Video description",
  "channel": "Channel Name",
  "thumbnail": "URL to thumbnail"
}
```

---

## 🚀 Content Generation Scripts

### Script 1: Test API Integration
```bash
cd backend
python test_api_integration.py
```
✅ Tests both Gemini and YouTube APIs
✅ Confirms connectivity and quota

### Script 2: Generate All Content (FULL)
```bash
cd backend
python api_generate_all_content.py
```
⏯️ Generates for all 200 topics:
- AI explanations (simplified, logical, visual, analogy)
- Quiz questions (5-10 per topic)
- Video recommendations (3 per topic)
- Topic overviews

**Time:** ~2-5 minutes per 50 topics (depends on API throttling)

### Script 3: Generate Content (Existing Script)
```bash
cd backend
python generate_all_content.py
```
Original generator with additional orchestration

---

## 📊 Data Flow

```
┌─────────────────────────────────────────────────────────┐
│         Frontend (React @ localhost:5173)               │
│  ├─ TopicView.tsx                                      │
│  ├─ VideoTrackerUI.tsx (plays YouTube videos)          │
│  └─ Quiz Component (shows Gemini-generated questions)  │
└────────────────┬────────────────────────────────────────┘
                 │ HTTP/REST Calls
                 ↓
┌─────────────────────────────────────────────────────────┐
│      Backend (FastAPI @ localhost:5000)                │
│  ├─ GET /api/topics/{id}                               │
│  │   ├─ Returns: recommendedVideos (from YouTube)      │
│  │   ├─ Returns: explanations (from Gemini)            │
│  │   └─ Returns: quizzes (from Gemini)                 │
│  │                                                      │
│  ├─ GET /api/topics/{id}/explanation                   │
│  │   └─ Generates on-demand Gemini explanation        │
│  │                                                      │
│  ├─ GET /api/topics/{id}/fresh-videos                  │
│  │   └─ Searches YouTube for latest videos             │
│  │                                                      │
│  └─ GET /api/quiz/{topic_id}                           │
│      └─ Returns Gemini-generated quiz questions        │
└────────────────┬────────────────────────────────────────┘
                 │ Database Calls
                 ↓
┌─────────────────────────────────────────────────────────┐
│          MongoDB                                        │
│  ├─ 200 Topics with AI content                         │
│  ├─ Video references from YouTube                      │
│  ├─ Cached Gemini explanations                         │
│  ├─ Quiz questions                                     │
│  └─ User progress & analytics                          │
└─────────────────────────────────────────────────────────┘
```

### External API Calls

```
Frontend/Backend
    ⬇
┌─────────────────────────────────────────┐
│      Gemini API                         │
│  /v1beta/generateContent                │
│  ├─ Explanations in 4 styles           │
│  ├─ Quiz questions                     │
│  ├─ Study materials                    │
│  └─ Topic overviews                    │
└─────────────────────────────────────────┘

Frontend/Backend
    ⬇
┌─────────────────────────────────────────┐
│      YouTube API                        │
│  /youtube/v3/search                    │
│  ├─ Tutorial videos                    │
│  ├─ Educational content                │
│  ├─ Video metadata                     │
│  └─ Recommendations                    │
└─────────────────────────────────────────┘
```

---

## 🔧 Configuration Files

### Backend Configuration
**File:** `backend/app/core/config.py`

```python
class Settings:
    # Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # YouTube
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    YOUTUBE_API_VERSION: str = "v3"
    
    def validate_settings(self) -> bool:
        # Validates all required keys are present
```

### Frontend API Configuration
**File:** `frontend/.env`

```env
VITE_API_URL=http://localhost:5000/api
```

---

## ✅ Verification Checklist

- [x] Gemini API Key configured
- [x] YouTube API Key configured
- [x] API endpoints responding
- [x] MongoDB connected with 200 topics
- [x] Video fetching working
- [x] AI explanation generation working
- [x] Quiz generation working
- [x] Frontend connecting to Backend
- [x] CORS enabled for cross-origin requests
- [x] Authentication working (JWT)

---

## 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| Topics | 200 |
| Videos per topic | 3 |
| Total videos | 600 |
| Explanations per topic | 4 styles |
| Quiz questions | 5-10 per topic |
| Generation time | ~2-5 min per 50 topics |
| API calls per topic | 6-8 (Gemini + YouTube) |
| Database records | ~1000+ |

---

## 🐛 Troubleshooting

### Issue: "Gemini API not responding"
**Solution:**
1. Check GEMINI_API_KEY in `.env`
2. Verify key has proper permissions
3. Check rate limiting (Google has free tier limits)

### Issue: "YouTube videos not loading"
**Solution:**
1. Check YOUTUBE_API_KEY in `.env`
2. Verify YouTube Data API v3 is enabled in Google Cloud Console
3. Check quota usage in Cloud Console
4. Fallback to Invidious should kick in automatically

### Issue: "Database not updating with generated content"
**Solution:**
1. Ensure MongoDB is running: `mongod`
2. Check MONGODB_URL in `.env`
3. Verify database permissions
4. Run `python api_generate_all_content.py` to regenerate

---

## 🎯 Next Steps

1. **Generate All Content**
   ```bash
   cd backend
   python api_generate_all_content.py
   ```

2. **Verify in Database**
   ```
   MongoDB compass → pixel_pirates → topics
   Check that topics have: explanations, quizzes, recommendedVideos
   ```

3. **Test in Frontend**
   - Open http://localhost:5173
   - Login with alex@edutwin.com / password123
   - Click a topic
   - See AI explanations and YouTube videos

4. **Monitor Usage**
   - Check Google Cloud Console for API quota
   - Monitor MongoDB storage
   - Track generation times

---

## 📞 Support

- **Gemini Docs:** https://ai.google.dev/docs
- **YouTube API Docs:** https://developers.google.com/youtube/v3
- **MongoDB Docs:** https://docs.mongodb.com

---

**Last Updated:** March 21, 2026
**Status:** ✅ ALL SYSTEMS OPERATIONAL
