import requests
import sys

BASE_URL = "http://localhost:8000/api"

def login(username, password):
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "username": username,
        "password": password
    })
    if resp.status_code == 200:
        return resp.json()["access_token"]
    print(f"Login failed for {username}: {resp.status_code} {resp.text}")
    return None

def check_access(role, token):
    print(f"\n[{role.upper()}] Checking Read Access...")
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        f"{BASE_URL}/commissions/payout-history?from=2025-01-01&to=2025-01-31",
        f"{BASE_URL}/commissions/export-csv?from=2025-01-01&to=2025-01-31",
        f"{BASE_URL}/analytics/orders-hourly?date=2025-01-01",
        f"{BASE_URL}/shopee-accounts/?studio_id=1"
    ]

    for url in endpoints:
        endpoint_name = url.split("?")[0].split("/")[-1]
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            print(f"✅ {role} -> {endpoint_name}: 200 OK")
        elif resp.status_code == 403:
            print(f"❌ {role} -> {endpoint_name}: 403 Forbidden")
        else:
            print(f"⚠️ {role} -> {endpoint_name}: {resp.status_code} {resp.text}")

def check_write_access(role, token):
    print(f"[{role.upper()}] Checking Write Access (Bonus Upsert)...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to upsert a bonus rate (Write access)
    url = f"{BASE_URL}/bonus/rates/upsert"
    data = {"day_type": "weekday", "shift_id": 1, "bonus_per_order": 1000, "is_active": True}
    
    resp = requests.post(url, json=data, headers=headers)
    
    if resp.status_code == 200 or "created" in resp.text or "updated" in resp.text:
       print(f"✅ {role} -> bonus/upsert: Allowed (Success)")
    elif resp.status_code == 403:
       print(f"🔒 {role} -> bonus/upsert: Blocked (As Expected for Restricted)" if role in ['host', 'affiliate'] else f"❌ {role} -> bonus/upsert: 403 Forbidden (Unexpected!)")
    else:
       print(f"⚠️ {role} -> bonus/upsert: {resp.status_code} {resp.text}")


def main():
    admin_token = login("admin", "Admin123!")
    if not admin_token:
        print("Admin login failed, cannot proceed")
        return

    # Create test users
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    users_to_create = [
        {"username": "super_debug", "password": "password123", "email": "super_debug@test.com", "role": "Super Admin"}, # TEST NORMALIZATION
        {"username": "test_leader", "password": "password123", "email": "leader@test.com", "role": "leader"},
        {"username": "test_host", "password": "password123", "email": "host@test.com", "role": "host"}, 
        {"username": "test_owner", "password": "password123", "email": "owner@test.com", "role": "owner"}
    ]
    
    print("\nCreating/Updating Users...")
    for u in users_to_create:
        resp = requests.post(f"{BASE_URL}/users/", json=u, headers=headers)
        print(f"User {u['username']} creation: {resp.status_code} {resp.text}")
        
    # Now test each
    print("\nRunning RBAC Tests...")
    for u in users_to_create:
        # Normalize role for login lookup since we created it with weird casing, 
        # but locally we want to test if login WORKS with that weird role in DB
        login_role = u["role"]
        token = login(u["username"], u["password"])
        
        if token:
            check_access(u["role"], token)
            check_write_access(u["role"], token)
        else:
            print(f"Skipping {u['role']} due to login failure")

if __name__ == "__main__":
    main()
