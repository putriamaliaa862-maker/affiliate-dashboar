# Affiliate Dashboard - Sistem Manajemen Bisnis Affiliate Live Shopee

Aplikasi web komprehensif untuk mengelola bisnis affiliate Shopee Anda dengan fitur:

## ✨ Fitur Utama

- **Manajemen Karyawan**: Data lengkap host, leader, supervisor, director
- **Absensi**: Input manual absensi harian (check in/out)
- **Akun Shopee**: Kelola multiple akun Shopee dengan integrasi API
- **Kampanye Iklan**: Tracking budget, spending, dan performa kampanye
- **Data Omset**: Integrasi order dari Shopee secara real-time
- **Perhitungan Komisi**: Otomatis berdasarkan rules per role dan periode
- **Laporan Performa**: Daily, weekly, monthly reports dengan export CSV
- **Multi-Studio**: Siap untuk ekspansi ke multiple studio

## 🏗️ Tech Stack

- **Backend**: FastAPI (Python 3.11+) + PostgreSQL
- **Frontend**: React 18 + TypeScript + TailwindCSS
- **Auth**: JWT Token based
- **Deployment**: Docker + Docker Compose

## 🚀 Instalasi & Menjalankan

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (untuk development lokal)
- Node.js 18+ (untuk development lokal)

### 1. Setup Environment Variables

```bash
cd backend
cp .env.example .env
# Edit .env dengan kredensial Shopee Anda
```

### 2. Jalankan dengan Docker Compose

```bash
docker-compose up --build
```

Aplikasi akan tersedia di:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- PostgreSQL: localhost:5432

### 3. Development Lokal (Tanpa Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 📊 Struktur Database

```
Studio
├── Employees (host, leader, supervisor, director)
├── ShopeeAccounts
│   ├── Campaigns (iklan)
│   └── Orders (omset)
├── CommissionRules
└── CommissionCalculations

Attendance
Reports (daily, weekly, monthly)
```

## 🔑 API Endpoints (Draft)

```
## Studios
GET    /api/studios
POST   /api/studios
GET    /api/studios/{id}
PUT    /api/studios/{id}

## Employees
GET    /api/employees?studio_id={id}
POST   /api/employees
PUT    /api/employees/{id}
DELETE /api/employees/{id}

## Attendance
GET    /api/attendances?employee_id={id}&from={date}&to={date}
POST   /api/attendances
POST   /api/attendances/bulk

## Shopee Accounts
GET    /api/shopee-accounts
POST   /api/shopee-accounts
POST   /api/shopee-accounts/{id}/sync (Integrasi API Shopee)

## Commissions
GET    /api/commissions?period={YYYY-MM}
POST   /api/commissions/calculate

## Reports
GET    /api/reports?type={daily|weekly|monthly}&period={date}
POST   /api/reports/export
```

## 📝 Catatan Pengembangan

### Phase 1 (MVP - Current)
- [x] Setup project structure
- [x] Database models & schema
- [ ] Implement API endpoints
- [ ] Frontend dashboard UI
- [ ] Basic CRUD operations

### Phase 2
- [ ] Shopee API integration
- [ ] Advanced reporting & analytics
- [ ] Commission auto-calculation
- [ ] CSV import/export
- [ ] Email notifications

### Phase 3
- [ ] Advanced role-based access control
- [ ] Mobile responsive improvements
- [ ] Payment integration
- [ ] Multi-currency support
- [ ] Performance optimization

## 🔐 Security

- JWT based authentication
- Password hashing dengan bcrypt
- CORS enabled untuk frontend
- Environment variables untuk sensitive data

## 📖 Next Steps

1. **Implement API Endpoints** - CRUD operations untuk semua entities
2. **Frontend Integration** - Connect React components dengan API
3. **Shopee API Integration** - Sync orders dan campaign data
4. **Testing** - Unit tests, integration tests
5. **Deployment** - Setup production environment

## 📞 Support & Questions

Untuk pertanyaan atau issues, silakan discuss lebih lanjut untuk:
- Custom business rules
- Integrasi dengan sistem lain
- Deployment strategy
- Performance optimization

---

**Status**: MVP Phase 1 - Foundation Ready ✅
