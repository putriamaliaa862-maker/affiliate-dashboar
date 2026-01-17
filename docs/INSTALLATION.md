# INSTALLATION & TROUBLESHOOTING GUIDE

## ⚙️ System Requirements

### Minimum Requirements
- CPU: 2 cores
- RAM: 2GB
- Disk: 1GB
- OS: Linux, macOS, or Windows (WSL2)

### Required Software
- Docker & Docker Compose (Recommended)
- OR: Python 3.11+, Node.js 18+, PostgreSQL 15+

---

## 🔧 Installation Options

### Option 1: Docker Compose (Recommended - Easiest)

#### Prerequisites
```bash
# Check if Docker is installed
docker --version
docker-compose --version

# If not installed, download from https://www.docker.com/products/docker-desktop
```

#### Installation Steps

1. **Clone/Download Project**
```bash
cd affiliate-dashboard
```

2. **Setup Environment**
```bash
cp backend/.env.example backend/.env

# Optional: Edit .env untuk Shopee credentials
# SHOPEE_PARTNER_ID=your_id
# SHOPEE_PARTNER_KEY=your_key
```

3. **Start Services**
```bash
docker-compose up --build
```

Wait untuk semua services startup (PostgreSQL, Backend, Frontend).

4. **Verify Installation**
```bash
# Terminal baru, check containers
docker-compose ps

# Test API
curl http://localhost:8000/health
# Expected: {"status":"ok"}

# Open browser
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs
```

✅ **Installation Complete!**

---

### Option 2: Local Development (Python + Node.js)

#### Prerequisites
```bash
# Check Python 3.11+
python --version
python -m pip --version

# Check Node.js 18+
node --version
npm --version

# Install PostgreSQL 15+
# https://www.postgresql.org/download/
```

#### Backend Setup

1. **Navigate to backend**
```bash
cd backend
```

2. **Create virtual environment**
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup database**
```bash
# Create PostgreSQL database
psql -U postgres
CREATE DATABASE affiliate_dashboard;
\q

# Update .env
cp .env.example .env
# Edit DATABASE_URL=postgresql://user:password@localhost:5432/affiliate_dashboard
```

5. **Run backend**
```bash
uvicorn app.main:app --reload
# API running at http://localhost:8000
# Docs at http://localhost:8000/docs
```

#### Frontend Setup

1. **Open new terminal, navigate to frontend**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Run frontend**
```bash
npm run dev
# Frontend running at http://localhost:5173
```

✅ **Installation Complete!**

---

## 🧪 Testing Installation

### Verify Services Are Running

```bash
# Test Backend Health
curl http://localhost:8000/health
# Expected: {"status":"ok"}

# Test API (list studios)
curl http://localhost:8000/api/studios
# Expected: [] or existing studios

# Test Frontend
curl http://localhost:5173
# Expected: HTML response
```

### Run Test Script
```bash
# Make sure backend is running
python test_api.py
# Should show all tests passing ✓
```

---

## ❌ Troubleshooting

### Docker Issues

#### Issue: `docker-compose: command not found`
**Solution:**
```bash
# Install Docker Compose V2
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

#### Issue: `Permission denied while trying to connect to Docker`
**Solution (Linux):**
```bash
sudo usermod -aG docker $USER
newgrp docker
# Logout and login again
```

#### Issue: Ports already in use
**Solution:**
```bash
# Check which process is using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

#### Issue: Database connection failed
**Solution:**
```bash
# Check PostgreSQL container is running
docker-compose ps

# Check logs
docker-compose logs db

# Rebuild container
docker-compose down
docker-compose up --build
```

### Backend Issues

#### Issue: `ModuleNotFoundError: No module named 'app'`
**Solution:**
```bash
# Make sure you're in backend directory
cd backend

# Install requirements again
pip install -r requirements.txt

# Run from backend directory
uvicorn app.main:app --reload
```

#### Issue: Database connection refused
**Solution:**
```bash
# Check PostgreSQL is running
psql -U postgres -l

# If not, install and start PostgreSQL
# https://www.postgresql.org/download/

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@localhost:5432/affiliate_dashboard

# Try again
uvicorn app.main:app --reload
```

#### Issue: Port 8000 already in use
**Solution:**
```bash
# Use different port
uvicorn app.main:app --reload --port 8001
```

### Frontend Issues

#### Issue: `npm: command not found`
**Solution:**
```bash
# Install Node.js from https://nodejs.org/
# Then test
node --version
npm --version
```

#### Issue: Modules not found
**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### Issue: Cannot connect to API (404 errors)
**Solution:**
```bash
# Check backend is running on port 8000
curl http://localhost:8000/health

# Check vite.config.ts proxy settings point to 8000
# Check CORS is enabled in backend

# Try direct API call
curl http://localhost:8000/api/studios
```

#### Issue: Port 5173 already in use
**Solution:**
```bash
cd frontend
npm run dev -- --port 5174
# Or edit vite.config.ts
server:
  port: 5174
```

### Common Issues

#### Issue: `.env` file not found
**Solution:**
```bash
# Copy template
cp backend/.env.example backend/.env

# Edit with values
nano backend/.env  # or use your editor
```

#### Issue: CORS errors in browser console
**Solution:**
```
# Backend main.py already has CORS enabled
# If still error, check:
# 1. Backend is running
# 2. Frontend URL is in allow_origins
# 3. API proxy is configured in vite.config.ts
```

#### Issue: Database tables not created
**Solution:**
```bash
# Backend creates tables on startup
# If error, check:
# 1. PostgreSQL is running
# 2. Database exists
# 3. DATABASE_URL is correct

# Manual database creation:
createdb -U postgres affiliate_dashboard
```

---

## 📋 Pre-Flight Checklist

Before going live:

- [ ] Docker installed and working
- [ ] All services start without errors
- [ ] Backend health check passes (http://localhost:8000/health)
- [ ] Frontend loads (http://localhost:5173)
- [ ] API documentation available (http://localhost:8000/docs)
- [ ] Database tables created
- [ ] Test API script runs successfully
- [ ] Environment variables configured
- [ ] Shopee credentials (if integrating) are valid

---

## 🚀 Next Steps

1. **Read Quick Start**
   ```bash
   cat QUICKSTART.md
   ```

2. **Test the API**
   ```bash
   python test_api.py
   ```

3. **Read API Documentation**
   ```bash
   cat API_DOCUMENTATION.md
   ```

4. **Deploy to Production**
   ```bash
   cat DEPLOYMENT.md
   ```

---

## 💬 Getting Help

### Check Logs
```bash
# Docker Compose
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# Local development
# Terminal 1 (backend)
uvicorn app.main:app --reload

# Terminal 2 (frontend)
npm run dev
```

### Test API Manually
```bash
# List all studios
curl -X GET http://localhost:8000/api/studios

# Access Swagger UI
open http://localhost:8000/docs
```

### Debug Mode
```bash
# Backend debug
export DEBUG=True
uvicorn app.main:app --reload

# Frontend debug
npm run dev -- --host
```

---

## 📞 Support Resources

- **API Docs**: http://localhost:8000/docs
- **Project Docs**: See README.md, QUICKSTART.md, API_DOCUMENTATION.md
- **Test Script**: python test_api.py
- **Docker Logs**: docker-compose logs -f
- **Python Version**: python --version (needs 3.11+)
- **Node Version**: node --version (needs 18+)

---

## ✅ Verification Checklist

Run these commands to verify everything works:

```bash
# 1. Docker running
docker ps

# 2. Containers started
docker-compose ps
# Should show: db, backend, frontend all UP

# 3. API responding
curl http://localhost:8000/health

# 4. Frontend loaded
curl http://localhost:5173 | head -20

# 5. Database connected
curl http://localhost:8000/api/studios

# 6. API Docs accessible
open http://localhost:8000/docs
```

All showing success? ✅ **You're ready to use Affiliate Dashboard!**

---

## 📞 Emergency Restart

If something goes wrong:

```bash
# Stop everything
docker-compose down

# Remove volumes (careful - this deletes data!)
docker-compose down -v

# Clean rebuild
docker-compose up --build

# Check status
docker-compose ps
docker-compose logs
```

---

**Last Updated**: January 13, 2026
**Version**: 0.1.0
