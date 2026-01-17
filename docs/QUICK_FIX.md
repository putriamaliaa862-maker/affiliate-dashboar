# 🔧 QUICK FIX - Error "email-validator not installed"

## Solusi Cepat

Buka terminal/command prompt dan jalankan:

```bash
cd backend
venv\Scripts\pip.exe install email-validator
```

Atau install semua dependencies lagi:

```bash
cd backend
venv\Scripts\pip.exe install -r requirements.txt
```

Setelah selesai:
1. **Tutup** terminal backend yang error
2. Jalankan `START.bat` lagi
3. Pilih **opsi 2** (Start Backend Only)
4. Backend sekarang akan jalan normal

---

## Sudah Fix? Lanjut ke Frontend

1. Buka terminal **BARU**
2. Jalankan `START.bat`
3. Pilih **opsi 3** (Start Frontend Only)
4. Browser akan buka otomatis ke http://localhost:5173
5. Login dengan:
   - Username: `admin`
   - Password: `Admin123!`

---

## Catatan

Dependency `email-validator` sudah saya tambahkan ke `requirements.txt`, jadi untuk instalasi berikutnya tidak akan error lagi.
