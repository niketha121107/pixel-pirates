#!/bin/bash
# 🚀 PIXEL PIRATES - COMMAND REFERENCE GUIDE
# Save this file and run commands from it

# ==============================================================================
# SETUP & VERIFICATION
# ==============================================================================

# Check if everything is ready
echo "=== VERIFY SETUP ==="
cd backend
python verify_setup.py

# ==============================================================================
# CONTENT GENERATION (Choose One)
# ==============================================================================

# RECOMMENDED: Full automated pipeline
echo "=== GENERATE ALL CONTENT (RECOMMENDED) ==="
python generate_all_content.py

# OR: Step by step
echo "=== STEP 1: Generate Topics ==="
python verify_and_generate_topics.py

echo "=== STEP 2: Generate All Content ==="
python generate_complete_content.py

# ==============================================================================
# START APPLICATION
# ==============================================================================

# Start backend
echo "=== START BACKEND ==="
python main.py

# In another terminal, start frontend:
echo "=== START FRONTEND ==="
cd ../frontend
npm run dev

# ==============================================================================
# VERIFY GENERATION
# ==============================================================================

# Check statistics
echo "=== CHECK GENERATION STATS ==="
curl http://localhost:8000/api/content/statistics

# ==============================================================================
# DATABASE OPERATIONS
# ==============================================================================

# Connect to MongoDB
echo "=== CONNECT TO MONGODB ==="
mongosh

# Count topics
# db.topics.count()

# Get one topic
# db.topics.findOne()

# ==============================================================================
# DEBUG & TROUBLESHOOTING
# ==============================================================================

# Run setup check again
echo "=== DEBUG: Check Setup ==="
python verify_setup.py

# Get full log output
echo "=== DEBUG: Full Generation Log ==="
python generate_all_content.py 2>&1 | tee generation.log

# Check last errors
echo "=== DEBUG: Check Errors ==="
grep -i "error\|failed" generation.log

# ==============================================================================
# USEFUL COMMANDS
# ==============================================================================

# Check Python version
python --version

# List installed packages
pip list | grep -E "fastapi|motor|google|httpx|reportlab"

# Check if MongoDB is running
mongosh --eval "db.version()"

# View environment variables
echo $GEMINI_API_KEY
echo $YOUTUBE_API_KEY

# ==============================================================================
# FRONTEND DEVELOPMENT
# ==============================================================================

# Install dependencies
npm install

# Dev mode
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# ==============================================================================
# DOCKER OPERATIONS (if using Docker)
# ==============================================================================

# Start MongoDB in Docker
docker run -d -p 27017:27017 --name mongodb mongo

# Stop MongoDB
docker stop mongodb

# Remove MongoDB container
docker rm mongodb

# ==============================================================================
# QUICK CHECKS
# ==============================================================================

# Is MongoDB running?
echo "Checking MongoDB..."
python -c "from pymongo import MongoClient; print('✅ MongoDB OK' if MongoClient('mongodb://localhost:27017/').server_info() else print('❌ MongoDB FAIL'))"

# Are API keys set?
echo "Checking API keys..."
[ -z "$GEMINI_API_KEY" ] && echo "❌ GEMINI_API_KEY not set" || echo "✅ GEMINI_API_KEY set"
echo "✅ YOUTUBE_API_KEY provided"

# ==============================================================================
# MONITORING GENERATION
# ==============================================================================

# Watch generation progress (in separate terminal)
watch -n 5 'python -c "
import asyncio
from app.core.database import db, connect_to_mongo
from app.core.config import settings

async def check():
    await connect_to_mongo(settings)
    total = db.database[\"topics\"].count_documents({})
    complete = db.database[\"topics\"].count_documents({\"contentStatus\": \"complete\"})
    print(f\"Progress: {complete}/{total}\")

asyncio.run(check())
"'

# ==============================================================================
# COMMON ISSUES & FIXES
# ==============================================================================

# MongoDB not found
# FIX: mongod

# API key missing
# FIX: Add to .env and reload terminal

# YouTube quota exceeded
# FIX: Wait 24 hours or use different key

# Slow generation
# FIX: Check internet, reduce concurrency

# PDF not saving
# FIX: mkdir -p storage/pdfs

# Package not found
# FIX: pip install -r requirements.txt

# ==============================================================================
# TESTING ENDPOINTS (using curl)
# ==============================================================================

# Get all topics
curl http://localhost:8000/api/topics

# Get specific topic (replace ID)
curl http://localhost:8000/api/content/complete/python_1

# Get videos
curl http://localhost:8000/api/content/videos/python_1

# Get explanations
curl http://localhost:8000/api/content/explanations/python_1

# Get mock test
curl http://localhost:8000/api/content/mock-tests/python_1

# Get statistics
curl http://localhost:8000/api/content/statistics

# ==============================================================================
# DOCUMENTATION
# ==============================================================================

# View quick reference
cat QUICK_REFERENCE.md

# View generation guide
cat README_GENERATION.md

# View complete guide
cat CONTENT_GENERATION_GUIDE.md

# View implementation summary
cat IMPLEMENTATION_SUMMARY.md

# View completion checklist
cat COMPLETION_CHECKLIST.md

# ==============================================================================
# PRODUCTION DEPLOYMENT CHECKLIST
# ==============================================================================

# 1. Update environment variables
# - Set GEMINI_API_KEY to production key
# - Update MONGODB_URL to production database
# - Set DEBUG=False

# 2. Install production packages
pip install gunicorn

# 3. Start with production server
gunicorn main:app --workers 4

# 4. Set up error monitoring (optional)
# - Sentry
# - DataDog
# - CloudWatch

# 5. Enable HTTPS
# - Get SSL certificate
# - Update server config

# ==============================================================================
# PERFORMANCE OPTIMIZATION
# ==============================================================================

# Increase generation concurrency (careful!)
# Edit generate_complete_content.py
# sem = asyncio.Semaphore(5)  # More parallel

# Add caching to API responses
# Use Redis or similar

# Enable database indexing
# db.topics.createIndex({"contentStatus": 1})

# ==============================================================================
# BACKUP & MAINTENANCE
# ==============================================================================

# Backup MongoDB
mongodump --uri="mongodb://localhost:27017/pixel_pirates"

# Restore MongoDB
mongorestore --uri="mongodb://localhost:27017/" ./dump

# Clean up old PDFs
find storage/pdfs -type f -mtime +30 -delete

# ==============================================================================
# HELP & SUPPORT
# ==============================================================================

# View API documentation
# Open http://localhost:8000/docs in browser

# Check logs
tail -f generation.log

# Search for errors
grep -i error generation.log

# Count API calls
grep -c "API\|Generating" generation.log

# ==============================================================================
# SUMMARY OF KEY COMMANDS
# ==============================================================================

# Three command setup:
cd backend
python verify_setup.py
python generate_all_content.py
python main.py

# Then access:
# Backend: http://localhost:8000/docs
# Frontend: http://localhost:5173

# ==============================================================================
# END OF REFERENCE GUIDE
# ==============================================================================
