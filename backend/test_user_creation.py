"""
Quick test to see user creation error
"""
import requests
import json

# Login first
login = requests.post('http://localhost:8000/api/auth/login', json={
    'username': 'admin',
    'password': 'Admin123!'
})

if login.status_code != 200:
    print(f"Login failed: {login.text}")
    exit(1)

token = login.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Try creating a user
user_data = {
    'username': 'testuser123',
    'email': 'testuser123@example.com',
    'password': 'TestPass123!',
    'role': 'affiliate',
    'leader_id': 1  # Assuming admin user ID is 1
}

print("Sending user data:")
print(json.dumps(user_data, indent=2))

response = requests.post(
    'http://localhost:8000/api/users',
    json=user_data,
    headers=headers
)

print(f"\nStatus: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 400:
    print("\n❌ 400 Bad Request - Check the error detail above")
elif response.status_code == 201:
    print("\n✅ User created successfully!")
