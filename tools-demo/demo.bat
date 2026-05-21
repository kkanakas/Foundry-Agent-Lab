@echo off
set "LOG_FILE="
if "%~1"=="log" set "LOG_FILE=%~dp0chat-log.txt"
if defined LOG_FILE call echo [Logging to %%LOG_FILE%%]
set "PY=%~dp0..\.venv\Scripts\python.exe"

echo === Running create_agent.py ===
"%PY%" "%~dp0create_agent.py"
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%

echo.
echo === Running chat.py ===
"%PY%" "%~dp0chat.py"
