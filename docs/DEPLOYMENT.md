# 🚀 Deployment Guide: Shopee Affiliate Dashboard

This guide covers the production deployment process on a Linux server (Ubuntu/Debian recommended).

## 📋 Prerequisites
- Server with strict firewall rules (Ports 80, 443, 22 open)
- Domain name pointed to server IP (e.g., `app.domain.com`)
- Docker & Docker Compose installed

## 🛠️ Step 1: Setup
1. **Clone Repository**
   ```bash
   git clone <repo_url>
   cd affiliate-dashboard
   ```

2. **Configure Environment**
   ```bash
   cp .env.production.example .env
   nano .env
   ```
   *Update `POSTGRES_PASSWORD`, `SECRET_KEY`, and `DOMAIN`.*

3. **Configure Nginx**
   Edit `nginx/nginx.conf`:
   ```bash
   nano nginx/nginx.conf
   ```
   *Replace `app.domain.com` with your actual domain name in the `server_name` and `ssl_certificate` paths.*

## 🔒 Step 2: SSL Certification (First Time)
Since Nginx needs certificates to start, we do a "fake" start first to generate them via Certbot.

1. **Start Nginx with HTTP only** (Comment out HTTPS section in `nginx.conf` temporarily or use a bootstrap config).
   *Alternative: Use Certbot standalone mode before starting Nginx:*
   ```bash
   sudo certbot certonly --standalone -d app.domain.com
   ```
   *Copy keys to `./certbot/conf` structure if needed, or map volumes to `/etc/letsencrypt`.*

2. **Recommended Certbot Flow with Docker**:
   Run the specific certbot script (if provided) or:
   ```bash
   docker compose -f docker-compose.prod.yml run --rm certbot certonly --webroot --webroot-path /var/www/certbot -d app.domain.com
   ```

## 🚀 Step 3: Launch
```bash
docker compose -f docker-compose.prod.yml up -d --build
```
This will:
1. Start Postgres
2. Build & Start Backend (Auto-runs migrations)
3. Build & Start Frontend
4. Start Nginx

## 🔍 Validation
1. Check Status: `docker compose -f docker-compose.prod.yml ps`
2. Check Logs: `docker compose -f docker-compose.prod.yml logs -f backend`
3. Access: `https://app.domain.com`
4. API Health: `https://app.domain.com/api/health`

## 📦 Maintenance
- **Backup DB**:
  ```bash
  docker compose -f docker-compose.prod.yml exec db pg_dump -U app_user affiliate_db > backup_$(date +%F).sql
  ```
- **Update App**:
  ```bash
  git pull
  docker compose -f docker-compose.prod.yml up -d --build backend frontend
  ```
- **View Logs**:
  ```bash
  docker compose -f docker-compose.prod.yml logs --tail=100 -f
  ```

## ⚠️ Troubleshooting
- **502 Bad Gateway**: Backend is starting or failed. Check `docker logs` for backend container.
- **SSL Errors**: Check cert paths in `nginx.conf` match volume mounts.
- **CORS Errors**: Ensure `DOMAIN` in `.env` matches the URL you are accessing.
