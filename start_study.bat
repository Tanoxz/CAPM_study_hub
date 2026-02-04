@echo off
REM ABOUTME: One-click launcher for CAPM Study Hub
REM ABOUTME: Starts Streamlit server (if needed) and opens browser

title CAPM Study Hub

REM Check if Streamlit is already running on port 8501
netstat -ano | findstr ":8501" | findstr "LISTENING" > nul
if %errorlevel% == 0 (
    echo Server already running, opening browser...
    start "" http://localhost:8501
    exit
)

echo ========================================
echo    CAPM Study Hub
echo ========================================
echo.
echo Starting server... (keep this window open)
echo.

REM Change to app directory
cd /d "%~dp0app"

REM Open browser after 4 second delay (in separate process)
start "" /min powershell -WindowStyle Hidden -Command "Start-Sleep -Seconds 4; Start-Process 'http://localhost:8501'"

REM Start Streamlit (this blocks and keeps window open)
python -m streamlit run app.py --server.headless true

REM If we get here, server stopped
echo.
echo Server stopped. Press any key to close.
pause > nul
