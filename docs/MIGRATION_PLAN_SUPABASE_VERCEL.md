# 📋 RENCANA MIGRASI: Supabase + Vercel

> **Tanggal:** 19 Januari 2025  
> **Status:** Planning Phase  
> **Prioritas:** High

---

## 🎯 Tujuan Migrasi

1. ✅ **Extension → Supabase**: Chrome extension posting langsung ke Supabase (tanpa backend)
2. ✅ **Database Migration**: Migrasi dari PostgreSQL lokal ke Supabase PostgreSQL
3. ✅ **Frontend Deployment**: Deploy React frontend ke Vercel

---

## 📊 ANALISIS FEASIBILITY

### ✅ 1. Extension Post ke Supabase - **SANGAT MUNGKIN**

**Current Flow:**
```
Chrome Extension → FastAPI Backend (/api/shopee-data/sync) → PostgreSQL
```

**Target Flow:**
```
Chrome Extension → Supabase REST API → Supabase PostgreSQL
```

**Kenapa Mungkin:**
- Supabase menyediakan REST API otomatis untuk semua tabel
- Supabase mendukung Row Level Security (RLS) untuk autentikasi
- Extension bisa menggunakan Supabase JS Client atau REST API langsung
- Lebih sederhana, tidak perlu maintain backend endpoint khusus

**Tantangan:**
- Perlu setup RLS policies untuk security
- Perlu migrate auth logic (access_code → Supabase auth)
- Perlu update extension code untuk call Supabase instead of backend

---

### ✅ 2. Database Migration ke Supabase - **SANGAT MUNGKIN**

**Current:**
- PostgreSQL 16 (local atau Docker)
- SQLAlchemy ORM
- Alembic migrations

**Target:**
- Supabase PostgreSQL (PostgreSQL 15 compatible)
- Tetap pakai SQLAlchemy (compatible)
- Import schema via Supabase SQL Editor atau pg_dump

**Kenapa Mungkin:**
- Supabase menggunakan PostgreSQL standar (fully compatible)
- SQLAlchemy 2.0 mendukung Supabase connection string
- Bisa migrate data dengan `pg_dump` → `pg_restore`
- Supabase support semua PostgreSQL features yang digunakan

**Tantangan:**
- Perlu update connection string di backend
- Perlu setup environment variables baru
- Perlu test semua queries setelah migration

---

### ✅ 3. Frontend Deploy ke Vercel - **SANGAT MUNGKIN**

**Current:**
- React + Vite
- Dev server di localhost:5173
- Proxy ke backend API

**Target:**
- Deploy static build ke Vercel
- Environment variables untuk API URL
- CDN & edge functions support

**Kenapa Mungkin:**
- Vite generate static files (perfect untuk Vercel)
- Vercel support React out of the box
- Environment variables mudah di-setup
- Vercel gratis untuk personal projects

**Tantangan:**
- Perlu update API base URL (jika backend masih di tempat lain)
- Perlu setup environment variables di Vercel
- Perlu konfigurasi build settings

---

## 🗺️ RENCANA IMPLEMENTASI

### **PHASE 1: Setup Supabase Project**

#### 1.1. Buat Supabase Project
- [ ] Sign up/login ke Supabase
- [ ] Create new project
- [ ] Catat:
  - Project URL (https://xxx.supabase.co)
  - Anon Key (public key untuk client)
  - Service Role Key (private key untuk backend)
  - Database password

#### 1.2. Setup Database Schema
- [ ] Export schema dari PostgreSQL lokal
- [ ] Import schema ke Supabase (via SQL Editor)
- [ ] Verifikasi semua tables terbuat
- [ ] Setup indexes & foreign keys

#### 1.3. Setup Row Level Security (RLS)
- [ ] Enable RLS di semua tables
- [ ] Buat policies untuk:
  - Extension insert data (anon key dengan specific access_code)
  - Backend full access (service role)
  - Users read access (JWT auth)
- [ ] Test policies

---

### **PHASE 2: Migrate Database**

#### 2.1. Export Data dari PostgreSQL Lokal
```bash
# Export schema
pg_dump -h localhost -U postgres -d affiliate_dashboard --schema-only > schema.sql

# Export data
pg_dump -h localhost -U postgres -d affiliate_dashboard --data-only > data.sql
```

#### 2.2. Import ke Supabase
- [ ] Upload schema.sql via Supabase SQL Editor
- [ ] Upload data.sql (atau gunakan pg_restore via connection string)
- [ ] Verifikasi data integrity

#### 2.3. Update Backend Config
- [ ] Update `backend/app/config.py`:
  ```python
  database_url: str = "postgresql://postgres:[PASSWORD]@[HOST].supabase.co:5432/postgres"
  ```
- [ ] Add Supabase keys ke `.env`:
  ```env
  SUPABASE_URL=https://xxx.supabase.co
  SUPABASE_ANON_KEY=xxx
  SUPABASE_SERVICE_ROLE_KEY=xxx
  ```
- [ ] Test connection

---

### **PHASE 3: Update Extension ke Supabase**

#### 3.1. Install Supabase JS Client
- [ ] Add `@supabase/supabase-js` ke extension (via npm atau CDN)
- [ ] Atau gunakan REST API langsung (tanpa library)

#### 3.2. Update Extension Code
**File: `extension/background/service-worker.js`**

**Current:**
```javascript
async function syncToBackend(data) {
    const endpoint = `${apiEndpoint}/shopee-data/sync`;
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Access-Code': storage.accessCode
        },
        body: JSON.stringify(data)
    });
    return await response.json();
}
```

**New (Option 1: REST API):**
```javascript
async function syncToSupabase(data) {
    const SUPABASE_URL = 'https://xxx.supabase.co';
    const SUPABASE_ANON_KEY = 'xxx';
    
    // Insert to shopee_data_sync table directly
    const response = await fetch(`${SUPABASE_URL}/rest/v1/shopee_data_sync`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
            'Prefer': 'return=representation'
        },
        body: JSON.stringify({
            type: data.type,
            account_info: data.account,
            payload: data.data,
            access_code: storage.accessCode,
            created_at: new Date().toISOString()
        })
    });
    
    if (!response.ok) throw new Error(`Supabase ${response.status}`);
    return await response.json();
}
```

**New (Option 2: Supabase JS Client):**
```javascript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
    'https://xxx.supabase.co',
    'xxx_anon_key'
);

async function syncToSupabase(data) {
    const { data: result, error } = await supabase
        .from('shopee_data_sync')
        .insert({
            type: data.type,
            account_info: data.account,
            payload: data.data,
            access_code: storage.accessCode
        })
        .select();
    
    if (error) throw error;
    return result;
}
```

#### 3.3. Setup RLS Policy untuk Extension
```sql
-- Allow insert with access_code check
CREATE POLICY "extension_insert" ON shopee_data_sync
    FOR INSERT
    WITH CHECK (
        access_code IN (SELECT access_code FROM users WHERE access_code IS NOT NULL)
    );

-- Allow service role full access
CREATE POLICY "service_role_full_access" ON shopee_data_sync
    FOR ALL
    USING (auth.role() = 'service_role');
```

---

### **PHASE 4: Deploy Frontend ke Vercel**

#### 4.1. Prepare Frontend Build
- [ ] Update `frontend/vite.config.ts` untuk production build
- [ ] Update `frontend/.env.production` (jika ada):
  ```env
  VITE_API_URL=https://your-backend-api.com/api
  ```

#### 4.2. Deploy ke Vercel
- [ ] Install Vercel CLI: `npm i -g vercel`
- [ ] Login: `vercel login`
- [ ] Deploy: `cd frontend && vercel`
- [ ] Atau connect GitHub repo ke Vercel dashboard

#### 4.3. Setup Environment Variables di Vercel
- [ ] VITE_API_URL → Backend API URL
- [ ] VITE_SUPABASE_URL → Supabase project URL
- [ ] VITE_SUPABASE_ANON_KEY → Supabase anon key

#### 4.4. Update API Client
- [ ] Update `frontend/src/api/client.ts` untuk use environment variable
- [ ] Test semua API calls

---

## 📝 DETAIL IMPLEMENTASI

### **A. Extension → Supabase Direct Insert**

**Tabel yang Perlu Dibuat di Supabase:**
```sql
-- Tabel untuk menerima data dari extension
CREATE TABLE shopee_data_sync (
    id BIGSERIAL PRIMARY KEY,
    type TEXT NOT NULL, -- 'transactions', 'affiliate_dashboard', 'live_streaming'
    account_info JSONB,
    payload JSONB,
    access_code TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE
);

-- Tabel untuk processed data (existing tables)
-- (orders, campaigns, live_sessions, etc.)
```

**RLS Policies:**
```sql
-- Enable RLS
ALTER TABLE shopee_data_sync ENABLE ROW LEVEL SECURITY;

-- Policy untuk extension (insert only)
CREATE POLICY "extension_insert_policy" ON shopee_data_sync
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE access_code = shopee_data_sync.access_code
        )
    );

-- Policy untuk backend (read & process)
CREATE POLICY "backend_read_policy" ON shopee_data_sync
    FOR SELECT
    USING (auth.role() = 'service_role');

CREATE POLICY "backend_update_policy" ON shopee_data_sync
    FOR UPDATE
    USING (auth.role() = 'service_role');
```

---

### **B. Backend Tetap Pakai Supabase**

**Connection String Format:**
```
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

**Update `backend/app/database.py`:**
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Supabase connection string
SQLALCHEMY_DATABASE_URL = settings.database_url

# Supabase uses connection pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True  # Important for Supabase
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

---

### **C. Vercel Deployment Config**

**File: `frontend/vercel.json` (opsional):**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://your-backend-api.com/api/$1"
    }
  ]
}
```

**Environment Variables di Vercel Dashboard:**
- `VITE_API_URL` → Backend API (atau tetap localhost untuk dev)
- `VITE_SUPABASE_URL` → Supabase project URL
- `VITE_SUPABASE_ANON_KEY` → Supabase anon key

---

## ⚠️ PERHATIAN & CONSIDERATIONS

### 1. **Security**
- ✅ Jangan expose Service Role Key di extension
- ✅ Gunakan Anon Key dengan RLS policies ketat
- ✅ Validasi access_code di Supabase function/trigger
- ✅ Rate limiting untuk extension requests

### 2. **Data Processing**
- **Option A**: Extension insert ke staging table → Backend cron job process
- **Option B**: Extension insert langsung ke final tables (dengan RLS)
- **Rekomendasi**: Option A lebih aman & maintainable

### 3. **Backend Architecture**
- Backend masih diperlukan untuk:
  - Business logic (commission calculation, reports)
  - Complex queries & aggregations
  - Scheduled jobs
  - Admin functions
- Backend bisa di-deploy ke:
  - Railway
  - Render
  - Fly.io
  - VPS

### 4. **Cost Estimation**

**Supabase:**
- Free tier: 500MB database, 2GB bandwidth
- Pro tier ($25/mo): 8GB database, 250GB bandwidth

**Vercel:**
- Free tier: Unlimited deployments, 100GB bandwidth
- Pro tier ($20/mo): More features, team collaboration

---

## ✅ CHECKLIST MIGRATION

### Pre-Migration
- [ ] Backup database lokal (pg_dump)
- [ ] Document current API endpoints
- [ ] Test semua features existing

### Supabase Setup
- [ ] Create Supabase project
- [ ] Import schema
- [ ] Import data
- [ ] Setup RLS policies
- [ ] Test connection dari backend

### Extension Update
- [ ] Update manifest.json (add Supabase URLs)
- [ ] Update service-worker.js
- [ ] Test extension insert ke Supabase
- [ ] Verify RLS policies bekerja

### Backend Update
- [ ] Update database connection string
- [ ] Test semua endpoints
- [ ] Update environment variables

### Frontend Deploy
- [ ] Build frontend production
- [ ] Setup Vercel project
- [ ] Configure environment variables
- [ ] Deploy & test
- [ ] Update CORS di backend (add Vercel domain)

### Post-Migration
- [ ] Test semua flows end-to-end
- [ ] Monitor error logs
- [ ] Performance testing
- [ ] Update documentation

---

## 🚀 NEXT STEPS

1. **Diskusi Prioritas**: Mana yang mau dilakukan dulu?
   - A. Extension → Supabase (simplify architecture)
   - B. Database migration (centralize data)
   - C. Frontend deploy (go live)

2. **Setup Supabase Project**: Saya bisa bantu setup jika sudah ada credentials

3. **Start Implementation**: Mulai dari yang paling urgent

---

## 📚 RESOURCES

- [Supabase Docs](https://supabase.com/docs)
- [Supabase JS Client](https://supabase.com/docs/reference/javascript/introduction)
- [Vercel Deployment](https://vercel.com/docs)
- [PostgreSQL Migration Guide](https://supabase.com/docs/guides/database/migrations)

---

**Status:** ✅ Ready untuk Discussion & Implementation