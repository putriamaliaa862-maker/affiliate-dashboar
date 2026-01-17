# 🚀 Cara Menjalankan Affiliate Dashboard

Pilih salah satu cara berikut untuk menjalankan aplikasi:

---

## Opsi 1: START.bat (Menu Interaktif) ⭐ REKOMENDASI

**File**: `START.bat`

Klik dua kali file ini untuk membuka menu interaktif dengan opsi:

```
[1] Start All Services (Docker)       - Jalankan dengan Docker
[2] Start Backend Only (Local)        - Backend saja (tanpa Docker)
[3] Start Frontend Only (Local)       - Frontend saja
[4] Create Super Admin                - Buat admin pertama kali
[5] Stop All Services                 - Stop semua service Docker
[6] View Logs                          - Lihat log Docker
[7] Open API Documentation             - Buka Swagger UI
[8] Exit                               - Keluar
```

### Pilihan Terbaik untuk Pemula:

**Opsi #2 - Start Backend Only:**
- Tidak perlu Docker
- Otomatis install dependencies (termasuk email-validator)
- Otomatis buat database jika belum ada
- Otomatis seed super admin
- Tampilkan username/password default

**Opsi #4 - Create Super Admin:**
Gunakan ini untuk setup awal pertama kali.

---

## Opsi 2: start_local.bat (Quick Launch)

**File**: `start_local.bat`

Klik dua kali untuk:
- ✅ Jalankan Backend & Frontend sekaligus dalam 2 window terpisah
- ✅ Otomatis install dependencies (termasuk email-validator)
- ✅ Otomatis create database dan seed admin jika belum ada
- ✅ Otomatis buka browser

**Kelebihan:**
- Paling cepat untuk development
- Tidak perlu Docker
- 2 terminal window (backend & frontend)

**Login Default:**
- Username: `admin`
- Password: `Admin123!`

---

## Opsi 3: start_app.bat (Docker)

**File**: `start_app.bat`

Untuk yang sudah install Docker:
- Jalankan dengan Docker Compose
- Build dan start semua containers
- Buka browser otomatis

**Syarat:**
- Docker Desktop harus running

---

## Default Login Credentials 🔐

Setelah aplikasi jalan, gunakan kredensial ini:

```
Username: admin
Email:    admin@affiliatedashboard.com  
Password: Admin123!
```

> ⚠️ **PENTING**: Ganti password default setelah login pertama kali!

---

## URL Akses

Setelah aplikasi running:

- **Frontend Dashboard**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Troubleshooting

### Backend Error: "Module 'email_validator' not found"

**Solusi:** Gunakan `START.bat` opsi #2 atau #4 yang sudah auto-install email-validator.

Atau manual:
```bash
cd backend
call venv\Scripts\activate
pip install email-validator dnspython
```

### Database Kosong / Tidak Ada Admin

**Solusi:** Run `START.bat` pilih opsi #4 (Create Super Admin)

Atau manual:
```bash
cd backend
call venv\Scripts\activate
python seed_admin.py
```

### Port 8000 atau 5173 Sudah Digunakan

Stop aplikasi yang sedang running di port tersebut, atau ganti port di script.

---

## Rekomendasi untuk Development

### Pertama Kali Setup:

1. Double-click `START.bat`
2. Pilih **[4] Create Super Admin**
3. Tunggu hingga selesai
4. Kembali ke menu, pilih **[2] Start Backend Only**
5. Buka browser manual: http://localhost:8000/docs
6. Test login dengan credentials di atas

### Setelah Setup Awal:

Gunakan `start_local.bat` untuk quick launch backend + frontend sekaligus.

---

## Yang Sudah Auto-Handled ✅

Semua startup scripts sudah otomatis handle:

- ✅ Create virtual environment jika belum ada
- ✅ Install pip dependencies
- ✅ Install email-validator & dnspython
- ✅ Create database SQLite jika belum ada
- ✅ Seed super admin jika database baru
- ✅ Show default login credentials
- ✅ Error handling untuk missing Python/Node

---

## Next Steps

Setelah aplikasi jalan:

1. **Login ke Swagger UI**: http://localhost:8000/docs
2. **Test API Login**: POST `/api/auth/login`
3. **Create Users**: POST `/api/users` 
4. **Explore Endpoints**: Lihat semua available API
5. **Build Frontend**: Integrate dengan React app

Selamat coding! 🎉
