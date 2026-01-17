"""
Debug script to test JWT token verification.
Run this to see if the token verification is working correctly.
"""
from app.auth.jwt import verify_token, create_access_token, decode_token
from app.config import settings
from datetime import datetime

# Create a test token
test_payload = {
    "sub": 1,
    "username": "admin",
    "role": "super_admin"
}

print("=" * 60)
print("JWT TOKEN VERIFICATION DEBUG")
print("=" * 60)

# Create token
token = create_access_token(test_payload)
print(f"\n1. Created Token:")
print(f"   {token[:50]}...")

# Decode without verification (to see contents)
from jose import jwt as jose_jwt
decoded_no_verify = jose_jwt.decode(token, key="", options={"verify_signature": False})
print(f"\n2. Decoded (without verification):")
print(f"   {decoded_no_verify}")

# Verify token
verified = verify_token(token)
print(f"\n3. Verified Token:")
if verified:
    print(f"   ✅ SUCCESS")
    print(f"   Payload: {verified}")
else:
    print(f"   ❌ FAILED - Token returned None")

# Check expiration
if verified:
    exp = verified.get("exp")
    if exp:
        exp_time = datetime.fromtimestamp(exp)
        now = datetime.utcnow()
        print(f"\n4. Expiration Check:")
        print(f"   Expires at: {exp_time}")
        print(f"   Current time: {now}")
        print(f"   Expired: {now > exp_time}")
        print(f"   Time left: {(exp_time - now).total_seconds()} seconds")

# Check secret key
print(f"\n5. SECRET_KEY:")
print(f"   {settings.secret_key}")

print("\n" + "=" * 60)
