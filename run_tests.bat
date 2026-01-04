@echo off
REM ===========================================
REM AI Smart Finance - Playwright UI Tests
REM ===========================================
REM
REM Chạy script này để test UI với Playwright
REM 
REM Prerequisites:
REM 1. Django server phải đang chạy: python manage.py runserver 8000
REM 2. Access code đã được set: python manage.py init_access_code 1234
REM
REM Usage:
REM   run_tests.bat           - Chạy tất cả tests (headless)
REM   run_tests.bat headed    - Chạy với browser hiển thị
REM   run_tests.bat slow      - Chạy chậm để xem browser
REM ===========================================

set PYTHON_PATH=C:\Users\ADMIN\anaconda3\envs\taichinh\python.exe

REM Kiểm tra Docker services
echo [1/3] Checking if Django server is running on port 8000...
netstat -an | findstr ":8000" > nul
if errorlevel 1 (
    echo [ERROR] Django server is not running!
    echo Please start it first: %PYTHON_PATH% manage.py runserver 8000
    exit /b 1
)
echo [OK] Django server is running

REM Chạy tests
echo [2/3] Running Playwright UI tests...
echo.

if "%1"=="headed" (
    echo Mode: HEADED (browser visible)
    %PYTHON_PATH% -m pytest tests/ --headed -p no:django -v
) else if "%1"=="slow" (
    echo Mode: SLOW MOTION (browser visible, 500ms delay)
    %PYTHON_PATH% -m pytest tests/ --headed --slowmo=500 -p no:django -v
) else (
    echo Mode: HEADLESS (default)
    %PYTHON_PATH% -m pytest tests/ -p no:django -v
)

echo.
echo [3/3] Tests completed!
if errorlevel 1 (
    echo [RESULT] Some tests FAILED
) else (
    echo [RESULT] All tests PASSED
)

