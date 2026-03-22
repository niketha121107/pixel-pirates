# DEPLOYMENT_GUIDE.md

# 🚀 Pixel Pirates - Deployment Guide

This guide covers deploying the complete Pixel Pirates system with AI integration.

---

## 📋 Prerequisites

### Required
- **Docker** (version 20.0+) - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** (version 1.29+) - Included with Docker Desktop
- **Gemini API Key** - [Get free key](https://makersuite.google.com/app/apikey)
- **MongoDB Atlas** (for production) - [Create account](https://www.mongodb.com/cloud/atlas)

### Optional
- **Git** - For version control
- **Make** - For running commands
- **curl** - For testing endpoints

---

## 🏃 Quick Start (Development)

### 1. Clone or prepare the project

```bash
cd pixel-pirates
```

### 2. Set up environment variables

**Backend (.env in backend/ directory):**
```bash
GEMINI_API_KEY=AIzaSyBEd2lFjAW1oivAXhpEN4LRcCcSjkhj_wM
MONGODB_URI=mongodb://admin:admin123@mongodb:27017/
HOST=0.0.0.0
PORT=5000
LOG_LEVEL=INFO
ENABLE_AI=true
```

**Frontend (.env.local in frontend/ directory):**
```bash
VITE_API_URL=http://localhost:5000/api
VITE_ENABLE_AI=true
VITE_ENABLE_MOCK_DATA=false
```

### 3. Start the development environment

```bash
# Using Docker Compose
docker-compose up -d

# Or using the startup script
bash start-dev.sh
```

### 4. Verify deployment

```bash
# Check services
docker-compose ps

# Test backend
curl http://localhost:5000/api/topics

# Test AI endpoint
curl http://localhost:5000/api/ai/quiz/test-ai?topic_name=Python&question_count=2

# Access frontend
open http://localhost:3000
```

---

## 🌍 Production Deployment

### 1. Set up Production Environment

Create a `.env.production` file:

```bash
# Backend
GEMINI_API_KEY=your-production-key
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/
HOST=0.0.0.0
PORT=5000
LOG_LEVEL=WARNING

# Frontend (in Dockerfile or deployment)
VITE_API_URL=https://api.yourdomain.com/api
```

### 2. Deploy to Docker

```bash
# Using the deployment script
bash deploy.sh

# Or manually
docker-compose -f docker-compose.yml up -d --build
```

### 3. Configure Production Database

**MongoDB Atlas Setup:**
1. Create free cluster at mongodb.com/cloud/atlas
2. Create user account
3. Get connection string
4. Update `MONGODB_URI` environment variable

### 4. Configure Reverse Proxy (Nginx)

Create `nginx.conf`:

```nginx
upstream backend {
    server backend:5000;
}

upstream frontend {
    server frontend:3000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 5. SSL/TLS Configuration

Use Let's Encrypt for HTTPS:

```bash
# With docker: certbot
docker run --rm \
  -v /etc/letsencrypt:/etc/letsencrypt \
  certbot/certbot certonly --standalone \
  -d yourdomain.com -d api.yourdomain.com
```

---

## 📊 Monitoring & Maintenance

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb
```

### Health Checks

```bash
# Backend health
curl http://localhost:5000/api/topics

# Frontend health
curl http://localhost:3000

# MongoDB health
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
```

### Database Backup

```bash
# Backup MongoDB
docker-compose exec mongodb mongodump --out /backup

# Restore from backup
docker-compose exec mongodb mongorestore /backup
```

### Update Services

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Or for zero-downtime update (if using Kubernetes)
kubectl rollout restart deployment/backend
```

---

## 🔧 Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Verify API key
echo $GEMINI_API_KEY

# Test Gemini connectivity
curl -X POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}' \
  -H "x-goog-api-key: YOUR_API_KEY"
```

### Frontend can't connect to backend

```bash
# Check VITE_API_URL
cat frontend/.env.local

# Verify backend is running
curl http://localhost:5000/api/topics

# Check network
docker-compose exec frontend ping backend
```

### Database connection fails

```bash
# Check MongoDB service
docker-compose logs mongodb

# Verify connection string
echo $MONGODB_URI

# Test connection
docker-compose exec mongodb mongosh "$MONGODB_URI" --eval "db.adminCommand('ping')"
```

### High memory usage

```bash
# Check resource usage
docker stats

# Limit resources in docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

---

## 🚀 Performance Optimization

### Caching

```python
# Backend - Redis caching
REDIS_URL=redis://redis:6379

# Add to docker-compose.yml
redis:
    image: redis:7-alpine
```

### Database Indexing

```javascript
// Create indexes for common queries
db.topics.createIndex({ "topicName": 1 })
db.topics.createIndex({ "language": 1 })
db.users.createIndex({ "email": 1 }, { unique: true })
```

### Frontend Optimization

```typescript
// Lazy load routes, images, components
// Use React.lazy() and Suspense
// Enable gzip compression in nginx
```

---

## 📈 Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml with multiple backend instances
backend:
  deploy:
    replicas: 3
  
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
```

### Load Balancing

Use Nginx or cloud load balancer (AWS ELB, GCP LB, etc.)

---

## 🔐 Security Checklist

- [ ] Change default MongoDB credentials
- [ ] Use strong environment variable values
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Use private container registry
- [ ] Regular security updates
- [ ] Rate limiting on API
- [ ] Input validation
- [ ] CORS configuration
- [ ] Database backups

---

## 📞 Support

For issues, check:
1. [Backend docs](backend/docs/ai-integration/README.md)
2. [Testing guide](backend/docs/ai-integration/TESTING_GUIDE.md)
3. [Troubleshooting](backend/docs/ai-integration/TROUBLESHOOTING.md)

---

## 🎯 Next Steps

1. ✅ Verify all services running
2. ✅ Test AI endpoints
3. ✅ Confirm database connectivity
4. ✅ Test frontend-backend integration
5. Implement monitoring (New Relic, DataDog)
6. Set up automated backups
7. Configure CI/CD pipeline
8. Plan scaling strategy
