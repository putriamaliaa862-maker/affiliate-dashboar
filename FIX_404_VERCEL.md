# 🔧 FIX: 404 Error di Vercel

## ⚠️ Masalah
Frontend di Vercel dapat error **404: NOT_FOUND** karena:
1. `VITE_API_URL` belum diset di Vercel (masih pakai `localhost`)
2. Belum ada `vercel.json` untuk SPA routing
3. Ngrok belum running (jika backend lokal)

---

## ✅ SOLUSI LENGKAP

### STEP 1: Commit `vercel.json` ✅

File `frontend/vercel.json` sudah dibuat. Commit dan push:

```bash
cd frontend
git add vercel.json
git commit -m "Add vercel.json for SPA routing"
git push
```

---

### STEP 2: Pastikan Backend Running

Backend harus running di `localhost:8000`:

```bash
cd backend
venv\Scripts\activate
py -3.12 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Test:** Buka `http://localhost:8000/health` - harus return JSON.

---

### STEP 3: Expose Backend dengan Ngrok

**A. Download Ngrok** (jika belum):
- Download: https://ngrok.com/download
- Extract `ngrok.exe`

**B. Sign Up Ngrok** (gratis):
- Buka: https://dashboard.ngrok.com/signup
- Login dan copy **Auth Token**

**C. Setup Ngrok:**
```bash
# Set auth token (hanya sekali)
ngrok config add-authtoken YOUR_AUTH_TOKEN

# Expose port 8000
ngrok http 8000
```

**D. Copy Forwarding URL:**
```
Forwarding: https://xxxx-xxxx-xxxx.ngrok-free.app -> http://localhost:8000
```

**Copy URL ini:** `https://xxxx-xxxx-xxxx.ngrok-free.app`

**⚠️ PENTING:** Biarkan terminal Ngrok **tetap running**!

---

### STEP 4: Set Environment Variable di Vercel

1. **Buka Vercel Dashboard:**
   - https://vercel.com/dashboard
   - Pilih project **affiliate-dashboard**

2. **Buka Settings:**
   - Klik **Settings** → **Environment Variables**

3. **Add Variable:**
   - **Name:** `VITE_API_URL`
   - **Value:** `https://xxxx-xxxx-xxxx.ngrok-free.app/api` (ganti dengan Ngrok URL kamu)
   - **⚠️ PASTIKAN ada `/api` di akhir!**
   - **Environments:** ✅ Production, ✅ Preview, ✅ Development

4. **Save**

---

### STEP 5: Redeploy Frontend

**Opsi A: Trigger via Git Push**
```bash
git add frontend/vercel.json
git commit -m "Add vercel.json for SPA routing"
git push
```

**Opsi B: Manual Redeploy di Vercel:**
1. Buka **Deployments** tab
2. Click **3 dots** (⋯) pada deployment terbaru
3. Click **Redeploy**

---

### STEP 6: Test

1. Tunggu deployment selesai (1-2 menit)
2. Buka Vercel URL: `https://dashboar.vercel.app` (atau URL kamu)
3. Coba login:
   - Username: `admin`
   - Password: `Admin123!`

**Harusnya berhasil! ✅**

---

## 🔍 TROUBLESHOOTING

### Masih 404?

**A. Cek Environment Variable:**
- Buka Vercel → Settings → Environment Variables
- Pastikan `VITE_API_URL` sudah diset
- Format: `https://xxxx-xxxx-xxxx.ngrok-free.app/api` (ada `/api`!)

**B. Cek Ngrok masih running?**
- Pastikan terminal Ngrok masih open
- URL harus `https://xxxx-xxxx-xxxx.ngrok-free.app`
- Test: Buka Ngrok URL di browser → harus return backend response

**C. Cek Backend masih running?**
- Buka `http://localhost:8000/health` di browser
- Harus return JSON

**D. Cek Browser Console:**
- Buka Developer Tools (F12)
- Tab **Console** → lihat error message
- Tab **Network** → cek request ke `/api/auth/login`
- Lihat apakah URL benar atau masih `localhost`

**E. Cek Vercel Build Log:**
- Buka Vercel → Deployments → Latest deployment
- Lihat **Build Logs**
- Pastikan build berhasil tanpa error

---

## 📝 CATATAN PENTING

1. **Ngrok Free:** URL berubah setiap restart, jadi harus update di Vercel setiap kali
2. **Ngrok Paid:** Bisa pakai static domain (recommended untuk production)
3. **Backend harus running** terus kalau pakai setup ini
4. **Untuk Production:** Deploy backend ke Railway/Render, bukan pakai Ngrok

---

## 🚀 NEXT STEP (Optional)

Kalau mau lebih stabil, deploy backend ke **Railway**:
- Lihat: `DEPLOY_BACKEND_RAILWAY.md`
- Atau: `docs/MIGRATION_GUIDE.md`
