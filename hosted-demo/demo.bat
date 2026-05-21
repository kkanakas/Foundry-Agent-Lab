@echo off
set "LOG_FILE="
if "%~1"=="log" set "LOG_FILE=%~dp0chat-log.txt"
if defined LOG_FILE call echo [Logging to %%LOG_FILE%%]
set "PY=%~dp0..\.venv\Scripts\python.exe"

echo === Starting hosted agent server ===
start /b "" cmd /c ""%PY%" "%~dp0main.py" >nul 2>&1"

:: Wait for the server to be ready
timeout /t 3 /nobreak >nul
echo Server running on http://localhost:8088

echo.
echo === Running chat.py ===
"%PY%" "%~dp0chat.py"

:: Stop the server when chat exits
taskkill /f /fi "WINDOWTITLE eq *main.py*" >nul 2>&1
