#!/bin/bash

# Pixel Pirates - Full Stack Development Startup

echo "🚀 Starting Pixel Pirates Development Environment..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Create .env if it doesn't exist
if [ ! -f frontend/.env.local ]; then
    echo "📝 Creating frontend .env.local..."
    cat > frontend/.env.local << EOF
VITE_API_URL=http://localhost:5000/api
VITE_ENABLE_AI=true
VITE_ENABLE_MOCK_DATA=false
EOF
fi

if [ ! -f backend/.env.local ]; then
    echo "📝 Creating backend .env.local..."
    echo "⚠️  Please update backend/.env.local with your GEMINI_API_KEY"
    cat > backend/.env.local << EOF
GEMINI_API_KEY=your-api-key-here
MONGODB_URI=mongodb://localhost:27017/
HOST=0.0.0.0
PORT=5000
LOG_LEVEL=INFO
ENABLE_AI=true
EOF
fi

# Start services
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 3

# Check backend health
echo "✓ Checking backend health..."
for i in {1..10}; do
    if curl -s http://localhost:5000/api/topics > /dev/null 2>&1; then
        echo "✓ Backend is ready"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "❌ Backend failed to start"
        docker-compose logs backend
        exit 1
    fi
    sleep 2
done

# Check frontend
echo "✓ Checking frontend..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✓ Frontend is ready"
else
    echo "⏳ Frontend is starting... (usually takes 10-15 seconds)"
    for i in {1..30}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            echo "✓ Frontend is ready"
            break
        fi
        sleep 1
    done
fi

echo ""
echo "✅ All services are running!"
echo ""
echo "📍 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:5000"
echo ""
echo "📚 API Documentation:"
echo "   GET  http://localhost:5000/api/topics"
echo "   GET  http://localhost:5000/api/ai/quiz/test-ai?topic_name=Python&question_count=2"
echo ""
echo "🐳 Docker Management:"
echo "   View logs:      docker-compose logs -f [service]"
echo "   Stop services:  docker-compose down"
echo "   Stop & cleanup: docker-compose down -v"
echo ""
