# 🎨 DEPLOY FRONTEND KE VERCEL

> **Step-by-step guide untuk deploy React frontend ke Vercel**

---

## 📋 PREREQUISITES

Sebelum mulai, pastikan sudah punya:
- ✅ Backend sudah deployed ke Railway (sudah punya URL)
- ✅ GitHub repo dengan code frontend
- ✅ Vercel account (sign up di https://vercel.com)

---

## 🚀 STEP 1: Connect GitHub ke Vercel

### 1.1. Login Vercel

1. Buka https://vercel.com
2. Sign up / Login (bisa pakai GitHub account)
3. Klik **"Add New Project"**

### 1.2. Import Repository

1. Pilih **"Import Git Repository"**
2. Authorize Vercel untuk akses GitHub (jika pertama kali)
3. Pilih repository: `affiliate-dashboard`
4. Klik **"Import"**

---

## ⚙️ STEP 2: Configure Project

### 2.1. Configure Build Settings

Vercel akan auto-detect Vite. Verify settings:

**Framework Preset:** `Vite`  
**Root Directory:** `frontend`  
**Build Command:** `npm run build`  
**Output Directory:** `dist`  
**Install Command:** `npm install`

### 2.2. Set Root Directory

1. Klik **"Edit"** di Root Directory
2. Set ke: `frontend`
3. Save

---

## 🔐 STEP 3: Set Environment Variables

### 3.1. Buka Environment Variables

1. Di project configuration page
2. Scroll ke **"Environment Variables"**
3. Click **"Add"** untuk setiap variable

### 3.2. Add Environment Variables

Add variables berikut:

```env
# Backend API URL (Railway)
VITE_API_URL=https://your-app.up.railway.app/api

# Supabase (optional, jika frontend perlu direct access)
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGc...
```

**Cara ambil values:**

**VITE_API_URL:**
- Ambil dari Railway deployment URL
- Format: `https://your-app.up.railway.app/api`
- **Pastikan ada `/api` di akhir!**

**VITE_SUPABASE_URL:**
- Supabase Dashboard → Settings → API
- Copy **Project URL**: `https://xxxxx.supabase.co`

**VITE_SUPABASE_ANON_KEY:**
- Supabase Dashboard → Settings → API
- Copy **anon public** key

### 3.3. Set untuk Production & Preview

Pastikan environment variables di-set untuk:
- ✅ **Production** (wajib)
- ✅ **Preview** (recommended, untuk test PR)
- ✅ **Development** (optional)

---

## 🚀 STEP 4: Deploy

### 4.1. Deploy Now

1. Scroll ke bawah
2. Klik **"Deploy"**
3. Tunggu build complete (~2-3 menit)

### 4.2. Get Public URL

1. Setelah deploy selesai
2. Vercel akan generate URL: `https://your-app.vercel.app`
3. **Copy URL ini!**

---

## ✅ STEP 5: Verify Deployment

### 5.1. Test Website

1. Buka URL Vercel: `https://your-app.vercel.app`
2. Harusnya muncul login page
3. Test login functionality

### 5.2. Check Console for Errors

1. Buka browser DevTools (F12)
2. Tab **Console**
3. Cek apakah ada error API calls
4. Tab **Network**
5. Cek apakah API calls ke Railway berhasil

### 5.3. Test API Connection

1. Login ke frontend
2. Buka dashboard
3. Cek apakah data bisa di-load dari backend
4. Test beberapa fitur

---

## 🔧 STEP 6: Fix Common Issues

### Issue 1: API Calls Failed (CORS Error)

**Error:** `Access to fetch at '...' from origin '...' has been blocked by CORS policy`

**Solution:**
- Update backend CORS settings di Railway
- Tambahkan Vercel domain ke allowed origins
- File: `backend/app/main.py`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://your-app.vercel.app",  # ← Add ini
        "*"  # Atau pakai * untuk development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 2: Environment Variables Not Working

**Error:** API calls masih ke `localhost`

**Solution:**
- Pastikan variable name pakai prefix `VITE_`
- Vite hanya expose variables dengan prefix `VITE_`
- Re-deploy setelah update environment variables

### Issue 3: Build Failed

**Error:** `npm run build` failed

**Solution:**
- Cek build logs di Vercel
- Pastikan semua dependencies ada di `package.json`
- Pastikan `Root Directory` set ke `frontend`

---

## 🔄 STEP 7: Auto-Deploy Setup

### Enable Auto-Deploy

Vercel otomatis deploy ketika:
- Push ke `main` branch (production)
- Create Pull Request (preview deployment)

### Preview Deployments

1. Create Pull Request di GitHub
2. Vercel akan auto-create preview deployment
3. URL preview: `https://your-app-git-branch.vercel.app`
4. Perfect untuk test sebelum merge!

---

## 📊 STEP 8: Custom Domain (Optional)

### Add Custom Domain

1. Vercel Dashboard → **Settings** → **Domains**
2. Add domain: `dashboard.yourdomain.com`
3. Follow DNS setup instructions
4. Vercel akan auto-configure SSL

---

## 💰 COST MONITORING

### Free Tier

- ✅ **Unlimited deployments**
- ✅ **100GB bandwidth/month**
- ✅ **Preview deployments**
- ✅ **Automatic SSL**

### Upgrade

- **Pro:** $20/month (team features)
- Free tier cukup untuk personal projects

---

## ✅ CHECKLIST

- [ ] ✅ Vercel project created
- [ ] ✅ GitHub repo connected
- [ ] ✅ Root directory set ke `frontend`
- [ ] ✅ Build settings configured
- [ ] ✅ Environment variables set (VITE_API_URL)
- [ ] ✅ Deployment successful
- [ ] ✅ Website accessible
- [ ] ✅ API calls working
- [ ] ✅ Login functionality working
- [ ] ✅ No console errors

---

## 🎯 NEXT STEPS

Setelah frontend deployed:

1. ✅ **Update Backend CORS**
   - Add Vercel domain ke allowed origins

2. ✅ **Test End-to-End**
   - Extension → Supabase → Backend → Frontend

3. ✅ **Update Extension Settings**
   - Extension bisa tetap pakai localhost untuk development
   - Atau update ke production URLs

---

## 🔗 LINKS

**Frontend URL:** `https://your-app.vercel.app`  
**Backend URL:** `https://your-app.up.railway.app`  
**API Docs:** `https://your-app.up.railway.app/docs`

---

**Status:** Ready untuk Deploy! 🚀