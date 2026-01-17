"""
Test script for Employee API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

# First, login to get token
print("=" * 60)
print("STEP 1: Login as admin")
print("=" * 60)
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"username": "admin", "password": "Admin123!"}
)
print(f"Status: {login_response.status_code}")

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Token obtained: {token[:20]}...")
else:
    print(f"❌ Login failed: {login_response.text}")
    exit(1)

# Test GET /api/employees
print("\n" + "=" * 60)
print("STEP 2: GET /api/employees (List)")
print("=" * 60)
get_response = requests.get(f"{BASE_URL}/employees", headers=headers)
print(f"Status: {get_response.status_code}")
if get_response.status_code == 200:
    employees = get_response.json()
    print(f"✅ Found {len(employees)} employees")
    if employees:
        print(f"First employee: {json.dumps(employees[0], indent=2)}")
    else:
        print("(List is empty)")
else:
    print(f"❌ Failed: {get_response.text}")

# Test POST /api/employees
print("\n" + "=" * 60)
print("STEP 3: POST /api/employees (Create)")
print("=" * 60)
new_employee = {
    "studio_id": 1,
    "name": "John Doe Test",
    "email": f"john.test.{requests.utils.default_user_agent()}@example.com"[:50],
    "phone": "08123456789",
    "role": "host",
    "salary_base": 5000000
}
print(f"Payload: {json.dumps(new_employee, indent=2)}")

post_response = requests.post(
    f"{BASE_URL}/employees",
    headers=headers,
    json=new_employee
)
print(f"Status: {post_response.status_code}")
if post_response.status_code == 201:
    created = post_response.json()
    employee_id = created["id"]
    print(f"✅ Employee created with ID: {employee_id}")
    print(json.dumps(created, indent=2))
else:
    print(f"❌ Failed: {post_response.text}")
    employee_id = None

# Test GET single employee
if employee_id:
    print("\n" + "=" * 60)
    print(f"STEP 4: GET /api/employees/{employee_id} (Get One)")
    print("=" * 60)
    get_one = requests.get(f"{BASE_URL}/employees/{employee_id}", headers=headers)
    print(f"Status: {get_one.status_code}")
    if get_one.status_code == 200:
        print(f"✅ Retrieved employee:")
        print(json.dumps(get_one.json(), indent=2))
    else:
        print(f"❌ Failed: {get_one.text}")

    # Test PUT
    print("\n" + "=" * 60)
    print(f"STEP 5: PUT /api/employees/{employee_id} (Update)")
    print("=" * 60)
    update_data = {"name": "John Doe UPDATED", "role": "leader"}
    put_response = requests.put(
        f"{BASE_URL}/employees/{employee_id}",
        headers=headers,
        json=update_data
    )
    print(f"Status: {put_response.status_code}")
    if put_response.status_code == 200:
        print(f"✅ Employee updated:")
        print(json.dumps(put_response.json(), indent=2))
    else:
        print(f"❌ Failed: {put_response.text}")

    # Test DELETE
    print("\n" + "=" * 60)
    print(f"STEP 6: DELETE /api/employees/{employee_id} (Soft Delete)")
    print("=" * 60)
    delete_response = requests.delete(
        f"{BASE_URL}/employees/{employee_id}",
        headers=headers
    )
    print(f"Status: {delete_response.status_code}")
    if delete_response.status_code == 200:
        print(f"✅ Employee deleted:")
        print(json.dumps(delete_response.json(), indent=2))
    else:
        print(f"❌ Failed: {delete_response.text}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
