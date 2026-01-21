# 📖 PANDUAN LENGKAP PENGGUNAAN
# Affiliate Dashboard - Sistem Manajemen Bisnis Affiliate Live Shopee

> **Update:** 19 Januari 2026  
> **Versi:** 2.0 (dengan Realtime Bot)

---

## 📋 Daftar Isi

1. [Pengenalan Sistem](#pengenalan-sistem)
2. [Setup Awal](#setup-awal)
3. [Menjalankan Dashboard Web](#menjalankan-dashboard-web)
4. [Menggunakan Chrome Extension](#menggunakan-chrome-extension)
5. [Realtime Bot 24/7](#realtime-bot-247)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Pengenalan Sistem

Sistem ini terdiri dari 3 komponen utama:

### 1. **Dashboard Web** 📊
- Interface web untuk melihat data omset, iklan, karyawan
- Login multi-user (Owner, Supervisor, Leader, Host)
- Laporan lengkap daily/weekly/monthly
- Manajemen karyawan dan absensi

### 2. **Chrome Extension** 🔌
- Auto-scraping data dari Shopee Seller Center
- Sinkronisasi otomatis ke dashboard
- Bekerja di background saat buka Shopee

### 3. **Realtime Bot (BARU)** 🤖
- Monitor 100 akun Shopee 24/7
- Scraping setiap 60 detik
- Standalone (tidak perlu buka browser manual)
- Tracking orders \& ads realtime

---

## ⚙️ Setup Awal

### Prasyarat
Pastikan sudah terinstall:
- ✅ **Node.js** (v18+) - [Download](https://nodejs.org)
- ✅ **Python** (v3.11+) - [Download](https://python.org)
- ✅ **PostgreSQL** (v14+) - [Download](https://postgresql.org)

### Langkah Setup

#### 1️⃣ **Setup Database**
```bash
# Buat database PostgreSQL
psql -U postgres
CREATE DATABASE affiliate_dashboard;
\q
```

#### 2️⃣ **Setup Backend**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Edit file `backend\.env`:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/affiliate_dashboard
SECRET_KEY=your-secret-key-here
SHOPEE_API_KEY=your-shopee-api-key
```

Jalankan migrasi database:
```bash
# Kembali ke root folder
cd ..
RUN_MIGRATION.bat
```

#### 3️⃣ **Setup Frontend**
```bash
cd frontend
npm install
```

---

## 🚀 Menjalankan Dashboard Web

### Opsi 1: Jalankan Semua Sekaligus (RECOMMENDED)

**Double-click file:** `START_ALL.bat`

Atau via command line:
```bash
START_ALL.bat
```

✅ **Otomatis menjalankan:**
- Backend (port 8000)
- Frontend (port 5173)
- Database check

Tunggu ~30 detik sampai loading selesai.

### Opsi 2: Jalankan Manual Satu-Satu

**Backend saja:**
```bash
START_BACKEND.bat
```

**Frontend saja:**
```bash
START_FRONTEND.bat
```

### Akses Dashboard

Buka browser:
```
http://localhost:5173
```

**Login Default (Owner):**
- Email: `owner@example.com`
- Password: `password123`

---

## 🔌 Menggunakan Chrome Extension

### Instalasi Extension

1. **Buka Chrome** → Ketik di address bar:
   ```
   chrome://extensions/
   ```

2. **Enable "Developer mode"** (toggle kanan atas)

3. **Klik "Load unpacked"**

4. **Pilih folder:**
   ```
   C:\workspace\affiliate-dashboard\extension
   ```

5. **Extension terinstall!** ✅

### Cara Pakai

#### Step 1: Setup Access Code
1. Login ke Dashboard Web
2. Klik **Profile** → **Settings**
3. Copy **Access Code** Anda (contoh: `ABC123XYZ`)

#### Step 2: Konfigurasi Extension
1. Klik **icon extension** di Chrome toolbar
2. Klik **Options** atau **Settings**
3. Paste **Access Code**
4. Pilih **Shopee Account** yang mau disync
5. **Save Settings**

#### Step 3: Auto-Sync
1. Buka **Shopee Seller Center**: https://banhang.shopee.co.id
2. Login dengan akun Shopee Anda
3. Buka halaman:
   - **Orders** → Data order otomatis tersync
   - **Ads Center** → Data iklan otomatis tersync
   - **Live Products** → Data produk live otomatis tersync

4. **Extension bekerja otomatis!** 🎉

### Cara Cek Extension Berhasil

Di **Console Chrome** (F12 → Console), Anda akan melihat:
```
✅ SHOPEE EXTENSION: Data synced successfully
✅ Sent 45 orders to backend
✅ Sent 12 ad campaigns to backend
```

---

## 🤖 Realtime Bot 24/7

**Realtime Bot** adalah sistem monitoring otomatis yang scraping 100 akun Shopee setiap 60 detik tanpa perlu buka browser manual.

### Setup Bot (Pertama Kali)

**1. Jalankan Setup:**
```bash
SETUP_REALTIME_BOT.bat
```

Ini akan:
- ✅ Install dependencies (playwright, axios, dll)
- ✅ Install Chromium browser
- ✅ Buat folder logs, screenshots, profiles

**2. Edit Config Akun Shopee**

Buka file:
```
bots\shopee_realtime_bot\config\accounts.json
```

Format:
```json
[
  {
    "id": "ACC001",
    "name": "Akun Host 1",
    "username": "user1@example.com",
    "password": "password123",
    "cookies": null
  },
  {
    "id": "ACC002",
    "name": "Akun Host 2",
    "username": "user2@example.com",
    "password": "password456",
    "cookies": null
  }
]
```

💡 **Tips:**
- Isi sampai **100 akun** jika perlu
- Field `cookies` biarkan `null` (akan auto-generate setelah login pertama kali)

**3. Get Access Code**

Login ke Dashboard → Profile → **Copy Access Code**

Contoh: `ABC123XYZ`

### Menjalankan Bot

**Jalankan bot 24/7:**
```bash
RUN_REALTIME_BOT_24H.bat ABC123XYZ
```

Ganti `ABC123XYZ` dengan **Access Code** Anda.

### Bot Berjalan! 🎉

Bot akan:
- ✅ Login ke 100 akun Shopee secara parallel
- ✅ Scraping data **orders** \& **ads** setiap 60 detik
- ✅ Kirim data ke backend via API
- ✅ Screenshot otomatis jika ada error
- ✅ Log lengkap di folder `bots\shopee_realtime_bot\logs`

### Monitoring Bot

**Cek status bot:**
```bash
CHECK_BOT_STATUS.bat
```

Output contoh:
```
✅ Bot Status: RUNNING
📊 Accounts: 100 total
   - 95 online
   - 3 need re-login
   - 2 error
⏱️  Last cycle: 58 seconds
📈 Total scraped today: 8,450 data points
```

### Melihat Data Realtime

1. Buka Dashboard Web
2. Menu: **Realtime Monitor**
3. Pilih filter:
   - **Akun**
   - **Tanggal**
   - **Tipe Data** (Orders / Ads)

Anda akan lihat:
- 📊 **Orders Ready to Ship** (realtime)
- 💰 **Ad Spend Today** (update tiap menit)
- 🪙 **Remaining Coins**
- ⚠️ **Alerts** (budget habis, error, dll)

### Stop Bot

```bash
STOP_REALTIME_BOT.bat
```

Bot akan shutdown gracefully (selesaikan cycle terakhir dulu).

---

## 🛠️ Troubleshooting

### Dashboard Web

#### ❌ Error: "Cannot connect to backend"
**Solusi:**
```bash
# Cek backend jalan?
CHECK_HEALTH.bat

# Restart backend
FORCE_RESTART_BACKEND.bat
```

#### ❌ Error: "Port 8000 already in use"
**Solusi:**
```bash
# Kill semua port yang bentrok
KILL_PORTS.bat
```

#### ❌ Database migration error
**Solusi:**
```bash
# Reset database + re-run migration
RESET_ALL.bat
```

⚠️ **WARNING:** Ini akan **hapus semua data**!

---

### Chrome Extension

#### ❌ Extension tidak muncul
**Solusi:**
1. Pastikan sudah **Load unpacked** di `chrome://extensions/`
2. Pastikan **Developer mode** ON
3. Klik **Reload** extension

#### ❌ "Access Code invalid"
**Solusi:**
1. Login Dashboard → Profile → **Generate New Access Code**
2. Copy code baru
3. Update di Extension Settings

#### ❌ Data tidak sync
**Solusi:**
```bash
# Test extension
TEST_EXTENSION.bat
```

Atau **Force reload extension:**
1. Buka `chrome://extensions/`
2. Klik **Reload** (ikon refresh)
3. Refresh halaman Shopee

---

### Realtime Bot

#### ❌ Bot crash / error
**Solusi:**
```bash
# Cek log error
cd bots\shopee_realtime_bot\logs
notepad supervisor_YYYYMMDD.log
```

**Restart bot:**
```bash
STOP_REALTIME_BOT.bat
RUN_REALTIME_BOT_24H.bat YOUR_ACCESS_CODE
```

#### ❌ "Account needs re-login"
**Solusi:**
1. Buka **screenshot** di `bots\shopee_realtime_bot\screenshots`
2. Lihat error (biasanya captcha / 2FA)
3. **Manual login:**
   - Buka Shopee Seller di browser biasa
   - Login manual
   - Export cookies (gunakan extension "EditThisCookie")
   - Paste cookies ke `config\accounts.json`

#### ❌ Bot lambat (> 60 detik per cycle)
**Solusi:**
- Reduce jumlah akun (coba 50 dulu)
- Edit `config\config.json`:
  ```json
  {
    "concurrent_workers": 10,  // naikkan jadi 15-20
    "timeout": 30000           // turunkan jadi 20000
  }
  ```

#### ❌ Data tidak masuk ke dashboard
**Solusi:**
```bash
# Cek health backend + bot
CHECK_HEALTH.bat
```

Pastikan:
- ✅ Backend running (port 8000)
- ✅ Access Code benar
- ✅ Bot running (cek `CHECK_BOT_STATUS.bat`)

---

## 📊 Workflow Harian Ideal

### Pagi (09:00)
```bash
# Start semua sistem
START_ALL.bat
RUN_REALTIME_BOT_24H.bat YOUR_ACCESS_CODE
```

### Siang (12:00, 15:00, 18:00)
```bash
# Quick check status
CHECK_BOT_STATUS.bat
```

Buka Dashboard → **Realtime Monitor** → cek performa.

### Malam (21:00)
- Export laporan harian (Dashboard → Reports → Export CSV)
- Review alerts / anomali

### Sebelum Tidur
- Bot tetap jalan 24/7 ✅
- Dashboard bisa di-close
- Besok pagi tinggal buka lagi

---

## 🔑 Command Cheat Sheet

| Command | Fungsi |
|---------|--------|
| `START_ALL.bat` | Jalankan Backend + Frontend |
| `START_BACKEND.bat` | Jalankan Backend saja |
| `START_FRONTEND.bat` | Jalankan Frontend saja |
| `SETUP_REALTIME_BOT.bat` | Setup bot pertama kali |
| `RUN_REALTIME_BOT_24H.bat CODE` | Jalankan bot 24/7 |
| `STOP_REALTIME_BOT.bat` | Stop bot |
| `CHECK_BOT_STATUS.bat` | Cek status bot |
| `CHECK_HEALTH.bat` | Cek health semua sistem |
| `KILL_PORTS.bat` | Kill port bentrok |
| `RESET_ALL.bat` | Reset database (HATI-HATI!) |
| `RUN_MIGRATION.bat` | Jalankan migrasi DB |
| `FORCE_RESTART_BACKEND.bat` | Paksa restart backend |
| `TEST_EXTENSION.bat` | Test Chrome extension |

---

## 📞 Bantuan \& Support

**Jika masih ada error:**

1. **Cek logs:**
   - Backend: `backend\logs\`
   - Bot: `bots\shopee_realtime_bot\logs\`
   - Frontend: Console browser (F12)

2. **Health check:**
   ```bash
   CHECK_HEALTH.bat
   ```

3. **Screenshot otomatis:**
   - Bot auto-screenshot error di: `bots\shopee_realtime_bot\screenshots\`

4. **Restart complete:**
   ```bash
   KILL_PORTS.bat
   START_ALL.bat
   RUN_REALTIME_BOT_24H.bat YOUR_ACCESS_CODE
   ```

---

## 🎬 Quick Start (TL;DR)

**Pertama kali:**
```bash
# 1. Setup
RUN_MIGRATION.bat
SETUP_REALTIME_BOT.bat

# 2. Edit akun (bots\shopee_realtime_bot\config\accounts.json)

# 3. Jalankan
START_ALL.bat
RUN_REALTIME_BOT_24H.bat YOUR_ACCESS_CODE
```

**Setiap hari:**
```bash
START_ALL.bat
RUN_REALTIME_BOT_24H.bat YOUR_ACCESS_CODE
```

**Buka dashboard:**
```
http://localhost:5173
```

---

**Selamat menggunakan! 🚀**

*Last Updated: 19 Jan 2026*
