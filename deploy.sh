#!/bin/bash

# Pixel Pirates - Production Deployment

echo "🚀 Deploying Pixel Pirates to Production..."
echo ""

# Check environment variables
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY environment variable not set"
    exit 1
fi

if [ -z "$MONGODB_URI" ]; then
    echo "❌ MONGODB_URI environment variable not set"
    exit 1
fi

echo "✓ Environment variables validated"

# Build images
echo "🏗️  Building Docker images..."
docker-compose -f docker-compose.yml build --no-cache

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

echo "✓ Build completed"

# Start services
echo "🐳 Starting services..."
docker-compose -f docker-compose.yml up -d

# Wait for services
echo "⏳ Waiting for services to be ready..."
sleep 5

# Health checks
echo "🏥 Performing health checks..."

# Check MongoDB
if docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo "✓ MongoDB is healthy"
else
    echo "❌ MongoDB health check failed"
    exit 1
fi

# Check Backend
for i in {1..20}; do
    if curl -s http://localhost:5000/api/topics > /dev/null 2>&1; then
        echo "✓ Backend is healthy"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "❌ Backend health check failed"
        docker-compose logs backend | tail -20
        exit 1
    fi
    sleep 1
done

# Check Frontend
for i in {1..20}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✓ Frontend is healthy"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "⚠️  Frontend startup slower than expected"
    fi
    sleep 2
done

echo ""
echo "✅ Production deployment successful!"
echo ""
echo "📍 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:5000"
echo ""
echo "📊 To view logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 To stop deployment:"
echo "   docker-compose down"
echo ""
