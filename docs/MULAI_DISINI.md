# 🚀 Quick Start Guide - Affiliate Dashboard

## Cara Mudah Menjalankan Aplikasi

### Langkah Pertama Kali (First Time Setup)

1. **Double-click** file `START.bat`
2. Pilih **opsi 4** untuk membuat Super Admin
3. Tunggu sampai selesai, akan muncul:
   ```
   Username: admin
   Password: Admin123!
   ```
4. Kembali ke menu, pilih **opsi 1** atau **opsi 2 & 3**

### Menu START.bat

```
[1] Start All Services (Docker) - Jalankan semuanya dengan Docker
[2] Start Backend Only (Local) - Jalankan backend saja
[3] Start Frontend Only (Local) - Jalankan frontend saja
[4] Create Super Admin - Buat user admin pertama kali
[5] Stop All Services - Matikan semua service
[6] View Logs - Lihat log aplikasi
[7] Open API Documentation - Buka dokumentasi API
[8] Exit - Keluar
```

## Cara Penggunaan Sehari-hari

### Dengan Docker (Paling Mudah) ✅
1. Double-click `START.bat`
2. Pilih **1** (Start All Services)
3. Tunggu sampai browser terbuka otomatis
4. Login dengan:
   - Username: `admin`
   - Password: `Admin123!`

### Tanpa Docker (Development)
1. Double-click `START.bat`
2. **Terminal 1**: Pilih **2** (Backend Only)
3. Buka terminal baru, jalankan `START.bat` lagi
4. **Terminal 2**: Pilih **3** (Frontend Only)
5. Buka browser ke http://localhost:5173

## Cara Menghentikan Aplikasi

### Jika pakai Docker:
1. Jalankan `START.bat`
2. Pilih **5** (Stop All Services)

### Jika pakai Local:
- Tekan `Ctrl + C` di terminal backend dan frontend

## Troubleshooting

### Error "Docker not found"
- Install Docker Desktop: https://www.docker.com/products/docker-desktop
- Restart komputer setelah install

### Error "email-validator is not installed"
Jika muncul error ini saat start backend, jalankan:
```bash
cd backend
venv\Scripts\pip.exe install email-validator
```

Atau install ulang semua dependencies:
```bash
cd backend
venv\Scripts\pip.exe install -r requirements.txt
```

### Error "Port already in use"
- Matikan aplikasi yang pakai port 8000 atau 5173
- Atau gunakan opsi 5 untuk stop services dulu

### Lupa Password Admin
1. Jalankan `START.bat`
2. Pilih **4** (Create Super Admin)
3. Script akan membuat ulang admin dengan password default

## URL Penting

- **Dashboard**: http://localhost:5173
- **API Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database** (PostgreSQL): localhost:5432

## Default Credentials

```
Username: admin
Email: admin@affiliatedashboard.com
Password: Admin123!
```

> ⚠️ **PENTING**: Ganti password setelah login pertama kali!

## Next Steps After Login

1. **Ganti Password**:
   - Buka Profile → Change Password
   
2. **Buat User Baru**:
   - Menu Users → Create User
   - Pilih role: leader atau affiliate
   
3. **Setup Studio**:
   - Menu Studios → Create Studio
   
4. **Tambah Karyawan**:
   - Menu Employees → Create Employee

## Struktur Role

```
super_admin → admin → leader → affiliate
```

- **super_admin**: Full akses semua fitur
- **admin**: Manage users, studios, employees
- **leader**: Manage team affiliates
- **affiliate**: Lihat performa sendiri

## Butuh Bantuan?

Lihat file dokumentasi lengkap:
- `INSTALLATION.md` - Panduan instalasi detail
- `API_DOCUMENTATION.md` - Dokumentasi API lengkap
- `SYSTEM_ARCHITECTURE.md` - Arsitektur sistem
