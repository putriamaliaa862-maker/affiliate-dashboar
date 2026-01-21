# 🚂 DEPLOY BACKEND KE RAILWAY

> **Step-by-step guide untuk deploy FastAPI backend ke Railway**

---

## 📋 PREREQUISITES

Sebelum mulai, pastikan sudah punya:
- ✅ Supabase database sudah setup (sudah selesai!)
- ✅ GitHub repo dengan code backend
- ✅ Railway account (sign up di https://railway.app)

---

## 🚀 STEP 1: Connect GitHub ke Railway

### 1.1. Login Railway

1. Buka https://railway.app
2. Sign up / Login (bisa pakai GitHub account)
3. Click **"New Project"**

### 1.2. Deploy from GitHub

1. Pilih **"Deploy from GitHub repo"**
2. Authorize Railway untuk akses GitHub (jika pertama kali)
3. Pilih repository: `affiliate-dashboard`
4. Railway akan auto-detect FastAPI

---

## ⚙️ STEP 2: Configure Service

### 2.1. Set Root Directory

1. Klik service yang terbuat
2. Buka **Settings** → **Root Directory**
3. Set: `backend`
4. Save

### 2.2. Configure Build & Start Commands

1. Buka **Settings** → **Deploy**
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Save

---

## 🔐 STEP 3: Set Environment Variables

### 3.1. Buka Variables Tab

1. Di Railway service page
2. Klik tab **"Variables"**
3. Click **"New Variable"**

### 3.2. Add Environment Variables

Add semua variables berikut:

```env
# Database - Supabase
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres

# Supabase Config
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...

# Security
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Shopee API (optional)
SHOPEE_PARTNER_ID=your-partner-id
SHOPEE_PARTNER_KEY=your-partner-key
SHOPEE_SYNC_API_KEY=your-sync-key
ACCESS_CODE=your-access-code

# Application
APP_NAME=Affiliate Dashboard
DEBUG=False
```

**Cara ambil values:**

**DATABASE_URL:**
- Supabase Dashboard → Settings → Database
- Copy **Connection string** (Pooler mode, port 6543)
- Format: `postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres`

**SUPABASE_URL:**
- Supabase Dashboard → Settings → API
- Copy **Project URL**: `https://xxxxx.supabase.co`

**SUPABASE_ANON_KEY:**
- Supabase Dashboard → Settings → API
- Copy **anon public** key

**SUPABASE_SERVICE_ROLE_KEY:**
- Supabase Dashboard → Settings → API
- Copy **service_role** key (JANGAN EXPOSE!)

**SECRET_KEY:**
- Generate random string: `openssl rand -hex 32`
- Atau pakai online generator

---

## 🚀 STEP 4: Deploy

### 4.1. Trigger Deploy

1. Railway akan auto-deploy setelah push ke GitHub
2. Atau klik **"Deploy"** manual
3. Tunggu build complete (~2-3 menit)

### 4.2. Get Public URL

1. Klik **Settings** → **Generate Domain**
2. Railway akan generate URL: `https://your-app.up.railway.app`
3. **Copy URL ini!** Akan dipakai untuk frontend

---

## ✅ STEP 5: Verify Deployment

### 5.1. Test Health Endpoint

```bash
curl https://your-app.up.railway.app/health
```

Response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "docs": "/docs"
}
```

### 5.2. Test API Docs

1. Buka: `https://your-app.up.railway.app/docs`
2. Harusnya muncul Swagger UI
3. Test endpoint `/health`

### 5.3. Check Logs

1. Railway Dashboard → **Deployments** tab
2. Klik deployment terbaru
3. Cek logs untuk error

---

## 🔧 STEP 6: Fix Common Issues

### Issue 1: Build Failed

**Error:** `ModuleNotFoundError` atau import error

**Solution:**
- Cek `requirements.txt` sudah ada semua dependencies
- Pastikan `Root Directory` set ke `backend`
- Re-deploy

### Issue 2: Database Connection Failed

**Error:** `Connection refused` atau `authentication failed`

**Solution:**
- Double check `DATABASE_URL` format benar
- Pastikan password tidak ada spaces di awal/akhir
- Test connection string dari local dulu

### Issue 3: Port Error

**Error:** `Address already in use`

**Solution:**
- Pastikan start command pakai `$PORT` variable
- Railway auto-inject PORT variable
- Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## 📊 STEP 7: Monitor & Logs

### View Logs

1. Railway Dashboard → **Deployments**
2. Click deployment
3. View **Logs** tab
4. Real-time logs tersedia

### Monitor Usage

1. Dashboard → **Usage** tab
2. Monitor:
   - CPU usage
   - Memory usage
   - Network bandwidth
   - Credit usage ($5 free/month)

---

## 🔄 STEP 8: Auto-Deploy Setup

### Enable Auto-Deploy

Railway otomatis deploy ketika:
- Push ke `main` branch (default)
- Atau branch yang di-set di Settings

### Manual Deploy

1. Dashboard → **Deployments**
2. Click **"Redeploy"**
3. Pilih commit yang mau di-deploy

---

## 💰 COST MONITORING

### Free Tier

- **$5 credit/bulan** (gratis)
- Pay-per-use pricing
- Auto-pause jika tidak dipakai

### Estimated Cost

- **Development/Testing:** $0-2/bulan
- **Production (24/7):** $8-10/bulan (512MB RAM)

### Monitor Credit

1. Dashboard → **Usage**
2. Cek **Credit Used**
3. Set **Budget Alerts** jika perlu

---

## ✅ CHECKLIST

- [ ] ✅ Railway project created
- [ ] ✅ GitHub repo connected
- [ ] ✅ Root directory set ke `backend`
- [ ] ✅ Build & start commands configured
- [ ] ✅ Environment variables set (all)
- [ ] ✅ Deployment successful
- [ ] ✅ Health endpoint working
- [ ] ✅ API docs accessible
- [ ] ✅ Logs no errors

---

## 🎯 NEXT STEPS

Setelah backend deployed:

1. ✅ **Update Frontend Config**
   - Set `VITE_API_URL` ke Railway URL
   - Deploy frontend ke Vercel

2. ✅ **Update Extension**
   - Set API endpoint ke Railway URL
   - Test extension post ke Supabase

3. ✅ **Test End-to-End**
   - Extension → Supabase → Backend → Frontend

---

**Backend URL:** `https://your-app.up.railway.app`  
**API Docs:** `https://your-app.up.railway.app/docs`  
**Health Check:** `https://your-app.up.railway.app/health`

---

**Status:** Ready untuk Deploy! 🚀