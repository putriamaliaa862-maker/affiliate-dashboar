import requests
import sys

BASE_URL = "http://localhost:8000"

def login(username, password):
    response = requests.post(f"{BASE_URL}/api/auth/login", json={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()["access_token"]
    print(f"Login failed: {response.status_code} {response.text}")
    return None

def test_endpoint(token, endpoint):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
    print(f"GET {endpoint} -> {response.status_code}")
    if response.status_code != 200:
        print(f"Response: {response.text}")

def main():
    # Login as Super Admin (assuming username 'test_super', password 'password123' from previous context)
    # If not exists, I might need to create it or use existing 'admin'
    
    print("Testing Super Admin access...")
    token = login("test_super", "password123")
    if not token:
        # Try 'admin' just in case
        print("Retrying with 'admin'...")
        token = login("admin", "Admin123!")
    
    if token:
        test_endpoint(token, "/api/commissions/payout-history?from=2025-12-17&to=2026-01-16")
        test_endpoint(token, "/api/commissions/export-csv?from=2025-12-17&to=2026-01-16")
    else:
        print("Could not get token.")

if __name__ == "__main__":
    main()
