"""
Test Shopee Sync Endpoint
Tests API key authentication and data storage
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/shopee-data"
API_KEY = "dev-sync-key-12345"

print("🧪 Testing Shopee Sync Endpoint\n")
print("="*60)

# Test 1: Without API Key (should fail)
print("\n1️⃣ Test: Sync without API key (should return 401)")
try:
    response = requests.post(f"{BASE_URL}/sync", json={
        "timestamp": "2026-01-17T10:00:00Z",
        "url": "https://shopee.co.id/test",
        "type": "transactions",
        "accountId": "test",
        "payload": {}
    })
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 401, "Should return 401 without API key"
    print("   ✅ PASS - Correctly rejected without API key")
except Exception as e:
    print(f"   ❌ FAIL: {e}")

# Test 2: With wrong API Key (should fail)
print("\n2️⃣ Test: Sync with wrong API key (should return 401)")
try:
    response = requests.post(
        f"{BASE_URL}/sync",
        headers={"X-Sync-Key": "wrong-key"},
        json={
            "timestamp": "2026-01-17T10:00:00Z",
            "url": "https://shopee.co.id/test",
            "type": "transactions",
            "accountId": "test",
            "payload": {}
        }
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 401, "Should return 401 with wrong API key"
    print("   ✅ PASS - Correctly rejected with wrong API key")
except Exception as e:
    print(f"   ❌ FAIL: {e}")

# Test 3: Transactions sync (should succeed)
print("\n3️⃣ Test: Sync transactions with correct API key")
try:
    payload = {
        "timestamp": "2026-01-17T10:00:00Z",
        "url": "https://shopee.co.id/shop/yeyep_store",
        "type": "transactions",
        "accountId": "yeyep_store_123",
        "sessionToken": "SPC_EC_test_token",
        "payload": {
            "shop_name": "YEYEP STORE",
            "transactions": [
                {
                    "orderId": "ORDER_TEST_001",
                    "amount": 150000,
                    "commission": 7500,
                    "status": "completed",
                    "date": "2026-01-17T09:00:00Z",
                    "product_name": "Test Product 1"
                },
                {
                    "orderId": "ORDER_TEST_002",
                    "amount": 250000,
                    "commission": 12500,
                    "status": "completed",
                    "date": "2026-01-17T10:00:00Z",
                    "product_name": "Test Product 2"
                }
            ]
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/sync",
        headers={"X-Sync-Key": API_KEY},
        json=payload
    )
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Response: {json.dumps(result, indent=2)}")
    
    assert response.status_code == 200, f"Should return 200, got {response.status_code}"
    assert result["success"] == True, "Should be successful"
    assert result["account_name"] == "YEYEP STORE", f"Account name should be 'YEYEP STORE', got '{result['account_name']}'"
    assert result["created"] == 2, f"Should create 2 orders, created {result['created']}"
    
    print("   ✅ PASS - Transactions synced successfully")
    print(f"   ✅ Account: {result['account_name']} (ID: {result['account_id']})")
    print(f"   ✅ Created: {result['created']}, Updated: {result['updated']}, Skipped: {result['skipped']}")
except Exception as e:
    print(f"   ❌ FAIL: {e}")

# Test 4: Affiliate dashboard metrics
print("\n4️⃣ Test: Sync affiliate dashboard metrics")
try:
    payload = {
        "timestamp": "2026-01-17T10:05:00Z",
        "url": "https://affiliate.shopee.co.id/dashboard",
        "type": "affiliate_dashboard",
        "accountId": "yeyep_store_123",
        "payload": {
            "shop_name": "YEYEP STORE",
            "totalCommission": 1500000,
            "pendingCommission": 500000,
            "paidCommission": 1000000,
            "clicks": 2500,
            "conversions": 150
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/sync",
        headers={"X-Sync-Key": API_KEY},
        json=payload
    )
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Response: {json.dumps(result, indent=2)}")
    
    assert response.status_code == 200, f"Should return 200, got {response.status_code}"
    assert result["success"] == True, "Should be successful"
    
    print("   ✅ PASS - Affiliate metrics synced successfully")
except Exception as e:
    print(f"   ❌ FAIL: {e}")

# Test 5: Live streaming data
print("\n5️⃣ Test: Sync live streaming data")
try:
    payload = {
        "timestamp": "2026-01-17T10:10:00Z",
        "url": "https://live.shopee.co.id/session/123",
        "type": "live_streaming",
        "accountId": "yeyep_store_123",
        "payload": {
            "shop_name": "YEYEP STORE",
            "viewers": 5000,
            "likes": 1200,
            "totalSales": 150,
            "revenue": 25000000,
            "duration": "2:30:00"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/sync",
        headers={"X-Sync-Key": API_KEY},
        json=payload
    )
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Response: {json.dumps(result, indent=2)}")
    
    assert response.status_code == 200, f"Should return 200, got {response.status_code}"
    assert result["success"] == True, "Should be successful"
    
    print("   ✅ PASS - Live streaming data synced successfully")
except Exception as e:
    print(f"   ❌ FAIL: {e}")

# Test 6: Check status endpoint
print("\n6️⃣ Test: Check sync status endpoint")
try:
    response = requests.get(
        f"{BASE_URL}/status",
        headers={"X-Sync-Key": API_KEY}
    )
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Response: {json.dumps(result, indent=2)}")
    
    assert response.status_code == 200, f"Should return 200, got {response.status_code}"
    assert result["status"] == "online", "Status should be online"
    
    print("   ✅ PASS - Status endpoint working")
except Exception as e:
    print(f"   ❌ FAIL: {e}")

print("\n" + "="*60)
print("✅ All tests completed!")
print("\nNext: Verify data in database")
