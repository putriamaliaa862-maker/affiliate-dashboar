# 🚀 MIGRATION GUIDE: Supabase + Railway + Vercel

> **Complete step-by-step guide untuk migrate affiliate dashboard ke Supabase**

---

## 📋 PREREQUISITES

Sebelum mulai, pastikan sudah punya:
- ✅ Supabase account (sign up di https://supabase.com)
- ✅ Railway account (sign up di https://railway.app)
- ✅ Vercel account (sign up di https://vercel.com)
- ✅ GitHub account (untuk auto-deploy)

---

## 🗺️ MIGRATION STEPS OVERVIEW

1. ✅ **Setup Supabase Project** (Database)
2. ✅ **Migrate Database Schema** (Import schema)
3. ✅ **Migrate Data** (Export & Import)
4. ✅ **Update Backend Config** (Connect ke Supabase)
5. ✅ **Update Extension** (Post ke Supabase)
6. ✅ **Deploy Backend ke Railway**
7. ✅ **Deploy Frontend ke Vercel**
8. ✅ **Test & Verify**

---

## STEP 1: Setup Supabase Project

### 1.1. Create Supabase Project

1. Login ke https://supabase.com
2. Click **"New Project"**
3. Fill in:
   - **Name**: `affiliate-dashboard`
   - **Database Password**: Generate strong password (save ini!)
   - **Region**: Pilih yang terdekat (Asia Pacific - Singapore recommended)
4. Click **"Create new project"**
5. Tunggu ~2 menit sampai project ready

### 1.2. Get Supabase Credentials

Setelah project ready, buka **Settings** → **API**:

- **Project URL**: `https://xxxxx.supabase.co`
- **anon/public key**: `eyJhbGc...` (Anon key)
- **service_role key**: `eyJhbGc...` (Service role key - JANGAN EXPOSE!)

**Buka juga Settings** → **Database** → **Connection string**:
- Copy **Connection string** (format: `postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres`)

**SAVE SEMUA INI!** Akan dipakai nanti.

---

## STEP 2: Migrate Database Schema

### 2.1. Export Schema dari PostgreSQL Lokal

Jika punya PostgreSQL lokal, export schema:

```bash
# Export schema only (no data)
pg_dump -h localhost -U postgres -d affiliate_dashboard --schema-only > schema.sql
```

### 2.2. Import ke Supabase (SEMPURNA - 1 File Saja!)

**✅ PAKAI FILE INI:** `backend/migrations/supabase_complete_setup.sql`

**File ini sudah include SEMUA:**
- ✅ Schema (semua tables)
- ✅ Indexes
- ✅ Triggers
- ✅ RLS Policies

**Cara pakai:**

1. Buka Supabase Dashboard → **SQL Editor**
2. Click **"New Query"**
3. Buka file `backend/migrations/supabase_complete_setup.sql`
4. Copy paste **SEMUA** isi file (dari awal sampai akhir)
5. Click **"Run"**
6. Tunggu ~30 detik sampai semua selesai
7. **Done!** ✅

**Cek hasil:**
- Buka **Table Editor** → harusnya semua tables sudah ada
- Cek **Authentication** → **Policies** → RLS policies sudah active

### 2.4. Verify Schema

Cek di **Table Editor** apakah semua tables terbuat:
- ✅ studios
- ✅ users
- ✅ employees
- ✅ shopee_accounts
- ✅ orders
- ✅ shopee_data_sync (staging table)
- ✅ dll

---

## STEP 3: Migrate Data (Optional)

Jika punya data existing yang perlu di-migrate:

### 3.1. Export Data dari PostgreSQL Lokal

```bash
# Export data only
pg_dump -h localhost -U postgres -d affiliate_dashboard --data-only > data.sql
```

### 3.2. Import ke Supabase

**Via psql:**

```bash
psql "postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres" -f data.sql
```

**Atau via Supabase SQL Editor:**
1. Open `data.sql`
2. Copy paste ke SQL Editor
3. Run

---

## STEP 4: Update Backend Config

### 4.1. Update `.env` File

Edit `backend/.env`:

```env
# Database - Supabase Connection
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres

# Supabase Config
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc... (anon key)
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc... (service role key)

# Keep existing configs
SECRET_KEY=your-secret-key-here
SHOPEE_PARTNER_ID=...
SHOPEE_PARTNER_KEY=...
ACCESS_CODE=...
```

### 4.2. Test Connection Lokal

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Test connection
python -c "from app.database import engine; engine.connect(); print('✅ Connected to Supabase!')"
```

---

## STEP 5: Update Extension

### 5.1. Update Extension Settings

Buka extension popup, isi:
- **Supabase URL**: `https://xxxxx.supabase.co`
- **Supabase Anon Key**: `eyJhbGc...` (anon key)
- **Enable Supabase**: ✅ Check

Extension akan auto-detect dan pakai Supabase jika di-enable.

### 5.2. Test Extension

1. Open Shopee page
2. Click extension popup
3. Click "Connect Account" atau "Sync Now"
4. Cek di Supabase **Table Editor** → `shopee_data_sync` apakah data masuk

---

## STEP 6: Deploy Backend ke Railway

### 6.1. Prepare Railway

1. Login ke https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Connect GitHub account & select `affiliate-dashboard` repo

### 6.2. Configure Service

Railway akan auto-detect FastAPI. Set environment variables:

**Railway Dashboard** → **Variables** tab, add:

```env
DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
SECRET_KEY=your-secret-key-here
SHOPEE_PARTNER_ID=...
SHOPEE_PARTNER_KEY=...
ACCESS_CODE=...
```

### 6.3. Configure Build Settings

**Settings** → **Deploy**:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Root Directory**: `backend`

### 6.4. Deploy

1. Railway akan auto-deploy dari GitHub
2. Tunggu build complete (~2-3 menit)
3. Get public URL: **Settings** → **Generate Domain**
4. Test: `https://your-app.railway.app/health`

### 6.5. Setup Cron Job (Optional)

Untuk process pending syncs dari staging table:

**Railway** → **Add Service** → **Cron Job**:

```bash
# Run setiap 5 menit
*/5 * * * * curl -X POST https://your-app.railway.app/api/shopee-data/process-pending -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Atau pakai Railway **Cron** service atau external cron (cron-job.org).

---

## STEP 7: Deploy Frontend ke Vercel

### 7.1. Connect GitHub

1. Login ke https://vercel.com
2. Click **"Add New Project"**
3. Import `affiliate-dashboard` repo
4. Select **"frontend"** sebagai root directory

### 7.2. Configure Build Settings

**Framework Preset**: Vite
**Root Directory**: `frontend`
**Build Command**: `npm run build`
**Output Directory**: `dist`

### 7.3. Set Environment Variables

**Settings** → **Environment Variables**:

```env
VITE_API_URL=https://your-app.railway.app/api
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGc...
```

### 7.4. Deploy

1. Click **"Deploy"**
2. Tunggu build complete (~2-3 menit)
3. Get public URL: `https://your-app.vercel.app`

---

## STEP 8: Update Extension dengan Production URLs

### 8.1. Update Extension Settings

Edit extension popup settings:
- **API Endpoint**: `https://your-app.railway.app/api`
- **Supabase URL**: `https://xxxxx.supabase.co`
- **Supabase Anon Key**: `eyJhbGc...`

### 8.2. Update manifest.json

Edit `extension/manifest.json`, tambahkan ke `host_permissions`:

```json
{
  "host_permissions": [
    "https://xxxxx.supabase.co/*",
    "https://your-app.railway.app/*"
  ]
}
```

---

## STEP 9: Test & Verify

### 9.1. Test Extension → Supabase

1. Open Shopee page
2. Extension sync data
3. Cek Supabase **Table Editor** → `shopee_data_sync` → data masuk ✅

### 9.2. Test Backend Processing

1. Call backend endpoint: `POST /api/shopee-data/process-pending`
2. Cek data di `orders`, `campaigns`, etc → data ter-process ✅

### 9.3. Test Frontend

1. Open Vercel URL
2. Login
3. Cek dashboard → data muncul ✅

---

## 🔧 TROUBLESHOOTING

### Extension tidak bisa post ke Supabase

**Problem:** Error `401 Unauthorized` atau `RLS policy violation`

**Solution:**
1. Cek Supabase Anon Key benar
2. Cek RLS policies sudah di-setup
3. Cek access_code valid di table `users`

### Backend tidak bisa connect ke Supabase

**Problem:** Connection timeout atau authentication failed

**Solution:**
1. Cek DATABASE_URL format benar
2. Cek password benar (no spaces)
3. Cek Supabase project masih active
4. Test connection dari psql

### Frontend tidak bisa call backend API

**Problem:** CORS error atau 404

**Solution:**
1. Cek VITE_API_URL benar
2. Cek backend CORS allow Vercel domain
3. Cek backend masih running di Railway

---

## 📝 POST-MIGRATION CHECKLIST

- [ ] ✅ Supabase database schema imported
- [ ] ✅ RLS policies setup
- [ ] ✅ Backend connected ke Supabase
- [ ] ✅ Extension bisa post ke Supabase
- [ ] ✅ Backend bisa process staging data
- [ ] ✅ Backend deployed ke Railway
- [ ] ✅ Frontend deployed ke Vercel
- [ ] ✅ Extension configured dengan production URLs
- [ ] ✅ Test end-to-end flow
- [ ] ✅ Monitor error logs

---

## 🎯 NEXT STEPS

Setelah migration complete:

1. **Monitor**: Cek logs di Railway & Supabase
2. **Optimize**: Setup indexes jika perlu
3. **Backup**: Supabase auto-backup, tapi bisa setup manual backup juga
4. **Scale**: Upgrade plans jika traffic tinggi

---

## 📚 RESOURCES

- [Supabase Docs](https://supabase.com/docs)
- [Railway Docs](https://docs.railway.app)
- [Vercel Docs](https://vercel.com/docs)
- [Migration Plan Detail](./MIGRATION_PLAN_SUPABASE_VERCEL.md)

---

**Status:** Ready untuk Execute! 🚀