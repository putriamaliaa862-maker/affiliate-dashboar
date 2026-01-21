# 📋 URUTAN DEPLOYMENT

> **Step-by-step urutan untuk deploy semua components**

---

## 🎯 REKOMENDASI URUTAN

### **URUTAN TERBAIK: Backend Dulu, Lalu Frontend**

**Kenapa?**
- ✅ Frontend butuh backend URL untuk environment variables
- ✅ Lebih mudah test kalau backend sudah jalan dulu
- ✅ Bisa verify API endpoints sebelum deploy frontend

---

## 📦 URUTAN DEPLOYMENT

### **STEP 1: Database Setup** ✅ (Sudah Selesai!)

- [x] ✅ Setup Supabase project
- [x] ✅ Import schema (`supabase_complete_setup.sql`)
- [x] ✅ Setup RLS policies
- [x] ✅ Get credentials (URL, keys, connection string)

**File:** `backend/migrations/supabase_complete_setup.sql`  
**Status:** ✅ Done

---

### **STEP 2: Deploy Backend ke Railway** ⏳ (NEXT!)

**Kenapa backend dulu?**
- Frontend butuh backend API URL
- Bisa test API endpoints dulu
- Verify database connection

**Guide:** `DEPLOY_BACKEND_RAILWAY.md`

**Actions:**
1. Connect GitHub ke Railway
2. Set root directory: `backend`
3. Configure build & start commands
4. Set environment variables (DATABASE_URL, Supabase keys, dll)
5. Deploy
6. Get Railway URL: `https://your-app.up.railway.app`
7. Test: `/health` endpoint

**Waktu:** ~15-20 menit

---

### **STEP 3: Deploy Frontend ke Vercel** ⏳ (Setelah Backend)

**Setelah backend deployed, baru deploy frontend**

**Guide:** `DEPLOY_FRONTEND_VERCEL.md`

**Actions:**
1. Connect GitHub ke Vercel
2. Set root directory: `frontend`
3. Set environment variables:
   - `VITE_API_URL=https://your-app.up.railway.app/api`
   - `VITE_SUPABASE_URL=...` (optional)
4. Deploy
5. Get Vercel URL: `https://your-app.vercel.app`
6. Test website & API calls

**Waktu:** ~10-15 menit

---

### **STEP 4: Update Extension** ⏳ (Optional)

**Extension bisa tetap pakai:**
- Localhost untuk development
- Atau update ke production URLs

**Jika mau update ke production:**
1. Update `apiEndpoint` ke Railway URL
2. Update Supabase settings
3. Test extension post ke Supabase

---

## 🚀 QUICK START

### Jika Mau Deploy Sekarang:

1. **Backend dulu:**
   ```bash
   # Ikuti guide:
   DEPLOY_BACKEND_RAILWAY.md
   ```

2. **Frontend setelahnya:**
   ```bash
   # Ikuti guide:
   DEPLOY_FRONTEND_VERCEL.md
   ```

---

## ⚠️ IMPORTANT NOTES

### Backend Environment Variables

Pastikan set semua di Railway:
```env
DATABASE_URL=postgresql://postgres.[ref]:[pass]@...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
SECRET_KEY=...
```

### Frontend Environment Variables

Pastikan set di Vercel:
```env
VITE_API_URL=https://your-app.up.railway.app/api
```

### CORS Configuration

Backend sudah set CORS ke `"*"` (allow all), jadi tidak perlu update untuk development. Untuk production, bisa restrict ke domain spesifik.

---

## ✅ FINAL CHECKLIST

Setelah semua deployed:

- [ ] ✅ Supabase database setup
- [ ] ✅ Backend deployed ke Railway
- [ ] ✅ Backend `/health` endpoint working
- [ ] ✅ Frontend deployed ke Vercel
- [ ] ✅ Frontend bisa load & call API
- [ ] ✅ Login functionality working
- [ ] ✅ Extension configured (optional)

---

## 🎯 NEXT: Deploy Backend!

**Mulai dari:** `DEPLOY_BACKEND_RAILWAY.md`

Good luck! 🚀