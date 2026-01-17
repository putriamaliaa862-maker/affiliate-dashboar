# Struktur Project - Affiliate Dashboard

```
affiliate-dashboard/
│
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # Main FastAPI application
│   │   ├── config.py                 # Configuration & settings
│   │   ├── database.py               # Database setup & session
│   │   │
│   │   ├── models/                   # SQLAlchemy ORM Models
│   │   │   ├── __init__.py
│   │   │   ├── studio.py             # Studio model
│   │   │   ├── employee.py           # Employee model
│   │   │   ├── attendance.py         # Attendance record
│   │   │   ├── shopee_account.py     # Shopee account
│   │   │   ├── campaign.py           # Campaign (iklan)
│   │   │   ├── order.py              # Order (omset)
│   │   │   ├── commission_rule.py    # Commission rules
│   │   │   ├── commission.py         # Commission calculation
│   │   │   └── report.py             # Reports
│   │   │
│   │   ├── routes/                   # API Route Handlers
│   │   │   ├── __init__.py
│   │   │   ├── studio.py             # Studio CRUD endpoints
│   │   │   ├── employee.py           # Employee CRUD endpoints
│   │   │   ├── attendance.py         # Attendance endpoints
│   │   │   ├── shopee_account.py     # Shopee account endpoints
│   │   │   ├── commission.py         # Commission endpoints
│   │   │   └── report.py             # Report endpoints
│   │   │
│   │   ├── services/                 # Business Logic
│   │   │   ├── __init__.py
│   │   │   └── shopee.py             # Shopee API integration
│   │   │
│   │   └── schemas/                  # Pydantic schemas (validation)
│   │       ├── __init__.py
│   │       └── studio.py
│   │
│   ├── migrations/                   # Alembic database migrations
│   ├── requirements.txt               # Python dependencies
│   ├── .env.example                  # Environment variables template
│   └── Dockerfile                    # Docker image for backend
│
├── frontend/                         # React + TypeScript Frontend
│   ├── src/
│   │   ├── pages/                    # Page components
│   │   │   ├── Dashboard.tsx         # Main dashboard
│   │   │   ├── Employees.tsx         # Employee management
│   │   │   ├── Attendance.tsx        # Attendance tracking
│   │   │   ├── Accounts.tsx          # Shopee accounts
│   │   │   ├── Reports.tsx           # Reports page
│   │   │   └── Commissions.tsx       # Commission management
│   │   │
│   │   ├── components/               # Reusable components
│   │   │   ├── Sidebar.tsx           # Navigation sidebar
│   │   │   └── Header.tsx            # Top header
│   │   │
│   │   ├── api/                      # API client functions
│   │   │   ├── client.ts             # Axios client setup
│   │   │   ├── employees.ts          # Employee API calls
│   │   │   └── attendance.ts         # Attendance API calls
│   │   │
│   │   ├── types/                    # TypeScript interfaces
│   │   │   └── index.ts              # Type definitions
│   │   │
│   │   ├── hooks/                    # Custom React hooks
│   │   ├── App.tsx                   # Root component
│   │   ├── main.tsx                  # Entry point
│   │   └── index.css                 # Global styles (Tailwind)
│   │
│   ├── index.html                    # HTML template
│   ├── package.json                  # npm dependencies
│   ├── tsconfig.json                 # TypeScript config
│   ├── tsconfig.node.json
│   ├── vite.config.ts                # Vite config
│   ├── postcss.config.cjs            # PostCSS config
│   ├── Dockerfile                    # Docker image for frontend
│   └── .gitignore
│
├── docker-compose.yml                # Docker Compose orchestration
├── .gitignore                        # Git ignore
├── README.md                         # Project documentation
└── QUICKSTART.md                     # Quick start guide
```

## Entity Relationships

```
Studio (1 studio = 1 bisnis affiliate)
├── Employees (N employees)
│   ├── Attendance (N attendance records)
│   └── Commission (N commission records)
├── ShopeeAccount (N shopee accounts)
│   ├── Campaign (N campaigns/iklan)
│   └── Order (N orders/omset)
└── CommissionRule (N rules per role)

Report (N reports per period)
```

## Technology Stack

**Backend:**
- FastAPI 0.104.1
- SQLAlchemy 2.0.23
- PostgreSQL 16
- Python 3.11

**Frontend:**
- React 18.2.0
- TypeScript 5.2.2
- TailwindCSS 3.3.6
- Vite 5.0.8
- Axios 1.6.5

**DevOps:**
- Docker
- Docker Compose

## Key Features Implemented

✅ **Completed:**
- Database models & schema untuk semua entities
- API endpoints CRUD untuk studio, employee, attendance
- Shopee API integration service (OAuth, token refresh, sync orders)
- Frontend dashboard UI dengan navigasi
- Docker setup dengan docker-compose

⏳ **In Progress:**
- Integrasi API endpoints dengan frontend
- Commission calculation engine
- Advanced reporting & analytics
- CSV import/export

## API Routes Summary

| Resource | GET | POST | PUT | DELETE |
|----------|-----|------|-----|--------|
| Studios | ✅ | ✅ | ✅ | ✅ |
| Employees | ✅ | ✅ | ✅ | ✅ |
| Attendance | ✅ | ✅ | ✅ | - |
| Shopee Accounts | ✅ | ✅ | ✅ | ✅ |
| Commissions | ✅ | ✅ | - | - |
| Reports | ✅ | ✅ | - | - |

## Database Models

1. **Studio** - Informasi studio/cabang
2. **Employee** - Data karyawan (host, leader, supervisor, director)
3. **Attendance** - Catatan absensi harian
4. **ShopeeAccount** - Akun Shopee yang terdaftar
5. **Campaign** - Kampanye iklan/ads
6. **Order** - Pesanan/omset
7. **CommissionRule** - Aturan komisi per role
8. **Commission** - Perhitungan komisi per karyawan per periode
9. **Report** - Laporan ringkas per periode
