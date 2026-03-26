# Pixel Pirates

An adaptive learning platform for coding education with AI-powered features.

## Overview

Pixel Pirates is a full-stack educational web application that provides personalized coding education through AI-powered mock tests, interactive quizzes, video recommendations, and progress tracking.

## Tech Stack

### Backend
- **Framework:** FastAPI (Python)
- **Database:** MongoDB (Motor async driver)
- **AI Integration:** OpenRouter API, Gemini 2.5 Flash
- **YouTube API:** Video integration for learning content

### Frontend
- **Framework:** React 19 with TypeScript
- **Build Tool:** Vite 7
- **Styling:** Tailwind CSS 3.4
- **Animations:** Framer Motion 12
- **HTTP Client:** Axios

### Infrastructure
- **Containerization:** Docker, Docker Compose

## Features

- 🔐 JWT Authentication (Sign Up, Sign In, Logout)
- 🤖 AI-Powered Mock Tests (Gemini 2.5 Flash + OpenRouter)
- 🎥 YouTube Video Integration
- 📊 Adaptive Quizzes
- 📈 Progress Analytics
- 🛡️ Anti-Cheat Mock Test Security
- 📝 Note-Taking & Study Materials
- 💬 AI-Powered Chat Assistance
- 📄 Auto-Generated PDF Study Materials (200+ topics covered)

## Project Structure

```
pixel-pirates/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── core/           # Auth, Config, Database
│   │   ├── data/           # Mock data
│   │   ├── models/         # Data models
│   │   ├── routes/        # API endpoints
│   │   └── services/      # Business logic
│   ├── docs/              # Documentation
│   ├── scripts/           # Utility scripts
│   ├── storage/           # Generated PDFs
│   └── tests/              # Test files
│
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/    # UI Components
│   │   ├── context/       # React Context
│   │   ├── hooks/         # Custom Hooks
│   │   ├── lib/           # Utilities & Translations
│   │   ├── pages/         # Page Components
│   │   └── services/      # API Services
│   └── public/            # Static Assets
│
├── docker-compose.yml      # Docker Orchestration
└── README.md
```

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.9+
- Docker & Docker Compose

### Local Development

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

The API will be available at `http://localhost:8000`

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

## PDF Study Materials

All 200+ topics in the platform have auto-generated PDF study materials. Each PDF includes:

- Topic overview and key concepts
- 4 explanation styles: Simplified, Logical, Visual & Analogy
- Code examples and practical demonstrations
- Key points summary
- Study materials and learning resources

PDFs are generated using ReportLab and stored in `/backend/storage/pdfs/`. The frontend fetches PDFs with authentication and displays them in an embedded viewer.

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for the interactive API documentation (Swagger UI).

## Environment Variables

### Backend (.env)
```
MONGO_URI=mongodb://localhost:27017
OPENROUTER_API_KEY=your_api_key
YOUTUBE_API_KEY=your_api_key
JWT_SECRET=your_secret_key
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## License

MIT