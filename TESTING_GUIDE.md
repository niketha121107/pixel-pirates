# Pixel Pirates - Local Testing Guide

This guide helps you test the full frontend-backend AI integration locally.

## Quick Start (5 minutes)

### Step 1: Start Services
```bash
cd pixel-pirates
bash start-dev.sh
```

This will:
- Start MongoDB
- Start Backend API (port 5000)
- Start Frontend (port 3000)
- Display health checks

### Step 2: Verify Backend is Running
```bash
# In another terminal
python test-integration.py
```

You should see:
```
✓ Backend is running
✓ Auth Endpoints
✓ Database Connectivity
✓ AI Quiz Generation
✓ AI Study Material
✓ AI Explanations
✓ AI Mock Test
```

### Step 3: Verify Frontend is Working
Open browser: http://localhost:3000

You should see:
- Navbar with language selector
- Topics list loading
- No errors in console

## Detailed Testing Checklist

### Backend Verification

#### 1. Check Backend Starts
```bash
cd backend
python main.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:5000
```

#### 2. Test Basic API Endpoints
```bash
# Get topics
curl http://localhost:5000/api/topics

# Expected: JSON list of topics with id, name, description
```

#### 3. Test AI Quiz Endpoint
```bash
curl "http://localhost:5000/api/ai/quiz/test-ai?topic_name=Python&question_count=2"

# Expected: JSON response with quiz questions
```

#### 4. Test Study Material Endpoint
```bash
# First, get a topic ID
TOPIC_ID="topic-from-previous-response"

curl "http://localhost:5000/api/ai/content/study-material/$TOPIC_ID"

# Expected: JSON response with study material
```

### Frontend Verification

#### 1. Check Frontend Builds
```bash
cd frontend
npm run build

# Expected: No errors, dist/ folder created
```

#### 2. Check Frontend Development Server
```bash
npm run dev

# Expected: Vite server starts on http://localhost:3000
```

#### 3. Test API Calls in Browser Console
```javascript
// Open browser console (F12)

// Test 1: Get topics
fetch('http://localhost:5000/api/topics')
  .then(r => r.json())
  .then(d => console.log('Topics:', d))

// Test 2: Call AI endpoint
fetch('http://localhost:5000/api/ai/quiz/test-ai?topic_name=Python&question_count=2')
  .then(r => r.json())
  .then(d => console.log('AI Quiz:', d))
```

### AI Integration Testing

#### Test 1: Study Material with AI

1. Go to http://localhost:3000
2. Click on any topic
3. Navigate to "Study Material" tab
4. Expected results:
   - If API key is configured: Shows "✨ AI Generated" badge
   - If API key is missing: Falls back to database content
   - No errors in console

#### Test 2: Quiz with AI

1. Go to http://localhost:3000
2. Click on any topic
3. Click "Take Quiz"
4. Expected results:
   - If API key is configured: Shows AI-generated questions
   - If API key is missing: Shows database questions
   - All quiz features work: animations, scoring, timer

#### Test 3: Adaptive Quiz

1. Go to http://localhost:3000
2. Click "Adaptive Quiz"
3. Select "Auto" or specific topic
4. Expected results:
   - Questions adapt based on performance
   - AI endpoint called first, database fallback
   - Scoring works correctly

### Environment Variables Verification

#### Check Backend Configuration
```bash
cat backend/.env.local

# Should contain:
# GEMINI_API_KEY=sk-...
# MONGODB_URI=mongodb://localhost:27017/
# HOST=0.0.0.0
# PORT=5000
```

#### Check Frontend Configuration
```bash
cat frontend/.env.local

# Should contain:
# VITE_API_URL=http://localhost:5000/api
# VITE_ENABLE_AI=true
# VITE_ENABLE_MOCK_DATA=false
```

### Docker Testing (Optional)

#### Test Docker Build
```bash
# Build all services
docker-compose build

# Should complete without errors

# Check images created
docker images | grep pixel-pirates
```

#### Test Docker Compose
```bash
# Start all services
docker-compose up -d

# Check services running
docker-compose ps

# Should show 3 services: mongodb, backend, frontend

# Check logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## Troubleshooting

### Issue: "Cannot connect to backend"

**Solution 1: Check backend is running**
```bash
curl http://localhost:5000/api/topics
```

If not working:
```bash
cd backend
python main.py
```

**Solution 2: Check MongoDB**
```bash
# Check MongoDB is running
docker-compose ps mongodb

# Should be running (if using Docker)
# Or check local MongoDB: mongosh
```

### Issue: "AI endpoints return 500 errors"

**Check 1: GEMINI_API_KEY**
```bash
# Verify API key is set
echo $GEMINI_API_KEY

# If empty, set it:
export GEMINI_API_KEY=your-api-key
```

**Check 2: API Rate Limiting**
- Gemini API has rate limits
- If hitting limit, fallback to database works
- Wait a few minutes before retrying

**Check 3: API Key Valid**
```bash
# Test API key directly
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Test"}]}]}'
```

### Issue: "Frontend not loading"

**Solution 1: Check Vite server**
```bash
cd frontend
npm run dev
```

**Solution 2: Clear cache**
```bash
# Clear node_modules
rm -rf node_modules
npm install

# Clear Vite cache
rm -rf dist
```

**Solution 3: Port conflict**
```bash
# Check port 3000 in use
netstat -antup | grep 3000

# Kill process on port 3000
# Or change Vite port in vite.config.ts
```

### Issue: "Database connection errors"

**Solution 1: MongoDB running**
```bash
# Check if MongoDB is running
docker-compose ps mongodb

# Or check local MongoDB:
mongosh # should connect
```

**Solution 2: MongoDB URI**
```bash
# Check MONGODB_URI in backend/.env.local
cat backend/.env.local | grep MONGODB_URI

# Should be: mongodb://localhost:27017/
# Or MongoDB Atlas: mongodb+srv://user:pass@host/
```

## Performance Testing

### Test API Response Times
```bash
# Using curl with timing
curl -w '\nTime: %{time_total}s\n' http://localhost:5000/api/topics

# Should be < 1 second
```

### Test Frontend Loading
```bash
# Open DevTools Network tab (F12)
# Reload page (Ctrl+Shift+R for hard refresh)

# Check load time: Should be < 3 seconds
# Check AI endpoints: Should be < 2 seconds
```

### Load Testing (Optional)
```bash
# Install Apache Bench
# Windows: choco install apache-httpd
# Mac: brew install httpd
# Linux: apt-get install apache2-utils

# Test backend
ab -n 100 -c 10 http://localhost:5000/api/topics

# Test AI endpoint
ab -n 20 -c 5 "http://localhost:5000/api/ai/quiz/test-ai?topic_name=Python&question_count=2"
```

## Manual Testing Scenarios

### Scenario 1: New User Learning Path
1. Start fresh app
2. Click "Get Started" or Dashboard
3. Browse topics
4. Select topic → View Study Material (AI-powered)
5. Take Quiz (AI-powered)
6. Check Results
7. Expected: All features work, AI endpoint called, fallback if needed

### Scenario 2: Adaptive Learning
1. Log in (or create account)
2. Select "Adaptive Mode"
3. Answer questions
4. System adapts difficulty
5. Complete quiz
6. Check progress tracking
7. Expected: Difficulty adapts, progress saved, UI smooth

### Scenario 3: Multi-Language Support
1. Click language selector (top header)
2. Select different language (if available)
3. Check content translates
4. Check AI endpoints still work
5. Expected: Content in selected language, AI works

### Scenario 4: Error Recovery
1. Stop backend: `docker-compose stop backend`
2. Try to take quiz
3. Expected: App shows graceful error, offers retry, or falls back to cached data
4. Restart backend: `docker-compose up -d backend`
5. Retry quiz works
6. Expected: Everything recovers without page reload

## Success Criteria

✅ **All tests pass if:**
- [ ] Backend starts without errors
- [ ] Frontend loads at http://localhost:3000
- [ ] Topics display correctly
- [ ] AI endpoints respond (or fallback works)
- [ ] Study Material loads with AI badge
- [ ] Quiz generates questions (AI or database)
- [ ] User can complete quiz and see results
- [ ] Adaptive mode works
- [ ] No console errors
- [ ] All network requests in DevTools are 2xx or 3xx

✅ **Performance targets:**
- Backend startup: < 5 seconds
- Frontend load: < 3 seconds
- API response: < 1 second (topics)
- AI endpoint: < 3 seconds (may be slower)
- Quiz display: < 2 seconds

## Next Steps

Once all tests pass:

1. **Deploy locally with Docker**
   ```bash
   bash start-dev.sh
   ```

2. **Prepare for production**
   - Set up MongoDB Atlas
   - Configure Nginx reverse proxy
   - Set up SSL certificates
   - See DEPLOYMENT_GUIDE.md for details

3. **Team testing**
   - Share test-integration.py
   - Share TESTING_GUIDE.md
   - Have team run tests on their machines

4. **Production deployment**
   ```bash
   bash deploy.sh
   ```

## Quick Test Command Sequence

```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Integration test
python test-integration.py

# Terminal 4: Manual testing
# Open http://localhost:3000 in browser
```

## Logs to Monitor

### Backend Logs
```bash
# In backend directory
tail -f *.log  # Any log files

# Or from Docker
docker-compose logs -f backend
```

### Frontend Logs
```bash
# Browser console (F12)
# Watch for:
# - Network requests to http://localhost:5000/api
# - No console errors
# - AI endpoints called successfully
```

### Database Logs
```bash
# Check MongoDB logs
docker-compose logs -f mongodb
```

## Support

If tests fail:
1. Check TROUBLESHOOTING section above
2. Review DEPLOYMENT_GUIDE.md for detailed setup
3. Check backend/README.md and frontend/README.md
4. Check individual service logs (see "Logs to Monitor")

Good luck! 🚀
