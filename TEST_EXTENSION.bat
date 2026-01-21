@echo off
echo ========================================
echo TEST EXTENSION SYNC ENDPOINT
echo ========================================
echo.
echo Testing POST /api/shopee-data/sync with identity payload...
echo.

curl -X POST http://localhost:8000/api/shopee-data/sync ^
  -H "Content-Type: application/json" ^
  -H "X-Access-Code: TEST_CODE_HERE" ^
  -d "{\"account\":{\"shopee_account_id\":\"affiliate_123456\",\"shop_name\":\"Test Shop\",\"username\":\"testuser\"},\"type\":\"identity\",\"data\":{\"shopee_account_id\":\"affiliate_123456\"}}"

echo.
echo ========================================
echo If you see 200 OK, backend is working!
echo If 401, check your Access Code
echo If 400, check payload format
echo ========================================
pause
