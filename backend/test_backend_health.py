"""
Quick health check untuk backend
"""
import requests
import time

BASE_URL = "http://localhost:8000"

print("🔍 Testing Backend Health...\n")

# Test 1: Health endpoint
try:
    print("1️⃣ Testing /api/health...")
    response = requests.get(f"{BASE_URL}/api/health", timeout=5)
    print(f"   ✅ Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")
except requests.exceptions.Timeout:
    print("   ❌ TIMEOUT after 5 seconds\n")
except Exception as e:
    print(f"   ❌ ERROR: {e}\n")

# Test 2: Docs endpoint
try:
    print("2️⃣ Testing /docs...")
    response = requests.get(f"{BASE_URL}/docs", timeout=5)
    print(f"   ✅ Status: {response.status_code}")
    print(f"   Content length: {len(response.text)} bytes\n")
except requests.exceptions.Timeout:
    print("   ❌ TIMEOUT after 5 seconds\n")
except Exception as e:
    print(f"   ❌ ERROR: {e}\n")

# Test 3: Login endpoint
try:
    print("3️⃣ Testing POST /api/auth/login...")
    start = time.time()
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": "Admin123!"},
        timeout=20
    )
    elapsed = time.time() - start
    print(f"   ✅ Status: {response.status_code}")
    print(f"   Time: {elapsed:.2f}s")
    print(f"   Response: {response.json()}\n")
except requests.exceptions.Timeout:
    elapsed = time.time() - start
    print(f"   ❌ TIMEOUT after {elapsed:.2f} seconds\n")
except Exception as e:
    print(f"   ❌ ERROR: {e}\n")

print("✅ Health check selesai")
