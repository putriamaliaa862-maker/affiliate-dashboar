# API Documentation - Affiliate Dashboard

Comprehensive API documentation untuk semua endpoints.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## Authentication

Saat ini menggunakan basic authentication. Future versions akan implement JWT.

## Response Format

Semua responses menggunakan JSON format:

```json
{
  "data": {...},
  "message": "Success",
  "status": 200
}
```

---

## Studios API

### List Studios
```
GET /api/studios
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Studio Jakarta 1",
    "location": "Jakarta Pusat",
    "description": "Main affiliate studio",
    "is_active": true,
    "created_at": "2024-01-13T10:00:00"
  }
]
```

### Create Studio
```
POST /api/studios
```

**Request:**
```json
{
  "name": "Studio Jakarta 1",
  "location": "Jakarta Pusat",
  "description": "Main affiliate studio"
}
```

**Response:** `201 Created`

### Get Studio
```
GET /api/studios/{id}
```

**Response:** Studio object

### Update Studio
```
PUT /api/studios/{id}
```

**Request:**
```json
{
  "name": "Studio Jakarta Updated",
  "location": "Jakarta Barat"
}
```

### Delete Studio
```
DELETE /api/studios/{id}
```

---

## Employees API

### List Employees
```
GET /api/employees?studio_id={id}
```

**Query Parameters:**
- `studio_id` (optional): Filter by studio

**Response:**
```json
[
  {
    "id": 1,
    "studio_id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "08123456789",
    "role": "host",
    "salary_base": 2000000,
    "hire_date": "2024-01-01T00:00:00",
    "is_active": true,
    "created_at": "2024-01-13T10:00:00"
  }
]
```

### Create Employee
```
POST /api/employees
```

**Request:**
```json
{
  "studio_id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "08123456789",
  "role": "host",
  "salary_base": 2000000,
  "hire_date": "2024-01-01T00:00:00"
}
```

**Roles:**
- `host`: Content creator/host
- `leader`: Team leader
- `supervisor`: Supervisor
- `director`: Director/CEO

### Get Employee
```
GET /api/employees/{id}
```

### Update Employee
```
PUT /api/employees/{id}
```

### Delete Employee
```
DELETE /api/employees/{id}
```

---

## Attendance API

### List Attendance
```
GET /api/attendances?employee_id={id}&date_from={date}&date_to={date}
```

**Query Parameters:**
- `employee_id` (optional): Filter by employee
- `date_from` (optional): Start date (ISO format)
- `date_to` (optional): End date (ISO format)

**Response:**
```json
[
  {
    "id": 1,
    "employee_id": 1,
    "date": "2024-01-13T00:00:00",
    "check_in": "2024-01-13T09:00:00",
    "check_out": "2024-01-13T17:00:00",
    "status": "present",
    "notes": null,
    "created_at": "2024-01-13T10:00:00"
  }
]
```

### Record Attendance
```
POST /api/attendances
```

**Request:**
```json
{
  "employee_id": 1,
  "date": "2024-01-13T00:00:00",
  "check_in": "2024-01-13T09:00:00",
  "check_out": "2024-01-13T17:00:00",
  "status": "present",
  "notes": "On time"
}
```

**Status Values:**
- `present`: Hadir
- `absent`: Tidak hadir
- `late`: Terlambat
- `sick`: Sakit

### Bulk Record Attendance
```
POST /api/attendances/bulk
```

**Request:**
```json
{
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
}
```

### Update Attendance
```
PUT /api/attendances/{id}
```

---

## Shopee Accounts API

### List Shopee Accounts
```
GET /api/shopee-accounts?studio_id={id}
```

**Response:**
```json
[
  {
    "id": 1,
    "studio_id": 1,
    "account_name": "Toko Aku 1",
    "shopee_account_id": "12345",
    "is_active": true,
    "created_at": "2024-01-13T10:00:00"
  }
]
```

### Create Shopee Account
```
POST /api/shopee-accounts
```

**Request:**
```json
{
  "studio_id": 1,
  "account_name": "Toko Aku 1",
  "shopee_account_id": "12345",
  "access_token": "token_here",
  "refresh_token": "refresh_token_here"
}
```

### Get Account
```
GET /api/shopee-accounts/{id}
```

### Update Account
```
PUT /api/shopee-accounts/{id}
```

### Delete Account
```
DELETE /api/shopee-accounts/{id}
```

---

## Commissions API

### List Commissions
```
GET /api/commissions?employee_id={id}&period={YYYY-MM}&status={status}
```

**Query Parameters:**
- `employee_id` (optional): Filter by employee
- `period` (optional): Filter by period (e.g., "2024-01")
- `status` (optional): calculated, approved, paid

**Response:**
```json
[
  {
    "id": 1,
    "employee_id": 1,
    "period": "2024-01",
    "total_amount": 500000,
    "status": "calculated",
    "paid_date": null,
    "notes": null,
    "created_at": "2024-01-13T10:00:00"
  }
]
```

### Calculate Commissions
```
POST /api/commissions/calculate
```

**Request:**
```json
{
  "studio_id": 1,
  "period": "2024-01"
}
```

**Response:**
```json
{
  "created": 9,
  "period": "2024-01",
  "message": "Commissions calculated for 9 employees"
}
```

### Approve Commission
```
POST /api/commissions/{id}/approve
```

### Mark as Paid
```
POST /api/commissions/{id}/pay
```

**Response:**
```json
{
  "message": "Commission marked as paid",
  "paid_date": "2024-01-13T10:00:00"
}
```

### Get Commission Summary
```
GET /api/commissions/summary/{period}?studio_id={id}
```

**Response:**
```json
{
  "period": "2024-01",
  "total": 5000000,
  "paid": 2500000,
  "pending": 2500000,
  "count": 9
}
```

---

## Reports API

### List Reports
```
GET /api/reports?studio_id={id}&report_type={type}
```

**Query Parameters:**
- `studio_id` (optional): Filter by studio
- `report_type` (optional): daily, weekly, monthly

**Response:**
```json
[
  {
    "id": 1,
    "studio_id": 1,
    "report_type": "monthly",
    "period": "2024-01",
    "total_revenue": 25500000,
    "total_commission": 2500000,
    "total_ad_spent": 8200000,
    "attendance_summary": {
      "present": 180,
      "absent": 10,
      "late": 5,
      "sick": 2
    },
    "created_at": "2024-01-13T10:00:00"
  }
]
```

### Generate Report
```
POST /api/reports/generate
```

**Request:**
```json
{
  "studio_id": 1,
  "report_type": "monthly",
  "period": "2024-01"
}
```

**Response:**
```json
{
  "message": "Report generated",
  "id": 1,
  "period": "2024-01"
}
```

### Get Report Details
```
GET /api/reports/{id}
```

### Export Report
```
GET /api/reports/{id}/export
```

---

## Error Responses

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

Saat ini tidak ada rate limiting. Akan ditambahkan di fase selanjutnya.

## Pagination

Akan diimplementasikan untuk endpoint yang mengembalikan banyak records.

## Webhooks

Akan disupport di fase selanjutnya untuk real-time integrations.

---

## Code Examples

### Python (Requests)
```python
import requests

BASE_URL = "http://localhost:8000/api"

# Get all employees
response = requests.get(f"{BASE_URL}/employees?studio_id=1")
employees = response.json()

# Create employee
employee_data = {
    "studio_id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "host",
    "salary_base": 2000000
}
response = requests.post(f"{BASE_URL}/employees", json=employee_data)
new_employee = response.json()
```

### JavaScript (Fetch)
```javascript
const BASE_URL = 'http://localhost:8000/api';

// Get employees
const employees = await fetch(`${BASE_URL}/employees?studio_id=1`)
  .then(r => r.json());

// Create employee
const newEmployee = await fetch(`${BASE_URL}/employees`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    studio_id: 1,
    name: 'John Doe',
    email: 'john@example.com',
    role: 'host',
    salary_base: 2000000
  })
}).then(r => r.json());
```

### cURL
```bash
# Get employees
curl -X GET "http://localhost:8000/api/employees?studio_id=1"

# Create employee
curl -X POST "http://localhost:8000/api/employees" \
  -H "Content-Type: application/json" \
  -d '{"studio_id":1,"name":"John","email":"john@example.com","role":"host","salary_base":2000000}'
```

---

## Version History

- **v0.1.0** (Current): Initial MVP
  - Basic CRUD for all entities
  - Commission calculation
  - Attendance tracking
  - Shopee account management
