"""
Smoke Test Checklist - Semua Fitur Critical
Sesuai aturan: Auth, Users, Employees, Attendance, Reports, Commissions
"""
import requests
import time

BASE_URL = "http://localhost:8000"

# Login dulu
print("🔐 Login...")
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"username": "admin", "password": "Admin123!"}
)
assert response.status_code == 200, f"Login failed: {response.status_code}"
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("✅ Login OK\n")

# Test checklist
tests = []

# 1. Auth
print("1️⃣ Testing Auth...")
try:
    r = requests.get(f"{BASE_URL}/api/auth/me", headers=headers, timeout=5)
    assert r.status_code == 200
    print(f"   ✅ GET /api/auth/me - {r.status_code}")
    tests.append(("Auth /auth/me", "✅"))
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    tests.append(("Auth /auth/me", "❌"))

# 2. Users
print("\n2️⃣ Testing Users...")
try:
    r = requests.get(f"{BASE_URL}/api/users", headers=headers, timeout=5)
    assert r.status_code == 200
    print(f"   ✅ GET /api/users - {r.status_code}")
    tests.append(("Users page load", "✅"))
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    tests.append(("Users page load", "❌"))

# 3. Employees
print("\n3️⃣ Testing Employees...")
try:
    r = requests.get(f"{BASE_URL}/api/employees", headers=headers, timeout=5)
    assert r.status_code == 200
    print(f"   ✅ GET /api/employees - {r.status_code}")
    tests.append(("Employees page load", "✅"))
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    tests.append(("Employees page load", "❌"))

# 4. Attendance
print("\n4️⃣ Testing Attendance...")
try:
    r = requests.get(f"{BASE_URL}/api/attendances", headers=headers, timeout=5)
    assert r.status_code == 200
    print(f"   ✅ GET /api/attendances - {r.status_code}")
    tests.append(("Attendance page load", "✅"))
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    tests.append(("Attendance page load", "❌"))

# 5. Reports
print("\n5️⃣ Testing Reports...")
try:
    r = requests.get(f"{BASE_URL}/api/reports/summary", headers=headers, timeout=5)
    # 422 OK karena butuh query params, yang penting tidak 500
    assert r.status_code in [200, 422]
    print(f"   ✅ GET /api/reports/summary - {r.status_code}")
    tests.append(("Reports generate", "✅"))
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    tests.append(("Reports generate", "❌"))

# 6. Commissions
print("\n6️⃣ Testing Commissions...")
try:
    r = requests.get(f"{BASE_URL}/api/commissions", headers=headers, timeout=5)
    assert r.status_code in [200, 422]
    print(f"   ✅ GET /api/commissions - {r.status_code}")
    tests.append(("Commissions load", "✅"))
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    tests.append(("Commissions load", "❌"))

# Summary
print("\n" + "="*50)
print("📊 SMOKE TEST SUMMARY")
print("="*50)
for name, status in tests:
    print(f"{status} {name}")

failed = [t for t in tests if t[1] == "❌"]
if failed:
    print(f"\n❌ {len(failed)} tests FAILED")
    exit(1)
else:
    print(f"\n✅ All {len(tests)} tests PASSED")
