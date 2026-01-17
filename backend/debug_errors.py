"""
Debug Reports & Commissions errors
"""
import requests
import traceback

BASE_URL = "http://localhost:8000"

# Login
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"username": "admin", "password": "Admin123!"}
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Test Reports dengan detail error
print("Testing Reports...")
try:
    r = requests.get(f"{BASE_URL}/api/reports/summary", headers=headers, timeout=5)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:500]}")
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()

print("\n" + "="*50 + "\n")

# Test Commissions dengan detail error
print("Testing Commissions...")
try:
    r = requests.get(f"{BASE_URL}/api/commissions", headers=headers, timeout=5)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:500]}")
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
