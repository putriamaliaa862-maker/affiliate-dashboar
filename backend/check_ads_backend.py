import requests
import json
from datetime import date

API_URL = "http://localhost:8000/api"

# Login as Super Admin (assuming default exists or I can use one)
def login(username, password):
    resp = requests.post(f"{API_URL}/auth/login", data={"username": username, "password": password})
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        return None
    return resp.json()["access_token"]

def check_ads_center():
    token = login("superuser", "admin123") # Assuming superuser exists
    if not token: 
        print("Cannot login, skipping test")
        return

    headers = {"Authorization": f"Bearer {token}"}
    today = date.today().strftime("%Y-%m-%d")

    print("\n--- 1. Testing GET /api/ads/center ---")
    resp = requests.get(f"{API_URL}/ads/center", params={"date": today}, headers=headers)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Accounts returned: {len(data)}")
        if len(data) > 0:
            print(f"Sample: {data[0]}")
            acc_id = data[0]['account_id']
    else:
        print(resp.text)
        return

    acc_id = 1 # Force use account 1 if exists, or use from list
    if resp.status_code == 200 and len(resp.json()) > 0:
        acc_id = resp.json()[0]['account_id']
    
    print(f"\n--- 2. Testing POST /api/ads/spend/upsert on Account {acc_id} ---")
    payload = {
        "date": today,
        "account_id": acc_id,
        "spend_amount": 500000,
        "spend_type": "audience",
        "note": "Test Spend"
    }
    resp = requests.post(f"{API_URL}/ads/spend/upsert", json=payload, headers=headers)
    print(f"Status: {resp.status_code} - {resp.text}")

    print("\n--- 3. Testing POST /api/ads/audience/add-budget ---")
    payload = {
        "date": today,
        "account_id": acc_id,
        "added_amount": 100000,
        "remaining_before": 2000
    }
    resp = requests.post(f"{API_URL}/ads/audience/add-budget", json=payload, headers=headers)
    print(f"Status: {resp.status_code} - {resp.text}")

    # Test Gap
    print("\n--- 4. Testing Gap Protection (Should Fail) ---")
    resp = requests.post(f"{API_URL}/ads/audience/add-budget", json=payload, headers=headers)
    print(f"Status: {resp.status_code} - {resp.text}")
    
    if resp.status_code == 409:
        print("✅ Gap protection working!")
    else:
        print("❌ Gap protection failed!")

if __name__ == "__main__":
    check_ads_center()
