@echo off
REM ========================================
REM Pixel Pirates - Automated Setup Script (Windows)
REM ========================================

setlocal enabledelayedexpansion

echo.
echo 🚀 Starting Pixel Pirates Setup
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.11 or higher.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 18 or higher.
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm is not installed. Please install npm.
    pause
    exit /b 1
)

echo ✅ Python version:
python --version
echo.
echo ✅ Node version:
node --version
echo.
echo ✅ npm version:
npm --version
echo.

REM ========================================
REM Backend Setup
REM ========================================
echo 📦 Setting up Backend...
echo ========================================

cd backend

REM Create virtual environment
if not exist "venv" (
    echo 🔧 Creating Python virtual environment...
    python -m venv venv
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install backend dependencies
echo 📥 Installing backend dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    if exist ".env.example" (
        echo 📋 Copying .env.example to .env
        copy .env.example .env
        echo ⚠️  Please update .env with your API keys:
        echo    - YOUTUBE_API_KEY
        echo    - GEMINI_API_KEY
        echo    - MONGODB_URL
        echo    - JWT_SECRET_KEY
    )
)

echo ✅ Backend setup completed
echo.

REM ========================================
REM Frontend Setup
REM ========================================
echo 🎨 Setting up Frontend...
echo ========================================

cd ..\frontend

REM Install frontend dependencies
echo 📥 Installing frontend dependencies...
npm install

REM Check if .env.local exists
if not exist ".env.local" (
    echo 📋 Creating .env.local
    echo VITE_API_URL=http://localhost:8000/api > .env.local
    echo ✅ .env.local created with default API URL
)

echo ✅ Frontend setup completed
echo.

REM ========================================
REM Summary
REM ========================================
cd ..
echo ========================================
echo ✨ Setup Complete!
echo ========================================
echo.
echo 📝 Next Steps:
echo.
echo 1️⃣  Backend Setup:
echo    cd backend
echo    venv\Scripts\activate.bat
echo    REM Update .env with your API keys
echo    python main.py
echo.
echo 2️⃣  Frontend Setup (new terminal):
echo    cd frontend
echo    npm run dev
echo.
echo 3️⃣  Open in Browser:
echo    http://localhost:5173
echo.
echo 💡 Backend API Docs:
echo    http://localhost:8000/docs
echo.
echo ========================================
echo Happy Coding! 🚀
echo.

pause
