# 🏠 RUN LOKAL SEDERHANA

> **Backend & Frontend run lokal (untuk development)**

---

## 🚀 QUICK START

### Step 1: Run Backend

```bash
# Buka terminal 1
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Buat .env file (isi dengan Supabase credentials)
# Copy dari backend/.env.example atau buat manual

# Run backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend jalan di: `http://localhost:8000`

---

### Step 2: Run Frontend

```bash
# Buka terminal 2 (terminal baru)
cd frontend
npm install
npm run dev
```

Frontend jalan di: `http://localhost:5173`

---

## ✅ TEST

1. Buka browser: `http://localhost:5173`
2. Test login
3. Semua API calls akan otomatis proxy ke `http://localhost:8000/api`

---

## 📝 ENVIRONMENT VARIABLES

### Backend (.env):
```env
DATABASE_URL=postgresql://postgres.[ref]:[pass]@...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
SECRET_KEY=...
```

### Frontend (.env.local) - Optional:
```env
VITE_API_URL=http://localhost:8000/api
```

(Default sudah set ke localhost, jadi tidak perlu)

---

## 🔄 AUTO-RELOAD

- **Backend:** Auto-reload saat ada perubahan (karena pakai `--reload`)
- **Frontend:** Auto-reload saat ada perubahan (Vite default)

---

**Sederhana & cepat untuk development!** ✅