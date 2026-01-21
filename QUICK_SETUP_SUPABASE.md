# ⚡ QUICK SETUP SUPABASE - 1 FILE SAJA!

## 📋 CARA PAKAI

### Step 1: Buka Supabase SQL Editor

1. Login ke https://supabase.com
2. Pilih project Anda
3. Klik **SQL Editor** di sidebar kiri
4. Klik **"New Query"**

### Step 2: Copy-Paste File

1. Buka file: `backend/migrations/supabase_complete_setup.sql`
2. **Select All** (Ctrl+A / Cmd+A)
3. **Copy** (Ctrl+C / Cmd+C)
4. **Paste** ke Supabase SQL Editor (Ctrl+V / Cmd+V)

### Step 3: Run!

1. Klik tombol **"Run"** (atau tekan F5)
2. Tunggu ~30 detik
3. **Done!** ✅

---

## ✅ CHECKLIST VERIFY

Setelah run, cek:

### 1. Tables Created

Buka **Table Editor**, harusnya ada tables:
- ✅ studios
- ✅ users
- ✅ employees
- ✅ shopee_accounts
- ✅ orders
- ✅ campaigns
- ✅ live_sessions
- ✅ shopee_data_sync (staging table)
- ✅ dll (total ~25 tables)

### 2. RLS Policies Active

Buka **Authentication** → **Policies**, cek:
- ✅ `shopee_data_sync` punya policies
- ✅ `orders` punya policies
- ✅ `shopee_accounts` punya policies
- ✅ `users` punya policies

### 3. Test Connection

Test dari backend (setelah update `.env`):
```bash
python -c "from app.database import engine; engine.connect(); print('✅ Connected!')"
```

---

## 🎯 NEXT STEPS

Setelah setup database:
1. Update `backend/.env` dengan Supabase connection string
2. Test backend connection
3. Update extension settings
4. Test extension post ke Supabase

Lihat `docs/MIGRATION_GUIDE.md` untuk langkah selanjutnya!

---

**File yang dipakai:** `backend/migrations/supabase_complete_setup.sql`  
**Total waktu:** ~2 menit  
**Sulit:** ⭐ (Sangat mudah!)