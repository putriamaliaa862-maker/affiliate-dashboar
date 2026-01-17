# Quick Start Guide - Affiliate Dashboard

## Setup & Run dengan Docker Compose (Recommended)

### 1. Clone/Open Project
```bash
cd affiliate-dashboard
```

### 2. Setup Environment
```bash
cp backend/.env.example backend/.env
# Edit backend/.env dengan Shopee credentials Anda (opsional)
```

### 3. Jalankan Aplikasi
```bash
docker-compose up --build
```

Tunggu hingga semua services berjalan (PostgreSQL, Backend, Frontend).

### 4. Akses Aplikasi

**Frontend Dashboard:**
```
http://localhost:5173
```

**Backend API (Swagger Docs):**
```
http://localhost:8000/docs
```

**API Base:**
```
http://localhost:8000/api
```

---

## Development Lokal (Tanpa Docker)

### Backend Setup
```bash
cd backend

# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database (PostgreSQL harus running)
# Update DATABASE_URL di .env

# Run server
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend

npm install
npm run dev
```

---

## API Endpoints Reference

### Studios
```
GET    /api/studios
POST   /api/studios
GET    /api/studios/{id}
PUT    /api/studios/{id}
DELETE /api/studios/{id}
```

### Employees
```
GET    /api/employees?studio_id={id}
POST   /api/employees
GET    /api/employees/{id}
PUT    /api/employees/{id}
DELETE /api/employees/{id}
```

### Attendance
```
GET    /api/attendances?employee_id={id}&date_from={date}&date_to={date}
POST   /api/attendances
POST   /api/attendances/bulk
PUT    /api/attendances/{id}
```

### Shopee Accounts
```
GET    /api/shopee-accounts?studio_id={id}
POST   /api/shopee-accounts
GET    /api/shopee-accounts/{id}
PUT    /api/shopee-accounts/{id}
DELETE /api/shopee-accounts/{id}
```

### Commissions
```
GET    /api/commissions?employee_id={id}&period={YYYY-MM}&status={status}
POST   /api/commissions/calculate
POST   /api/commissions/{id}/approve
POST   /api/commissions/{id}/pay
GET    /api/commissions/summary/{period}?studio_id={id}
```

### Reports
```
GET    /api/reports?studio_id={id}&report_type={daily|weekly|monthly}
POST   /api/reports/generate
GET    /api/reports/{id}
GET    /api/reports/{id}/export
```

---

## Example API Requests

### 1. Create Studio
```bash
curl -X POST http://localhost:8000/api/studios \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Studio Jakarta 1",
    "location": "Jakarta Pusat",
    "description": "Main affiliate studio"
  }'
```

### 2. Create Employee
```bash
curl -X POST http://localhost:8000/api/employees \
  -H "Content-Type: application/json" \
  -d '{
    "studio_id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "08123456789",
    "role": "host",
    "salary_base": 2000000,
    "hire_date": "2024-01-01T00:00:00"
  }'
```

### 3. Record Attendance
```bash
curl -X POST http://localhost:8000/api/attendances \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 1,
    "date": "2024-01-13T00:00:00",
    "check_in": "2024-01-13T09:00:00",
    "check_out": "2024-01-13T17:00:00",
    "status": "present"
  }'
```

### 4. Bulk Attendance
```bash
curl -X POST http://localhost:8000/api/attendances/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "attendances": [
      {
        "employee_id": 1,
        "date": "2024-01-13T00:00:00",
        "check_in": "2024-01-13T09:00:00",
        "check_out": "2024-01-13T17:00:00",
        "status": "present"
      },
      {
        "employee_id": 2,
        "date": "2024-01-13T00:00:00",
        "status": "absent"
      }
    ]
  }'
```

### 5. Add Shopee Account
```bash
curl -X POST http://localhost:8000/api/shopee-accounts \
  -H "Content-Type: application/json" \
  -d '{
    "studio_id": 1,
    "account_name": "Toko Aku 1",
    "shopee_account_id": "12345",
    "access_token": "token_here",
    "refresh_token": "refresh_token_here"
  }'
```

### 6. Calculate Commissions
```bash
curl -X POST http://localhost:8000/api/commissions/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "studio_id": 1,
    "period": "2024-01"
  }'
```

### 7. Generate Report
```bash
curl -X POST http://localhost:8000/api/reports/generate \
  -H "Content-Type: application/json" \
  -d '{
    "studio_id": 1,
    "report_type": "monthly",
    "period": "2024-01"
  }'
```

---

## Database Schema

Lihat di [README.md](README.md) untuk detail schema dan entity relationships.

---

## Next Steps

1. **Konfigurasi Shopee API** - Dapatkan Partner ID & Key dari Shopee Partner
2. **Testing Lokal** - Test CRUD endpoints dengan Postman atau curl
3. **Frontend Integration** - Connect React components dengan API
4. **Customize Business Rules** - Adjust commission rules sesuai kebutuhan
5. **Deployment** - Deploy ke production (VPS, Heroku, AWS, dll)

---

## Troubleshooting

### Port Sudah Digunakan
```bash
# Ganti port di docker-compose.yml atau vite.config.ts
```

### Database Connection Error
```bash
# Pastikan PostgreSQL running dan credentials di .env benar
psql -U user -d affiliate_dashboard -h localhost
```

### Frontend tidak konek ke API
```bash
# Pastikan backend running di port 8000
# Check vite.config.ts proxy settings
# Check CORS di backend/app/main.py
```

---

## Support
Untuk questions atau issues, buat discussion atau check API docs di:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)
