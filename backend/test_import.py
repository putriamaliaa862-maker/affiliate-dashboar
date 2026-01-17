import requests
import json
import os

BASE_URL = "http://localhost:8000/api"
CSV_PATH = "shopee_sample.csv"

# 1. Login to get token
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

def test_preview(token):
    print("\nTesting CSV Preview...")
    files = {'file': open(CSV_PATH, 'rb')}
    headers = {'Authorization': f'Bearer {token}'}
    
    resp = requests.post(
        f"{BASE_URL}/import/csv/preview",
        headers=headers,
        files=files
    )
    
    if resp.status_code == 200:
        data = resp.json()
        print("✅ Preview Success!")
        print(f"Detected Type: {data['detected_type']}")
        print(f"Sample Rows: {len(data['sample_rows'])}")
        print(f"Mapping: {json.dumps(data['suggested_mapping'], indent=2)}")
        return data
    else:
        print("❌ Preview Failed:", resp.text)
        return None

def test_execute(token, preview_data):
    print("\nTesting CSV Execute...")
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Simulate frontend sending rows back (since we implemented that logic in ImportData.tsx)
    payload = {
        "shop_id": 1,
        "import_type": preview_data['detected_type'],
        "mapping": preview_data['suggested_mapping'],
        "rows": preview_data['sample_rows'] # We are only executing the sample for this test script, but frontend sends all
    }
    
    resp = requests.post(
        f"{BASE_URL}/import/csv/execute",
        headers=headers,
        json=payload
    )
    
    if resp.status_code == 200:
        res = resp.json()
        print("✅ Execute Success!")
        print(f"Inserted: {res['inserted']}")
        print(f"Updated: {res['updated']}")
        print(f"Failed: {res['failed']}")
        if res['failed_rows']:
            print("Failed Rows Detail:", res['failed_rows'])
    else:
        print("❌ Execute Failed:", resp.text)

if __name__ == "__main__":
    token = login()
    if token:
        preview = test_preview(token)
        if preview:
            # We need to ensure we read the CSV fully for execute if we were simulating real app, 
            # but for this test, we re-use sample_rows from preview which is enough to prove logic works.
            # In 'preview' endpoint, we returned dicts.
            
            # Actually, let's manually parse the CSV to "rows" to simulate what Frontend `parseCsvLocally` does
            # to be more rigorous.
            import csv
            with open(CSV_PATH, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            preview['sample_rows'] = rows # Replace sample with full rows
            test_execute(token, preview)
