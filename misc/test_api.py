#!/usr/bin/env python
"""
Test script untuk Affiliate Dashboard API
Jalankan: python test_api.py
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api"

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def test_studios():
    """Test Studio endpoints"""
    print_header("TEST: STUDIOS")
    
    # Create studio
    print("1. Creating studio...")
    studio_data = {
        "name": "Studio Jakarta 1",
        "location": "Jakarta Pusat",
        "description": "Main affiliate studio"
    }
    response = requests.post(f"{BASE_URL}/studios", json=studio_data)
    print(f"Status: {response.status_code}")
    studio = response.json()
    print(json.dumps(studio, indent=2))
    studio_id = studio.get("id", 1)
    
    # List studios
    print("\n2. Listing all studios...")
    response = requests.get(f"{BASE_URL}/studios")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    return studio_id

def test_employees(studio_id):
    """Test Employee endpoints"""
    print_header("TEST: EMPLOYEES")
    
    employees_data = [
        {
            "studio_id": studio_id,
            "name": "John Host 1",
            "email": "john1@example.com",
            "phone": "081111111111",
            "role": "host",
            "salary_base": 2000000,
            "hire_date": "2024-01-01T00:00:00"
        },
        {
            "studio_id": studio_id,
            "name": "Jane Host 2",
            "email": "jane2@example.com",
            "phone": "081111111112",
            "role": "host",
            "salary_base": 2000000,
            "hire_date": "2024-01-01T00:00:00"
        },
        {
            "studio_id": studio_id,
            "name": "Mike Leader",
            "email": "mike@example.com",
            "phone": "081111111113",
            "role": "leader",
            "salary_base": 3000000,
            "hire_date": "2024-01-01T00:00:00"
        },
        {
            "studio_id": studio_id,
            "name": "Sarah Supervisor",
            "email": "sarah@example.com",
            "phone": "081111111114",
            "role": "supervisor",
            "salary_base": 4000000,
            "hire_date": "2024-01-01T00:00:00"
        },
        {
            "studio_id": studio_id,
            "name": "CEO Director",
            "email": "ceo@example.com",
            "phone": "081111111115",
            "role": "director",
            "salary_base": 5000000,
            "hire_date": "2024-01-01T00:00:00"
        },
    ]
    
    employee_ids = []
    for i, emp_data in enumerate(employees_data):
        print(f"{i+1}. Creating employee: {emp_data['name']}")
        response = requests.post(f"{BASE_URL}/employees", json=emp_data)
        print(f"   Status: {response.status_code}")
        employee = response.json()
        employee_ids.append(employee.get("id", i+1))
        print(f"   ID: {employee.get('id')}, Name: {employee.get('name')}")
    
    # List employees
    print(f"\n6. Listing all employees for studio {studio_id}...")
    response = requests.get(f"{BASE_URL}/employees?studio_id={studio_id}")
    print(f"   Status: {response.status_code}")
    print(f"   Total employees: {len(response.json())}")
    
    return employee_ids

def test_attendance(employee_ids):
    """Test Attendance endpoints"""
    print_header("TEST: ATTENDANCE")
    
    # Single attendance
    print("1. Recording single attendance...")
    today = datetime.now()
    attendance_data = {
        "employee_id": employee_ids[0],
        "date": today.isoformat(),
        "check_in": today.replace(hour=9, minute=0).isoformat(),
        "check_out": today.replace(hour=17, minute=0).isoformat(),
        "status": "present",
        "notes": "On time"
    }
    response = requests.post(f"{BASE_URL}/attendances", json=attendance_data)
    print(f"   Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # Bulk attendance
    print("\n2. Recording bulk attendance...")
    bulk_data = {
        "attendances": [
            {
                "employee_id": eid,
                "date": today.isoformat(),
                "check_in": today.replace(hour=9, minute=0).isoformat(),
                "check_out": today.replace(hour=17, minute=0).isoformat(),
                "status": "present"
            }
            for eid in employee_ids
        ]
    }
    response = requests.post(f"{BASE_URL}/attendances/bulk", json=bulk_data)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Created: {result.get('created')} records")
    
    # List attendance
    print(f"\n3. Listing attendance for employee {employee_ids[0]}...")
    response = requests.get(f"{BASE_URL}/attendances?employee_id={employee_ids[0]}")
    print(f"   Status: {response.status_code}")
    print(f"   Total records: {len(response.json())}")

def test_shopee_accounts(studio_id):
    """Test Shopee Account endpoints"""
    print_header("TEST: SHOPEE ACCOUNTS")
    
    accounts_data = [
        {
            "studio_id": studio_id,
            "account_name": "Toko Aku 1",
            "shopee_account_id": "shopee_12345",
            "access_token": "mock_token_123",
            "refresh_token": "mock_refresh_123"
        },
        {
            "studio_id": studio_id,
            "account_name": "Toko Aku 2",
            "shopee_account_id": "shopee_67890",
            "access_token": "mock_token_456",
            "refresh_token": "mock_refresh_456"
        }
    ]
    
    account_ids = []
    for i, acc_data in enumerate(accounts_data):
        print(f"{i+1}. Creating Shopee account: {acc_data['account_name']}")
        response = requests.post(f"{BASE_URL}/shopee-accounts", json=acc_data)
        print(f"   Status: {response.status_code}")
        account = response.json()
        account_ids.append(account.get("id", i+1))
    
    # List accounts
    print(f"\n3. Listing all Shopee accounts for studio {studio_id}...")
    response = requests.get(f"{BASE_URL}/shopee-accounts?studio_id={studio_id}")
    print(f"   Status: {response.status_code}")
    print(f"   Total accounts: {len(response.json())}")
    
    return account_ids

def test_commissions(studio_id):
    """Test Commission endpoints"""
    print_header("TEST: COMMISSIONS")
    
    # Calculate commissions
    period = datetime.now().strftime("%Y-%m")
    print(f"1. Calculating commissions for period {period}...")
    commission_data = {
        "studio_id": studio_id,
        "period": period
    }
    response = requests.post(f"{BASE_URL}/commissions/calculate", json=commission_data)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Created: {result.get('created')} commission records")
    
    # List commissions
    print(f"\n2. Listing commissions for period {period}...")
    response = requests.get(f"{BASE_URL}/commissions?period={period}")
    print(f"   Status: {response.status_code}")
    print(f"   Total commissions: {len(response.json())}")
    
    # Get summary
    print(f"\n3. Getting commission summary for period {period}...")
    response = requests.get(f"{BASE_URL}/commissions/summary/{period}?studio_id={studio_id}")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))

def test_reports(studio_id):
    """Test Report endpoints"""
    print_header("TEST: REPORTS")
    
    # Generate report
    period = datetime.now().strftime("%Y-%m")
    print(f"1. Generating monthly report for period {period}...")
    report_data = {
        "studio_id": studio_id,
        "report_type": "monthly",
        "period": period
    }
    response = requests.post(f"{BASE_URL}/reports/generate", json=report_data)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    
    # List reports
    print(f"\n2. Listing all reports for studio {studio_id}...")
    response = requests.get(f"{BASE_URL}/reports?studio_id={studio_id}")
    print(f"   Status: {response.status_code}")
    reports = response.json()
    print(f"   Total reports: {len(reports)}")
    
    if reports:
        print(f"\n3. Getting report details (ID: {reports[0]['id']})...")
        response = requests.get(f"{BASE_URL}/reports/{reports[0]['id']}")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  AFFILIATE DASHBOARD API TEST SUITE")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)
    
    try:
        # Test health check
        print("\nChecking API health...")
        response = requests.get(f"http://localhost:8000/health")
        if response.status_code == 200:
            print(f"✓ API is healthy: {response.json()}")
        else:
            print(f"✗ API health check failed. Is the server running on localhost:8000?")
            return
        
        # Run tests
        studio_id = test_studios()
        employee_ids = test_employees(studio_id)
        test_attendance(employee_ids)
        account_ids = test_shopee_accounts(studio_id)
        test_commissions(studio_id)
        test_reports(studio_id)
        
        print("\n" + "="*60)
        print("  ✓ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Cannot connect to API server")
        print("   Make sure backend is running: python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
