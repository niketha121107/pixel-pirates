# Backend Directory Structure - Complete Reference

## 📁 Full Directory Tree

```
pixel-pirates/
│
├── backend/                                ← MAIN BACKEND DIRECTORY
│   │
│   ├── app/                                ← Application Source Code
│   │   ├── __init__.py
│   │   ├── core/                           ← Core Utilities
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                     - Authentication logic
│   │   │   ├── config.py                   - Configuration
│   │   │   └── database.py                 - Database connection
│   │   │
│   │   ├── services/                       ← Business Logic Layer
│   │   │   ├── __init__.py
│   │   │   ├── ai_content_service.py       ✨ NEW - AI generation engine
│   │   │   ├── openrouter_service.py       - OpenRouter AI integration
│   │   │   ├── youtube_service.py          - YouTube API integration
│   │   │   └── __pycache__/
│   │   │
│   │   ├── routes/                         ← HTTP API Endpoints
│   │   │   ├── __init__.py
│   │   │   ├── ai_quiz.py                  ✨ NEW - Quiz generation endpoints
│   │   │   ├── ai_content.py               ✨ NEW - Content generation endpoints
│   │   │   ├── auth.py                     - Authentication endpoints
│   │   │   ├── quiz.py                     - Existing quiz endpoints
│   │   │   ├── topics.py                   - Topics endpoints
│   │   │   ├── users.py                    - User endpoints
│   │   │   ├── videos.py                   - Video endpoints
│   │   │   ├── analytics.py                - Analytics endpoints
│   │   │   ├── feedback.py                 - Feedback endpoints
│   │   │   ├── progress.py                 - Progress tracking
│   │   │   ├── notes.py                    - Notes endpoints
│   │   │   ├── leaderboard.py              - Leaderboard endpoints
│   │   │   ├── search.py                   - Search endpoints
│   │   │   ├── adaptive.py                 - Adaptive learning
│   │   │   ├── database.py                 - Database operations
│   │   │   └── __pycache__/
│   │   │
│   │   ├── models/                         ← Data Models
│   │   │   ├── __init__.py
│   │   │   └── __pycache__/
│   │   │
│   │   ├── data/                           ← Data Files
│   │   │   ├── __init__.py
│   │   │   └── __pycache__/
│   │   │
│   │   └── __pycache__/
│   │
│   ├── tests/                              ✨ NEW - Test Suite Directory
│   │   ├── __init__.py
│   │   └── ai/                             ✨ NEW - AI Integration Tests
│   │       ├── __init__.py
│   │       ├── test_ai_integration.py      ✨ NEW - Full end-to-end test
│   │       ├── test_quiz_debug.py          ✨ NEW - Quiz debugging
│   │       ├── test_explanation_debug.py   ✨ NEW - Explanation debugging
│   │       ├── test_service_direct.py      ✨ NEW - Service layer test
│   │       └── test_backend_direct.py      ✨ NEW - Endpoint test
│   │
│   ├── scripts/                            ✨ NEW - Utility Scripts
│   │   ├── __init__.py
│   │   └── verify_gemini_key.py            ✨ NEW - API key verification
│   │
│   ├── docs/                               ✨ NEW - Documentation
│   │   └── ai-integration/                 ✨ NEW - AI Integration Docs
│   │       ├── 00_FILE_ORGANIZATION.md    - Directory structure guide
│   │       ├── MIGRATION_SUMMARY.md       - Migration details
│   │       ├── TESTING_GUIDE.md           - How to run tests
│   │       ├── SETUP_GUIDE.md             - Setup instructions (existing)
│   │       ├── API_REFERENCE.md           - API documentation (existing)
│   │       ├── ARCHITECTURE.md            - System design (existing)
│   │       ├── TROUBLESHOOTING.md         - Issue solutions (existing)
│   │       └── DEPLOYMENT.md              - Deployment guide (existing)
│   │
│   ├── main.py                             - FastAPI application entry point
│   ├── .env                                - Environment configuration (GEMINI_API_KEY, etc.)
│   ├── requirements.txt                    - Python dependencies
│   ├── README.md                           - Backend overview
│   ├── README_AI_INTEGRATION.md            - AI integration quick start
│   │
│   ├── (Legacy Scripts - Can be archived)
│   ├── check_*.py                          - Database check scripts
│   ├── fix_*.py                            - Fix/migration scripts
│   ├── verify_*.py                         - Verification scripts
│   ├── test_*.py                           - Legacy tests
│   ├── count_*.py                          - Count/analysis scripts
│   ├── do_*.py                             - Utility scripts
│   ├── enrich_*.py                         - Data enrichment scripts
│   ├── expand_*.py                         - Expansion scripts
│   ├── fetch_*.py                          - Fetch/import scripts
│   ├── fill_*.py                           - Fill/update scripts
│   ├── generate_*.py                       - Generation scripts
│   ├── init_*.py                           - Initialization scripts
│   ├── inspect_*.py                        - Inspection scripts
│   ├── remove_*.py                         - Removal scripts
│   ├── seed_*.py                           - Seeding scripts
│   └── __pycache__/
│
├── frontend/                               ← REACT FRONTEND
│   ├── src/
│   │   ├── components/                     - React components
│   │   ├── pages/                          - Page components
│   │   ├── services/                       - API services
│   │   ├── context/                        - React context
│   │   ├── hooks/                          - Custom hooks
│   │   ├── lib/                            - Utilities
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── public/
│   │   └── dashboard-icons/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── README.md
│
└── README.md                                - Project overview
```

---

## 📊 File Organization by Purpose

### 🔧 Services Layer (Business Logic)
```
app/services/
├── ai_content_service.py              ✨ AI content generation
├── openrouter_service.py              - Alternative AI provider
└── youtube_service.py                 - YouTube integration
```
**Purpose**: Pure business logic, no HTTP  
**When to modify**: Add new content types or AI providers

---

### 🌐 Routes Layer (HTTP Endpoints)
```
app/routes/
├── ai_quiz.py                         ✨ Quiz generation endpoints
├── ai_content.py                      ✨ Content generation endpoints
├── quiz.py                            - Existing quiz endpoints
├── topics.py                          - Topic management
├── auth.py                            - Authentication
└── [13 other route modules]           - Various features
```
**Purpose**: HTTP request/response handling  
**When to modify**: Change endpoint behavior or add new endpoints

---

### 🧪 Tests (Quality Assurance)
```
tests/ai/
├── test_ai_integration.py             ✨ Full E2E test
├── test_quiz_debug.py                 ✨ Quiz debugging
├── test_explanation_debug.py          ✨ Explanation debugging
├── test_service_direct.py             ✨ Service testing
└── test_backend_direct.py             ✨ Endpoint testing
```
**Purpose**: Verification and debugging  
**When to modify**: Add new test cases or debug features

---

### 🔧 Scripts (Utilities)
```
scripts/
└── verify_gemini_key.py               ✨ API key verification
```
**Purpose**: Standalone tools and utilities  
**When to modify**: Add setup or maintenance scripts

---

### 📖 Documentation
```
docs/ai-integration/
├── 00_FILE_ORGANIZATION.md            ← Directory structure
├── MIGRATION_SUMMARY.md               ← What moved and why
├── TESTING_GUIDE.md                   ← How to run tests
├── SETUP_GUIDE.md                     ← Getting started
├── API_REFERENCE.md                   ← Endpoint docs
├── ARCHITECTURE.md                    ← System design
├── TROUBLESHOOTING.md                 ← Problem solving
└── DEPLOYMENT.md                      ← Production setup
```
**Purpose**: Knowledge base and guides  
**When to modify**: Update procedures or fix documentation

---

### ⚙️ Configuration (Root)
```
backend/
├── main.py                            - Application entry point
├── .env                               - Environment variables
├── requirements.txt                   - Python packages
├── README.md                          - Backend overview
└── README_AI_INTEGRATION.md           - AI quick start
```
**Purpose**: Application configuration  
**When to modify**: Add dependencies or environment variables

---

## 📋 File Organization Rules

### ✅ DO's

1. **Services** - Pure logic, reusable, testable
   ```python
   # ✅ GOOD: app/services/ai_content_service.py
   async def generate_quiz_questions(self, topic_name, num_questions):
       # No FastAPI, no HTTP, just business logic
       ...
   ```

2. **Routes** - HTTP endpoints, request handling
   ```python
   # ✅ GOOD: app/routes/ai_quiz.py
   @router.get("/quiz/{topic_id}")
   async def get_quiz(topic_id: str, ...):
       result = await ai_generator.generate_quiz_questions(...)
       return {"success": True, "data": result}
   ```

3. **Tests** - In `tests/` with clear names
   ```
   ✅ GOOD: tests/ai/test_ai_integration.py
   ✅ GOOD: tests/ai/test_quiz_debug.py
   ```

4. **Scripts** - Standalone utilities
   ```bash
   ✅ GOOD: scripts/verify_gemini_key.py
   ✅ GOOD: python scripts/verify_gemini_key.py
   ```

5. **Docs** - In `docs/` organized by topic
   ```
   ✅ GOOD: docs/ai-integration/SETUP_GUIDE.md
   ✅ GOOD: docs/ai-integration/API_REFERENCE.md
   ```

### ❌ DON'Ts

```
❌ DON'T: Keep test files in backend root
   ✅ DO: Move to tests/ai/

❌ DON'T: Keep docs scattered in root
   ✅ DO: Organize in docs/ai-integration/

❌ DON'T: Mix HTTP logic with business logic
   ✅ DO: Put logic in services, HTTP in routes

❌ DON'T: Keep scripts in root directories
   ✅ DO: Store in scripts/

❌ DON'T: Have multiple purposes in one file
   ✅ DO: One responsibility per file
```

---

## 🚀 Quick Navigation

### I need to...

| Task | Location |
|------|----------|
| Modify AI generation logic | `app/services/ai_content_service.py` |
| Add new AI endpoint | `app/routes/ai_quiz.py` or `app/routes/ai_content.py` |
| Debug AI generation | `tests/ai/test_quiz_debug.py` |
| Run integration test | `python tests/ai/test_ai_integration.py` |
| Verify API key setup | `python scripts/verify_gemini_key.py` |
| Learn API endpoints | `docs/ai-integration/API_REFERENCE.md` |
| Setup new environment | `docs/ai-integration/SETUP_GUIDE.md` |
| Deploy to production | `docs/ai-integration/DEPLOYMENT.md` |
| Troubleshoot issues | `docs/ai-integration/TROUBLESHOOTING.md` |

---

## 📊 Statistics

### Code Organization
- **Services**: 1 AI service file (`ai_content_service.py`)
- **Routes**: 2 AI route files (`ai_quiz.py`, `ai_content.py`)
- **Tests**: 5 AI test files (in `tests/ai/`)
- **Scripts**: 1 verification script (in `scripts/`)
- **Documentation**: 8 comprehensive guides (in `docs/ai-integration/`)

### Dependencies
- **Framework**: FastAPI
- **Database**: MongoDB (motor)
- **AI Provider**: Google Gemini
- **HTTP Client**: httpx, requests

### Endpoints
- **Quiz Generation**: 5 endpoints
- **Content Generation**: 3 endpoints
- **Total**: 8 AI endpoints

---

## 🔄 File Lookup Examples

### Find where quiz generation happens
1. Check `/tests/ai/test_ai_integration.py` - See test flow
2. Go to `/app/routes/ai_quiz.py` - See endpoint
3. Go to `/app/services/ai_content_service.py` - See actual logic

### Find test for explanations
1. Go to `/tests/ai/test_explanation_debug.py` - Direct test

### Find API documentation
1. Go to `/docs/ai-integration/API_REFERENCE.md` - All endpoints documented

### Find setup instructions
1. Go to `/docs/ai-integration/SETUP_GUIDE.md` - Complete setup guide

---

## ✨ Created in This Session

```
✅ tests/                                - Test directory
✅ tests/ai/                             - AI tests subdirectory
✅ tests/__init__.py                     - Package marker
✅ tests/ai/__init__.py                  - Package marker
✅ tests/ai/test_ai_integration.py       - Moved from root
✅ tests/ai/test_quiz_debug.py           - Moved from root
✅ tests/ai/test_explanation_debug.py    - Moved from root
✅ tests/ai/test_service_direct.py       - Moved from root
✅ tests/ai/test_backend_direct.py       - Moved from root

✅ scripts/                              - Scripts directory
✅ scripts/__init__.py                   - Package marker
✅ scripts/verify_gemini_key.py          - Moved from root

✅ docs/ai-integration/                  - AI docs directory
✅ docs/ai-integration/00_FILE_ORGANIZATION.md - Structure guide
✅ docs/ai-integration/MIGRATION_SUMMARY.md    - Migration details
✅ docs/ai-integration/TESTING_GUIDE.md        - Testing guide
```

---

## 🎯 Benefits

✅ **Clarity** - Everyone knows where to find things  
✅ **Maintainability** - Easy to modify and extend  
✅ **Scalability** - Can grow without confusion  
✅ **Professional** - Follows best practices  
✅ **Production-ready** - Proper structure for deployment  
✅ **Testability** - Easy to test and debug  

---

## Next Steps

1. ✅ **Review** this directory structure
2. ✅ **Run tests** from new location: `python tests/ai/test_ai_integration.py`
3. ✅ **Verify API key**: `python scripts/verify_gemini_key.py`
4. ✅ **Check documentation**: See `docs/ai-integration/` for guides
5. ✅ **Update project README** with new structure
6. ✅ **Commit changes**: `git add tests/ scripts/ docs/`

This organization is now **production-ready** and **fully documented**! 🚀
