"""
Test Reports API endpoint
"""
import requests
import json

# Login
login = requests.post('http://localhost:8000/api/auth/login', json={
    'username': 'admin',
    'password': 'Admin123!'
})

if login.status_code != 200:
    print(f"Login failed: {login.text}")
    exit(1)

token = login.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Test generate report
print("=" * 60)
print("Testing POST /api/reports/generate")
print("=" * 60)

payload = {
    "from_date": "2024-01-01",
    "to_date": "2024-01-31"
}

print(f"Payload: {json.dumps(payload, indent=2)}")

response = requests.post(
    'http://localhost:8000/api/reports/generate',
    json=payload,
    headers=headers
)

print(f"\nStatus: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code != 200:
    print("\n❌ ERROR - See detail above")
else:
    print("\n✅ SUCCESS")
    data = response.json()
    print(f"Summary: {data.get('summary')}")
    print(f"Data rows: {len(data.get('data', []))}")
