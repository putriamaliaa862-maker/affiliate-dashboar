@echo off
REM ========================================
REM EXTENSION CLEANUP SCRIPT
REM Cleans duplicate extension folders
REM ========================================

echo.
echo ========================================
echo EXTENSION FOLDER CLEANUP
echo ========================================
echo.

cd /d "C:\workspace\affiliate-dashboard"

echo [1/4] Creating backup...
set TIMESTAMP=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%
set TIMESTAMP=%TIMESTAMP: =0%
if not exist "_trash_extensions" mkdir "_trash_extensions"

echo [2/4] Moving duplicate folders to _trash_extensions...
if exist "shopee-scraper-extension" (
    echo   - Moving shopee-scraper-extension...
    move "shopee-scraper-extension" "_trash_extensions\shopee-scraper-extension_%TIMESTAMP%" >nul 2>&1
)
if exist "extension-temp" (
    echo   - Moving extension-temp...
    move "extension-temp" "_trash_extensions\extension-temp_%TIMESTAMP%" >nul 2>&1
)
if exist "temp_ext" (
    echo   - Moving temp_ext...
    move "temp_ext" "_trash_extensions\temp_ext_%TIMESTAMP%" >nul 2>&1
)
if exist "dist\extension" (
    echo   - Moving dist\extension...
    move "dist\extension" "_trash_extensions\dist_extension_%TIMESTAMP%" >nul 2>&1
)

echo [3/4] Verifying active extension folder...
if exist "extension\manifest.json" (
    echo   ✓ extension\manifest.json exists
) else (
    echo   ✗ WARNING: extension\manifest.json not found!
)
if exist "extension\popup\popup.html" (
    echo   ✓ extension\popup\popup.html exists
) else (
    echo   ✗ WARNING: extension\popup\popup.html not found!
)
if exist "extension\background\service-worker.js" (
    echo   ✓ extension\background\service-worker.js exists
) else (
    echo   ✗ WARNING: extension\background\service-worker.js not found!
)
if exist "extension\content\shopee-scraper.js" (
    echo   ✓ extension\content\shopee-scraper.js exists
) else (
    echo   ✗ WARNING: extension\content\shopee-scraper.js not found!
)

echo.
echo [4/4] CLEANUP COMPLETE!
echo.
echo ========================================
echo ACTIVE EXTENSION FOLDER:
echo C:\workspace\affiliate-dashboard\extension
echo ========================================
echo.
echo Next steps:
echo 1. Open chrome://extensions
echo 2. Enable Developer Mode
echo 3. Click "Load unpacked"
echo 4. Select: C:\workspace\affiliate-dashboard\extension
echo 5. Reload if already loaded
echo.
pause
