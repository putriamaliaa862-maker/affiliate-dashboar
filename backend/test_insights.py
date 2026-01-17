import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def login():
    print("Login...")
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin",
        "password": "Admin123!"
    })
    if resp.status_code == 200:
        return resp.json()["access_token"]
    else:
        print("Login failed:", resp.text)
        return None

def test_daily_summary(token):
    print("\n[TEST] Daily Summary...")
    today = datetime.now().strftime("%Y-%m-%d")
    
    headers = {'Authorization': f'Bearer {token}'}
    resp = requests.get(f"{BASE_URL}/insights/daily-summary?date=2025-12-16", headers=headers)
    
    if resp.status_code == 200:
        data = resp.json()
        print("✅ OK")
        print(f"KPI: {data['kpi']}")
        print(f"Notes: {data['notes']}")
    else:
        print(f"❌ Failed: {resp.status_code} - {resp.text}")

def test_daily_insights(token):
    print("\n[TEST] Daily Insights...")
    headers = {'Authorization': f'Bearer {token}'}
    resp = requests.get(f"{BASE_URL}/insights/daily?date=2025-12-16", headers=headers)
    
    if resp.status_code == 200:
        data = resp.json()
        print("✅ OK")
        print(f"Warnings: {len(data['warnings'].get('products_drop_sharp', []))}")
        print(f"Action Items: {len(data['action_items'])}")
    else:
        print(f"❌ Failed: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    token = login()
    if token:
        test_daily_summary(token)
        test_daily_insights(token)
