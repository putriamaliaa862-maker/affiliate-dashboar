# SHOPEE LIVE INTEGRATION - DEPLOYMENT CHECKLIST

## Pre-Deployment Verification

### ✅ Backend Verification

- [x] All 51 routes registered
- [x] 3 new database models created
  - [x] LiveSession
  - [x] LiveSessionItem
  - [x] LiveAnalytics
- [x] ShopeeStreamingService with 22 methods
- [x] Async/await implementation
- [x] Error handling & logging
- [x] Dependencies installed

**Verification Command:**
```bash
cd backend
python -c "
from app.main import app
print(f'Routes: {len(app.routes)}')
"
# Expected: Routes: 51
```

### ✅ Frontend Verification

- [x] React app compiles
- [x] Vite config correct
- [x] TypeScript strict mode
- [x] TailwindCSS configured
- [x] API client ready

**Verification Command:**
```bash
cd frontend
npm run build
# Expected: Successful build to dist/
```

### ✅ Database Verification

- [x] PostgreSQL schema ready
- [x] All migrations prepared
- [x] Relationships defined
- [x] Indexes created
- [x] Foreign keys validated

**Verification Command:**
```bash
docker-compose exec postgres psql -U postgres -d affiliate_dashboard -c "
SELECT tablename FROM pg_tables WHERE schemaname = 'public';
"
# Expected: 12 tables listed
```

### ✅ Documentation Verification

- [x] SHOPEE_LIVE_INTEGRATION.md (complete guide)
- [x] SHOPEE_LIVE_API_QUICK_REFERENCE.md (quick start)
- [x] SHOPEE_LIVE_INTEGRATION_SUMMARY.md (summary)
- [x] SYSTEM_ARCHITECTURE.md (architecture)
- [x] demo_shopee_live.py (working demo)

## Pre-Launch Checklist

### Configuration

- [ ] Copy `.env.example` to `.env`
- [ ] Set required environment variables:
  ```env
  DATABASE_URL=postgresql://postgres:password@localhost:5432/affiliate_dashboard
  SHOPEE_PARTNER_ID=your_partner_id
  SHOPEE_PARTNER_KEY=your_partner_key
  SECRET_KEY=your_secret_key_here
  DEBUG=false  # Set to false for production
  ```
- [ ] Verify all endpoints accessible
- [ ] Test Shopee API connectivity

### Database Setup

- [ ] PostgreSQL running (Docker or local)
- [ ] Database created: `affiliate_dashboard`
- [ ] Tables auto-created by SQLAlchemy
- [ ] Test table creation with:
  ```bash
  docker-compose up db
  # Wait for PostgreSQL to start
  ```

### Local Testing

- [ ] Backend starts: `uvicorn app.main:app --reload`
- [ ] Frontend starts: `npm run dev`
- [ ] API accessible at http://localhost:8000
- [ ] Dashboard accessible at http://localhost:5173
- [ ] Health check passes: `curl http://localhost:8000/health`

### Docker Setup

- [ ] Docker installed
- [ ] Docker Compose installed
- [ ] `.dockerignore` configured
- [ ] Dockerfile(s) functional
- [ ] `docker-compose.yml` complete
- [ ] Build success: `docker-compose build`

### Testing

- [ ] Run demo script: `python demo_shopee_live.py`
- [ ] Test session creation
- [ ] Test session sync (with mock token)
- [ ] Test analytics endpoints
- [ ] Test utility endpoints (share links, product URLs)

## Launch Steps

### Step 1: Local Docker Launch (5 minutes)

```bash
# Navigate to project
cd /workspace/affiliate-dashboard

# Build images
docker-compose build

# Start services
docker-compose up -d

# Wait for startup
sleep 5

# Verify services running
docker-compose ps

# Check logs
docker-compose logs -f backend
```

**Expected Output:**
```
postgres     running on port 5432
backend      running on port 8000
frontend     running on port 5173
```

### Step 2: Backend Verification (2 minutes)

```bash
# Check health
curl http://localhost:8000/health

# List routes
curl http://localhost:8000/api/studios

# Expected: Success responses
```

### Step 3: Frontend Access (1 minute)

```bash
# Open browser
http://localhost:5173

# Expected: Dashboard loads successfully
```

### Step 4: Run Demo (2 minutes)

```bash
cd /workspace/affiliate-dashboard
python demo_shopee_live.py

# Expected: All demos pass
```

## Production Deployment

### AWS ECS Deployment

```bash
# 1. Create ECR repositories
aws ecr create-repository --repository-name affiliate-backend
aws ecr create-repository --repository-name affiliate-frontend

# 2. Build and push images
docker build -t affiliate-backend ./backend
docker tag affiliate-backend:latest <account>.dkr.ecr.<region>.amazonaws.com/affiliate-backend:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/affiliate-backend:latest

# 3. Create RDS PostgreSQL database
aws rds create-db-instance --db-instance-identifier affiliate-db --db-instance-class db.t3.micro ...

# 4. Create ECS cluster and services
# (Use AWS Console or terraform)

# 5. Configure DNS
# Point domain to ECS load balancer
```

### Heroku Deployment

```bash
# 1. Install Heroku CLI
curl https://cli.heroku.com/install.sh | sh

# 2. Login
heroku login

# 3. Create app
heroku create affiliate-dashboard

# 4. Add PostgreSQL addon
heroku addons:create heroku-postgresql:standard-0

# 5. Set environment variables
heroku config:set SHOPEE_PARTNER_ID=your_id
heroku config:set SHOPEE_PARTNER_KEY=your_key

# 6. Deploy
git push heroku main
```

### VPS Deployment (Ubuntu 22.04)

```bash
#!/bin/bash
# 1. Install dependencies
sudo apt-get update
sudo apt-get install -y docker.io docker-compose nginx

# 2. Clone repository
git clone https://github.com/your/repo.git
cd affiliate-dashboard

# 3. Setup SSL with Let's Encrypt
sudo apt-get install -y certbot python3-certbot-nginx

# 4. Configure Nginx reverse proxy
sudo cp nginx.conf /etc/nginx/sites-available/affiliate
sudo ln -s /etc/nginx/sites-available/affiliate /etc/nginx/sites-enabled/
sudo systemctl reload nginx

# 5. Start services
docker-compose -f docker-compose.prod.yml up -d

# 6. Setup monitoring
docker run -d -p 9090:9090 prom/prometheus
```

## Post-Deployment Verification

### Health Checks

```bash
# API health
curl https://your-domain.com/health

# List studios
curl https://your-domain.com/api/studios

# List sessions
curl https://your-domain.com/api/live-streaming/sessions

# Get analytics
curl "https://your-domain.com/api/live-streaming/analytics/summary?studio_id=1&days=30"
```

### Performance Checks

```bash
# Response time test
curl -w "@curl-format.txt" -o /dev/null -s https://your-domain.com/health

# Load test (optional, using Apache Bench)
ab -n 100 -c 10 https://your-domain.com/health

# Expected: < 100ms response time
```

### Database Checks

```bash
# Connect to database
psql -h your-rds-endpoint.amazonaws.com -U postgres -d affiliate_dashboard

# Check tables
\dt

# Check table sizes
SELECT tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables 
WHERE schemaname = 'public';

# Check indexes
\di
```

### Log Review

```bash
# Backend logs
docker logs -f affiliate-dashboard-backend-1

# Database logs
docker logs -f affiliate-dashboard-postgres-1

# Frontend logs (if in container)
docker logs -f affiliate-dashboard-frontend-1

# Check for errors
grep "ERROR" backend.log
```

## Shopee Integration Enablement

### Step 1: Get Shopee Partner Credentials

1. Register at https://partner.shopee.com/
2. Create Partner API app
3. Get `PARTNER_ID` and `PARTNER_KEY`
4. Set in `.env`:
   ```env
   SHOPEE_PARTNER_ID=your_partner_id
   SHOPEE_PARTNER_KEY=your_partner_key
   ```

### Step 2: Setup OAuth Flow

1. Implement QR code login endpoint
2. Store `access_token`, `refresh_token` in database
3. Implement token refresh logic
4. Test with: `python demo_shopee_live.py --token YOUR_TOKEN`

### Step 3: Enable Auto-Sync

```python
# In backend/app/services/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('interval', minutes=5)
async def sync_live_sessions():
    """Auto-sync live sessions every 5 minutes"""
    sessions = get_active_sessions()
    for session in sessions:
        await shopee_streaming_service.sync_session(session)

scheduler.start()
```

### Step 4: Configure Webhooks (Optional)

```python
# Shopee can send webhooks on session events
@app.post("/webhooks/shopee/session-ended")
async def handle_session_ended(data: dict):
    session_id = data['session_id']
    # Handle session end
    update_session_status(session_id, 'ended')
```

## Monitoring & Alerts

### Setup Monitoring

```bash
# Install Datadog agent (optional)
DD_AGENT_MAJOR_VERSION=7 \
DD_API_KEY=your_api_key \
DD_SITE=datadoghq.com \
bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_mac_os.sh)"

# Or use CloudWatch
aws cloudwatch put-metric-alarm \
  --alarm-name high-api-latency \
  --alarm-description "Alert when API response time > 1000ms" \
  --metric-name ResponseTime \
  --namespace "AffiliateAPI" \
  --statistic Average \
  --period 300 \
  --threshold 1000 \
  --comparison-operator GreaterThanThreshold
```

### Setup Alerts

```bash
# Email alerts for errors
# Configure in monitoring tool:
# - Alert on error rate > 5%
# - Alert on API latency > 1000ms
# - Alert on database connection issues
# - Alert on disk space < 10%
```

## Rollback Plan

### If Issues Occur

```bash
# View previous versions
docker images | grep affiliate

# Rollback to previous version
docker tag affiliate-backend:previous affiliate-backend:latest
docker-compose up -d backend

# Alternatively, use git
git log --oneline
git revert <commit-hash>
git push

# Restart services
docker-compose restart backend
```

## Documentation for Users

### For Admin/Operations

- [x] SHOPEE_LIVE_INTEGRATION_SUMMARY.md - Overview
- [x] SHOPEE_LIVE_API_QUICK_REFERENCE.md - API Reference
- [x] DEPLOYMENT.md - Deployment Guide
- [x] INSTALLATION.md - Installation & Troubleshooting

### For Developers

- [x] SYSTEM_ARCHITECTURE.md - Architecture
- [x] SHOPEE_LIVE_INTEGRATION.md - Complete Integration Guide
- [x] API_DOCUMENTATION.md - API Details
- [x] Code comments & docstrings

## Launch Success Criteria

✅ **Must Have (All Required)**
- [ ] All 51 routes working
- [ ] Database tables created successfully
- [ ] Frontend loads without errors
- [ ] Backend API responds to requests
- [ ] Health check endpoint functional
- [ ] Demo script runs successfully

✅ **Should Have (Recommended)**
- [ ] Shopee API credentials configured
- [ ] OAuth flow tested
- [ ] Analytics endpoints working
- [ ] Session sync tested
- [ ] Logging configured
- [ ] Monitoring enabled

✅ **Nice to Have (Optional)**
- [ ] SSL certificate configured
- [ ] CDN setup
- [ ] Rate limiting enabled
- [ ] Caching layer active
- [ ] CI/CD pipeline running
- [ ] Automated backups configured

## Timeline Estimate

| Task | Estimated Time |
|------|-----------------|
| Local testing | 15 minutes |
| Docker setup | 20 minutes |
| Demo verification | 10 minutes |
| Shopee credential setup | 30 minutes |
| Production deployment | 1-2 hours |
| Monitoring setup | 30 minutes |
| Documentation review | 20 minutes |
| **Total** | **3-4 hours** |

## Support Contacts

- **Technical Issues**: Review documentation files
- **Shopee API Issues**: https://merchant.shopee.com/support
- **Database Issues**: PostgreSQL docs + DBA review
- **Deployment Issues**: Docker docs + DevOps review

## Sign-Off

- [ ] Product Owner: Verified requirements met
- [ ] Tech Lead: Code reviewed & approved
- [ ] QA: Testing complete
- [ ] DevOps: Deployment approved
- [ ] Security: Security review passed

---

**Version**: 1.0  
**Last Updated**: November 2025  
**Status**: 🚀 Ready for Launch

**Next Steps**: Follow "Launch Steps" section above
