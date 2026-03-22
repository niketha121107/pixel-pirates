# Backend AI Integration - File Organization Guide

## Directory Structure

```
backend/
├── app/
│   ├── services/
│   │   ├── ai_content_service.py          ✅ AI generation engine
│   │   ├── openrouter_service.py          ✅ Existing AI service
│   │   ├── youtube_service.py             ✅ Existing video service
│   │   └── mock_test_service.py           ✅ Existing mock test service
│   │
│   └── routes/
│       ├── ai_quiz.py                     ✅ AI quiz endpoints
│       ├── ai_content.py                  ✅ AI content endpoints
│       ├── quiz.py                        ✅ Existing quiz endpoints
│       ├── topics.py                      ✅ Existing topics endpoints
│       └── ... (other routes)
│
├── docs/
│   └── ai-integration/
│       ├── SETUP_GUIDE.md                 📖 API key setup & requirements
│       ├── API_REFERENCE.md               📖 All AI endpoints documentation
│       ├── ARCHITECTURE.md                📖 System design & data flow
│       ├── TROUBLESHOOTING.md             📖 Common issues & solutions
│       └── DEPLOYMENT.md                  📖 Production deployment guide
│
├── tests/
│   ├── __init__.py
│   └── ai/
│       ├── __init__.py
│       ├── test_ai_integration.py         ✅ Full end-to-end tests
│       ├── test_quiz_debug.py             ✅ Quiz generation debug
│       ├── test_explanation_debug.py      ✅ Explanation generation debug
│       ├── test_service_direct.py         ✅ Service-level testing
│       └── test_backend_direct.py         ✅ Backend endpoint testing
│
├── scripts/
│   └── verify_gemini_key.py               🔧 API key verification script
│
├── main.py                                ✅ Application entry point (routes registered)
├── requirements.txt                       ✅ Dependencies (httpx, fastapi, etc.)
├── .env                                   ✅ GEMINI_API_KEY configured
│
└── README_AI_INTEGRATION.md               📖 Quick start guide
```

---

## File Organization Rules

### 1️⃣ Core AI Services (`app/services/`)
**Store here**: AI generation logic and external API calls
- `ai_content_service.py` - Gemini API calls
- New AI services

**Rules**:
- One class per file (or related classes)
- Pure logic, no HTTP/FastAPI
- Async-ready for performance

### 2️⃣ API Routes (`app/routes/`)
**Store here**: HTTP endpoints and request handling
- `ai_quiz.py` - Quiz endpoints
- `ai_content.py` - Content endpoints

**Rules**:
- FastAPI routers only
- Import from services layer
- Authentication/validation logic

### 3️⃣ Documentation (`docs/ai-integration/`)
**Store here**: Setup guides, API reference, architecture
- Setup instructions
- API endpoint documentation
- Architecture diagrams
- Deployment guides
- Troubleshooting

**Never put in**: Root directory, app folder, or tests folder

### 4️⃣ Tests (`tests/ai/`)
**Store here**: All test scripts
- Integration tests
- Unit tests
- Debug scripts
- Verification scripts

**Rules**:
- One test file per feature
- Clear naming: `test_*.py`
- Use pytest conventions

### 5️⃣ Scripts (`scripts/`)
**Store here**: Utility and setup scripts
- Verification tools
- Migration scripts
- Setup helpers

**Rules**:
- Executable utilities only
- Clear purpose in filename

### 6️⃣ Configuration (Root)
**Store here**: Only essential config
- `main.py` - Entry point
- `.env` - API keys
- `requirements.txt` - Dependencies
- `README_AI_INTEGRATION.md` - Quick start only

**Never put in**: Detailed docs, test files, service code

---

## Migration Checklist

- [x] Create `docs/ai-integration/` directory
- [x] Create `tests/ai/` directory
- [x] Create `scripts/` directory
- [ ] Move documentation files to `docs/ai-integration/`
- [ ] Move test files to `tests/ai/`
- [ ] Move utility scripts to `scripts/`
- [ ] Update imports in all files
- [ ] Update `.gitignore` for test outputs
- [ ] Update README with new structure

---

## Examples of Proper Organization

### ❌ WRONG - Scattered everywhere
```
backend/
├── DEPLOYMENT_READY.md
├── QUICK_START.md
├── AI_IMPLEMENTATION_COMPLETE.md
├── GEMINI_SETUP_REQUIRED.md
├── test_ai_integration.py
├── test_quiz_debug.py
├── test_explanation_debug.py
├── verify_gemini_key.py
├── app/
│   ├── ai_content_service.py
│   └── ai_quiz_endpoints.py
```

### ✅ RIGHT - Organized by purpose
```
backend/
├── app/
│   ├── services/
│   │   └── ai_content_service.py
│   └── routes/
│       ├── ai_quiz.py
│       └── ai_content.py
├── docs/
│   └── ai-integration/
│       ├── SETUP_GUIDE.md
│       ├── API_REFERENCE.md
│       └── DEPLOYMENT.md
├── tests/
│   └── ai/
│       ├── test_ai_integration.py
│       ├── test_quiz_debug.py
│       └── test_explanation_debug.py
├── scripts/
│   └── verify_gemini_key.py
└── README_AI_INTEGRATION.md
```

---

## Import Examples After Reorganization

### ✅ Correct imports in routes

**Before** (if scattered):
```python
from app.services.ai_content_service import ai_generator
```

**After** (same - no change needed):
```python
from app.services.ai_content_service import ai_generator
```

### ✅ Correct imports in tests

**Before** (when scattered):
```python
from app.services.ai_content_service import ai_generator
```

**After** (same):
```python
from app.services.ai_content_service import ai_generator
```

---

## Backend `.gitignore` Updates

```gitignore
# Test outputs
tests/ai/**/*.log
tests/**/__pycache__/

# Cache
__pycache__/
*.pyc

# Generated content
storage/pdfs/
*.pdf

# Environment
.env.local
.env.*.local

# User-specific
.vscode/
.idea/
```

---

## Documentation Index

All documentation now in `docs/ai-integration/`:

| Document | Purpose |
|----------|---------|
| SETUP_GUIDE.md | API key setup & requirements |
| API_REFERENCE.md | Complete endpoint documentation |
| ARCHITECTURE.md | System design & data flow |
| TROUBLESHOOTING.md | Common issues & solutions |
| DEPLOYMENT.md | Production deployment |

---

## Quick Reference After Reorganization

### Run tests
```bash
cd backend
pytest tests/ai/
pytest tests/ai/test_ai_integration.py -v
```

### View documentation
```bash
# API setup
cat docs/ai-integration/SETUP_GUIDE.md

# API reference
cat docs/ai-integration/API_REFERENCE.md

# Troubleshooting
cat docs/ai-integration/TROUBLESHOOTING.md
```

### Verify setup
```bash
python scripts/verify_gemini_key.py
```

---

## Summary

✅ **Organized by role**:
- Services layer: Pure AI logic
- Routes layer: HTTP endpoints
- Tests: All testing
- Docs: All documentation
- Scripts: Utilities

✅ **Easy to maintain**:
- Clear separation of concerns
- Easy to find anything
- Standard Python project layout

✅ **Production-ready**:
- Tests in proper location
- Documentation organized
- Configuration centralized
