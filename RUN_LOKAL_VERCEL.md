# 🏠 RUN LOKAL + DEPLOY VERCEL

> **Backend run lokal, Frontend deploy ke Vercel**

---

## 📋 SKENARIO

- ✅ **Backend:** Run lokal (localhost:8000)
- ✅ **Frontend:** Deploy ke Vercel
- ✅ **Connection:** Frontend call backend via Ngrok (expose localhost ke internet)

---

## 🚀 PART 1: Setup Backend Lokal

### Step 1: Setup Environment

1. Buka terminal di folder `backend`:
   ```bash
   cd backend
   ```

2. Buat virtual environment (jika belum):
   ```bash
   python -m venv venv
   ```

3. Activate virtual environment:
   ```bash
   # Windows PowerShell:
   venv\Scripts\Activate.ps1
   
   # Windows CMD:
   venv\Scripts\activate.bat
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: Setup .env File

Buat file `backend/.env`:

```env
# Database - Supabase
DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres

# Supabase Config
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...

# Security
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Shopee API (optional)
SHOPEE_PARTNER_ID=...
SHOPEE_PARTNER_KEY=...
ACCESS_CODE=...

# Application
APP_NAME=Affiliate Dashboard
DEBUG=True
```

### Step 3: Run Backend

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend akan jalan di: `http://localhost:8000`

**Test:** Buka `http://localhost:8000/health`

---

## 🌐 PART 2: Expose Backend dengan Ngrok

### Step 1: Download & Install Ngrok

1. Download: https://ngrok.com/download
2. Extract `ngrok.exe` ke folder (misalnya: `C:\ngrok\`)
3. Atau install via package manager:
   ```bash
   # Via Chocolatey
   choco install ngrok
   
   # Atau download manual
   ```

### Step 2: Sign Up Ngrok

1. Buka https://dashboard.ngrok.com/signup
2. Sign up (gratis)
3. Get auth token dari dashboard

### Step 3: Setup Ngrok

1. Authenticate:
   ```bash
   ngrok config add-authtoken YOUR_AUTH_TOKEN
   ```

### Step 4: Expose Backend

Di terminal baru (biarkan backend tetap jalan):

```bash
ngrok http 8000
```

Output akan muncul:
```
Forwarding  https://xxxx-xxxx-xxxx.ngrok-free.app -> http://localhost:8000
```

**Copy URL ini!** (contoh: `https://xxxx-xxxx-xxxx.ngrok-free.app`)

### Step 5: Test Ngrok URL

Buka browser: `https://xxxx-xxxx-xxxx.ngrok-free.app/health`

Harusnya response sama seperti localhost ✅

---

## 🎨 PART 3: Deploy Frontend ke Vercel

### Step 1: Connect GitHub

1. Buka https://vercel.com
2. Sign up / Login
3. Click **"Add New Project"**
4. Import repository `affiliate-dashboard`
5. Set **Root Directory:** `frontend`

### Step 2: Set Environment Variables

**VITE_API_URL:**
```
https://xxxx-xxxx-xxxx.ngrok-free.app/api
```

(Gunakan Ngrok URL yang sudah di-copy)

### Step 3: Deploy

1. Click **"Deploy"**
2. Tunggu build selesai
3. Get Vercel URL: `https://your-app.vercel.app`

### Step 4: Test

1. Buka Vercel URL
2. Test login
3. Cek apakah bisa call backend API ✅

---

## 🔄 PART 4: Update CORS di Backend

Backend perlu allow request dari Vercel domain.

### Update `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://your-app.vercel.app",  # ← Add Vercel domain
        "*"  # Atau pakai * untuk development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Restart backend** setelah update!

---

## ⚠️ CATATAN PENTING

### Ngrok Free Tier Limitations:

- ✅ **Gratis** tapi ada limitations
- ⚠️ URL berubah setiap restart Ngrok (kecuali pakai paid plan)
- ⚠️ Rate limiting (40 requests/minute)
- ⚠️ Connection timeout setelah 2 jam idle

### Solusi untuk Production:

**Option 1: Ngrok Paid Plan**
- $8/month untuk fixed URL
- No rate limiting

**Option 2: Deploy Backend ke Render (Free)**
- Render punya free tier (750 jam/bulan)
- Bisa pakai fixed URL
- Lebih stable daripada Ngrok

**Option 3: Deploy Backend ke VPS**
- Pakai VPS murah ($5/bulan)
- Full control

---

## 🚀 WORKFLOW HARIAN

### Setiap Kali Mau Development:

1. **Start Backend:**
   ```bash
   cd backend
   venv\Scripts\activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start Ngrok** (terminal baru):
   ```bash
   ngrok http 8000
   ```

3. **Update Vercel Environment Variable:**
   - Jika Ngrok URL berubah
   - Vercel Dashboard → Settings → Environment Variables
   - Update `VITE_API_URL` dengan Ngrok URL baru
   - Re-deploy frontend

4. **Frontend sudah di Vercel** (tidak perlu run lokal)

---

## 💡 ALTERNATIF: Backend Lokal, Frontend Lokal

Jika Ngrok terlalu ribet, bisa pakai frontend lokal juga:

### Run Frontend Lokal:

```bash
cd frontend
npm install
npm run dev
```

Frontend akan jalan di: `http://localhost:5173`

Tidak perlu Vercel, semua lokal. Tapi tidak bisa akses dari internet.

---

## ✅ CHECKLIST

- [ ] ✅ Backend run lokal (localhost:8000)
- [ ] ✅ Ngrok expose backend
- [ ] ✅ Test Ngrok URL (`/health` endpoint)
- [ ] ✅ Frontend deployed ke Vercel
- [ ] ✅ Vercel environment variable set (VITE_API_URL)
- [ ] ✅ Backend CORS allow Vercel domain
- [ ] ✅ Test login dari Vercel

---

## 🎯 NEXT STEPS

Setelah semua jalan:

1. ✅ Test end-to-end flow
2. ✅ Extension bisa post ke Supabase
3. ✅ Frontend bisa akses data dari backend

---

**Status:** Ready untuk Run! 🚀

**Recommendation:** Untuk development, pakai **Backend Lokal + Frontend Lokal**. Untuk demo/production, pakai **Backend Lokal + Ngrok + Vercel**.