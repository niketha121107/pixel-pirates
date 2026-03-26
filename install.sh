#!/bin/bash

# ========================================
# Pixel Pirates - Automated Setup Script
# ========================================

set -e  # Exit on error

echo "🚀 Starting Pixel Pirates Setup"
echo "========================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

echo "✅ Python version: $(python3 --version)"
echo "✅ Node version: $(node --version)"
echo "✅ npm version: $(npm --version)"
echo ""

# ========================================
# Backend Setup
# ========================================
echo "📦 Setting up Backend..."
echo "========================================"

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "🔧 Creating Python virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate

# Install backend dependencies
echo "📥 Installing backend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📋 Copying .env.example to .env"
        cp .env.example .env
        echo "⚠️  Please update .env with your API keys:"
        echo "   - YOUTUBE_API_KEY"
        echo "   - GEMINI_API_KEY"
        echo "   - MONGODB_URL"
        echo "   - JWT_SECRET_KEY"
    fi
fi

echo "✅ Backend setup completed"
echo ""

# ========================================
# Frontend Setup
# ========================================
echo "🎨 Setting up Frontend..."
echo "========================================"

cd ../frontend

# Install frontend dependencies
echo "📥 Installing frontend dependencies..."
npm install

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "📋 Creating .env.local"
    echo "VITE_API_URL=http://localhost:8000/api" > .env.local
    echo "✅ .env.local created with default API URL"
fi

echo "✅ Frontend setup completed"
echo ""

# ========================================
# Summary
# ========================================
echo "========================================"
echo "✨ Setup Complete!"
echo "========================================"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1️⃣  Backend Setup:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   # Update .env with your API keys"
echo "   python main.py"
echo ""
echo "2️⃣  Frontend Setup (new terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3️⃣  Open in Browser:"
echo "   http://localhost:5173"
echo ""
echo "💡 Backend API Docs:"
echo "   http://localhost:8000/docs"
echo ""
echo "========================================"
echo "Happy Coding! 🚀"
