# 🔄 PERBANDINGAN ARSITEKTUR: Sebelum vs Sesudah

## 📊 OVERVIEW

| Aspek | **SEBELUM (Current)** | **SESUDAH (Target)** |
|-------|----------------------|---------------------|
| **Database** | PostgreSQL lokal/Docker | Supabase (PostgreSQL cloud) |
| **Extension API** | FastAPI Backend | Supabase REST API langsung |
| **Frontend** | Localhost:5173 | Vercel (CDN global) |
| **Backend** | Localhost:8000 | Deploy ke Railway/Render |
| **Auth Extension** | X-Access-Code header | Supabase RLS + Access Code |
| **Backup** | Manual pg_dump | Auto backup Supabase |
| **Scalability** | Terbatas | Cloud-native |

---

## 🔌 EXTENSION FLOW

### SEBELUM
```
Chrome Extension
    ↓
POST http://localhost:8000/api/shopee-data/sync
    ↓
FastAPI Route Handler
    ↓
SQLAlchemy Session
    ↓
PostgreSQL Database
```

**Kode:**
```javascript
// extension/background/service-worker.js
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

### SESUDAH
```
Chrome Extension
    ↓
POST https://xxx.supabase.co/rest/v1/shopee_data_sync
    ↓
Supabase REST API
    ↓
Row Level Security Check
    ↓
Supabase PostgreSQL
```

**Kode:**
```javascript
// extension/background/service-worker.js
async function syncToSupabase(data) {
    const SUPABASE_URL = 'https://xxx.supabase.co';
    const SUPABASE_KEY = 'xxx_anon_key';
    
    const response = await fetch(`${SUPABASE_URL}/rest/v1/shopee_data_sync`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'apikey': SUPABASE_KEY,
            'Authorization': `Bearer ${SUPABASE_KEY}`,
            'Prefer': 'return=representation'
        },
        body: JSON.stringify({
            type: data.type,
            account_info: data.account,
            payload: data.data,
            access_code: storage.accessCode
        })
    });
    
    if (!response.ok) throw new Error(`Supabase ${response.status}`);
    return await response.json();
}
```

**Keuntungan:**
- ✅ Tidak perlu backend endpoint khusus
- ✅ Lebih cepat (direct ke database)
- ✅ Auto-generated REST API dari Supabase
- ✅ Type-safe dengan Supabase JS Client (optional)

---

## 💾 DATABASE CONNECTION

### SEBELUM
```python
# backend/app/config.py
database_url: str = "postgresql://user:password@localhost:5432/affiliate_dashboard"

# backend/app/database.py
engine = create_engine(SQLALCHEMY_DATABASE_URL)
```

**Lokasi:** Localhost atau Docker container

### SESUDAH
```python
# backend/app/config.py
database_url: str = "postgresql://postgres.xxx:[PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"

# backend/app/database.py
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True  # Important for Supabase connection pooling
)
```

**Lokasi:** Supabase cloud (AWS)

**Keuntungan:**
- ✅ Auto backup harian
- ✅ Point-in-time recovery
- ✅ Dashboard monitoring
- ✅ Connection pooling otomatis
- ✅ Access dari mana saja (tidak perlu VPN)

---

## 🌐 FRONTEND DEPLOYMENT

### SEBELUM
```bash
# Development
npm run dev
# → http://localhost:5173

# Production (manual)
npm run build
# → Static files di folder dist/
# → Deploy manual ke VPS/CDN
```

**Lokasi:** Localhost atau manual deploy

### SESUDAH
```bash
# Development (tetap sama)
npm run dev

# Production (Vercel)
vercel deploy
# → Auto deploy ke Vercel CDN
# → https://your-app.vercel.app
```

**Environment Variables di Vercel:**
```env
VITE_API_URL=https://your-backend.railway.app/api
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=xxx
```

**Keuntungan:**
- ✅ Auto HTTPS
- ✅ Global CDN (cepat di mana saja)
- ✅ Auto deployment dari GitHub
- ✅ Preview deployments untuk PR
- ✅ Analytics built-in

---

## 🔐 AUTHENTICATION & SECURITY

### SEBELUM

**Extension Auth:**
- X-Access-Code header
- Backend validate access_code di database

**Frontend Auth:**
- JWT token
- Stored di localStorage
- Backend validate token

### SESUDAH

**Extension Auth:**
- X-Access-Code header (tetap)
- Supabase RLS policy validate access_code
- Anon key untuk public access (dengan RLS)

**Frontend Auth:**
- Bisa tetap pakai JWT (backend)
- Atau migrate ke Supabase Auth (optional)

**RLS Policy Example:**
```sql
-- Hanya allow insert jika access_code valid
CREATE POLICY "extension_insert_policy" ON shopee_data_sync
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE access_code = shopee_data_sync.access_code
        )
    );
```

**Keuntungan:**
- ✅ Security di database level (RLS)
- ✅ Tidak perlu validate di application layer
- ✅ Audit trail otomatis

---

## 📦 DATA FLOW COMPARISON

### SEBELUM: Extension → Backend → DB

```
┌──────────────┐
│   Extension  │
│  (Browser)   │
└──────┬───────┘
       │ POST /api/shopee-data/sync
       │ Headers: X-Access-Code
       │ Body: { type, account, data }
       ↓
┌────────────────────────┐
│   FastAPI Backend      │
│  ┌──────────────────┐  │
│  │ Verify Access    │  │
│  │ Code             │  │
│  └──────────────────┘  │
│  ┌──────────────────┐  │
│  │ Validate Data    │  │
│  └──────────────────┘  │
│  ┌──────────────────┐  │
│  │ Save to DB       │  │
│  └──────────────────┘  │
└──────┬─────────────────┘
       │ SQL INSERT
       ↓
┌──────────────┐
│  PostgreSQL  │
│   (Local)    │
└──────────────┘
```

**Layers:** 3 (Extension → Backend → DB)  
**Latency:** ~100-200ms (dengan backend processing)

### SESUDAH: Extension → Supabase

```
┌──────────────┐
│   Extension  │
│  (Browser)   │
└──────┬───────┘
       │ POST /rest/v1/shopee_data_sync
       │ Headers: apikey, Authorization
       │ Body: { type, account_info, payload, access_code }
       ↓
┌────────────────────────┐
│   Supabase REST API    │
│  ┌──────────────────┐  │
│  │ RLS Policy Check │  │
│  │ (validate access │  │
│  │  code in users)  │  │
│  └──────────────────┘  │
└──────┬─────────────────┘
       │ SQL INSERT
       ↓
┌──────────────┐
│  Supabase    │
│  PostgreSQL  │
│   (Cloud)    │
└──────────────┘
```

**Layers:** 2 (Extension → DB)  
**Latency:** ~50-100ms (direct ke database)

**Backend Processing (Optional):**
- Backend bisa baca dari staging table
- Process & move ke final tables
- Atau langsung insert ke final tables (dengan RLS)

---

## 🔄 MIGRATION PATH

### Option 1: Gradual Migration (Recommended)

**Step 1:** Setup Supabase, migrate database
- Backend connect ke Supabase
- Extension masih post ke backend
- ✅ Test dulu

**Step 2:** Update extension
- Extension post langsung ke Supabase
- Backend tetap jalan (untuk frontend)
- ✅ Test extension

**Step 3:** Deploy frontend
- Frontend ke Vercel
- Backend ke Railway/Render
- ✅ Full migration

**Risk:** ⚠️ Low (test setiap step)

### Option 2: Big Bang Migration

**Semua sekaligus:**
- Database migrate ke Supabase
- Extension update ke Supabase
- Frontend deploy ke Vercel
- Backend deploy ke Railway

**Risk:** ⚠️⚠️ High (break jika ada masalah)

**Rekomendasi:** ✅ Option 1 (gradual)

---

## 💰 COST COMPARISON

### SEBELUM (Current)
- **Database:** $0 (local/VPS)
- **Backend:** $0 (local/VPS)
- **Frontend:** $0 (local/VPS)
- **Total:** $0 (tapi perlu maintain sendiri)

### SESUDAH (Target)
- **Database (Supabase):** $0 free tier / $25 pro
- **Backend (Railway):** $0 free tier / $5-20
- **Frontend (Vercel):** $0 free tier / $20 pro
- **Total:** $0 (free tier) atau $45-65/bulan (pro)

**Free Tier Capacity:**
- Supabase: 500MB DB, 2GB bandwidth
- Railway: 500 hours/month
- Vercel: 100GB bandwidth/month

**Untuk development/testing:** ✅ Free tier cukup

---

## ✅ DECISION MATRIX

| Requirement | Current | Supabase + Vercel |
|-------------|---------|-------------------|
| **Scalability** | ❌ Manual | ✅ Auto |
| **Backup** | ❌ Manual | ✅ Auto |
| **Monitoring** | ❌ Manual setup | ✅ Built-in |
| **HTTPS** | ❌ Manual | ✅ Auto |
| **Global CDN** | ❌ No | ✅ Yes (Vercel) |
| **Development Speed** | ⚠️ Medium | ✅ Fast |
| **Maintenance** | ❌ High | ✅ Low |
| **Cost** | ✅ Free (VPS) | ✅ Free tier / $45-65 |

---

## 🎯 RECOMMENDATION

**✅ MIGRATE** - Benefit jauh lebih besar:

1. ✅ **Extension lebih simple** (tidak perlu backend endpoint)
2. ✅ **Database centralized** (backup, monitoring, access)
3. ✅ **Frontend global** (Vercel CDN)
4. ✅ **Less maintenance** (managed services)
5. ✅ **Better scalability** (cloud-native)

**Timeline:** 5-8 jam kerja  
**Risk:** Low (gradual migration)  
**Cost:** $0 (free tier) atau $45-65/bulan

---

**Next Step:** Diskusi prioritas & mulai implementation 🚀