# Pixel Pirates Backend API

FastAPI backend for the Pixel Pirates educational platform with integrated AI-powered learning and YouTube video search.

## 🚀 Features

### 🤖 AI-Powered Learning
- **Adaptive Quizzes** - AI generates personalized questions based on user performance
- **Smart Mock Tests** - Comprehensive assessments with difficulty balancing  
- **Personalized Explanations** - AI adapts explanations to user's learning style
- **Performance Analysis** - Intelligent insights and recommendations

### 📺 YouTube Integration
- **Smart Video Search** - Find educational programming videos
- **Relevance Scoring** - AI-ranked results for better learning outcomes
- **Personalized Recommendations** - Videos based on learning progress
- **Progress Tracking** - Monitor video watch time and completion

### 🎯 Core Learning Platform
- User authentication and profiles
- Topic management with progress tracking
- Quiz system with detailed analytics
- Leaderboards and gamification
- Search functionality across all content

## 🔧 Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure API Keys
The following API keys are already configured in `app/core/config.py`:

- **YouTube API**: `AIzaSyA1TyjjqwcWVTYl8RU_5n2iWauC4SB7Dho`
- **OpenRouter API**: `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`

### 3. Start the Server
```bash
# Option 1: Direct startup
python main.py

# Option 2: Using startup script (recommended)
python start.py

# Option 3: Development mode
uvicorn main:app --reload --port 5000
```

The API will be available at `http://localhost:5000`

## 📚 API Documentation

Once running, visit:
- **Interactive Docs**: `http://localhost:5000/docs`
- **ReDoc**: `http://localhost:5000/redoc`

## 🛣️ API Endpoints

### 🔐 Authentication (`/api/auth`)
- `POST /login` - User authentication
- `POST /signup` - User registration
- `POST /logout` - Session termination

### 👤 User Management (`/api/users`)
- `GET /profile` - Current user profile  
- `PUT /profile` - Update user preferences
- `GET /stats` - User statistics and badges

### 📖 Topics & Learning (`/api/topics`)
- `GET /` - All topics with progress status
- `GET /{topic_id}` - Detailed topic information
- `GET /{topic_id}/explanation` - **🤖 AI-powered personalized explanations**
- `PUT /{topic_id}/status` - Update learning progress
- `GET /{topic_id}/quiz` - Quiz questions

### 🧪 Quiz System (`/api/quiz`)
- `POST /submit` - Submit answers with AI feedback
- `POST /adaptive` - **🤖 Generate adaptive AI quizzes**
- `POST /mock-test` - **🤖 Create comprehensive mock tests**  
- `GET /results/{topic_id}` - Previous quiz attempts
- `GET /performance-analysis` - **🤖 AI learning analytics**

### 📺 Video Integration (`/api/videos`)
- `GET /search` - **📺 YouTube video search**
- `GET /recommendations` - **📺 Personalized video suggestions**
- `GET /watched` - User's watch history
- `POST /watch` - Mark video as watched
- `GET /{video_id}/details` - **📺 YouTube video details**
- `GET /trending/{language}` - **📺 Trending programming videos**

### 🏆 Leaderboard (`/api/leaderboard`)
- `GET /` - Global rankings with pagination
- `GET /top/{count}` - Top performers
- `GET /user-rank` - Current user's position
- `GET /language/{language}` - Language-specific leaderboard

### 📊 Analytics (`/api/analytics`)
- `GET /dashboard` - Overview statistics
- `GET /progress` - Learning progress over time  
- `GET /performance` - Performance by language/difficulty
- `GET /streaks` - Study consistency data

### 🔍 Search (`/api/search`)
- `GET /recent` - Search history
- `POST /` - Save search queries
- `GET /suggestions` - Auto-complete suggestions
- `GET /global` - Content search across platform
- `GET /trending` - Popular search terms

## 🤖 AI Integration Details

### OpenRouter Integration
- **Model**: Claude 3 Sonnet Beta
- **Capabilities**: 
  - Adaptive quiz generation
  - Personalized explanations  
  - Learning progress analysis
  - Mock test creation
- **Fallback**: Graceful degradation to static content

### YouTube Integration
- **Search Enhancement**: Programming-focused queries
- **Content Filtering**: Educational content prioritization
- **Relevance Scoring**: Multi-factor ranking algorithm
- **Duration Preferences**: Short/Medium/Long video filtering

## 🗄️ Data Structure

Currently uses mock data stored in `app/data/__init__.py`. In production, replace with:
- PostgreSQL/MySQL for user data and progress
- Redis for caching and sessions
- Vector database for AI-generated content

## 🚦 Error Handling

- **Graceful API Fallbacks**: If external APIs fail, falls back to static content
- **Rate Limiting**: Built-in protection for API usage
- **Validation**: Comprehensive input validation with Pydantic
- **Logging**: Detailed error tracking for debugging

## 🔒 Security Features

- **CORS Configuration**: Proper cross-origin setup
- **Input Sanitization**: Protection against injection attacks  
- **Rate Limiting**: API abuse prevention
- **Environment Isolation**: Separate dev/prod configurations

## 📈 Performance Optimizations

- **Async Operations**: Non-blocking AI and YouTube API calls
- **Connection Pooling**: Efficient HTTP client reuse
- **Caching Strategy**: Reduce redundant API calls
- **Background Tasks**: Non-critical operations in background

## 🛠️ Development

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
black .  # Code formatting
flake8 . # Linting
mypy .   # Type checking
```

### Adding New Features
1. Create feature branch
2. Add routes in `app/routes/` 
3. Update models in `app/models/`
4. Add tests in `tests/`
5. Update documentation

## 🚀 Deployment

### Docker
```bash
docker build -t pixel-pirates-api .
docker run -p 5000:5000 pixel-pirates-api
```

### Environment Variables
```bash
export YOUTUBE_API_KEY="your_key_here"
export OPENROUTER_API_KEY="your_key_here" 
export DATABASE_URL="your_db_url_here"
```

## 📞 Support

- **Issues**: Create GitHub issue with reproduction steps
- **Features**: Submit feature request with use case
- **Security**: Email security issues privately

---
**Pixel Pirates** - Making programming education intelligent and engaging! 🏴‍☠️✨