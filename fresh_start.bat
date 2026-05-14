@echo off
echo ==============================================
echo  Arnetrice V2 - Fresh Start Script
echo ==============================================

REM 1) Kill any running Python/Uvicorn processes
echo Killing old Python/Uvicorn processes...
FOR /F "tokens=5" %%P IN ('netstat -ano ^| find ":8000" ^| find "LISTENING"') DO taskkill /F /PID %%P >nul 2>&1
tasklist | find "python" >nul
IF %ERRORLEVEL%==0 (
    taskkill /F /IM python.exe >nul 2>&1
    echo [OK] Python processes terminated.
) ELSE (
    echo [INFO] No running Python processes found.
)

REM 2) Purge all .pyc files and __pycache__ folders
echo Purging .pyc files and __pycache__ folders...
powershell -Command "Get-ChildItem -Recurse -Include *.pyc | Remove-Item -Force"
powershell -Command "Get-ChildItem -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force"
echo [OK] Purge complete.

REM 3) Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate

REM 4) Start uvicorn with reload SCOPED to source directories.
REM    Without --reload-dir, uvicorn watches everything including static/dist/output.css,
REM    so every Tailwind rebuild triggers a Python reload. Watching only app/, templates/,
REM    and content/ eliminates that race condition.
echo Starting server with scoped reload watch...
uvicorn app.main:app --reload --reload-dir app --reload-dir templates --reload-dir content --host 0.0.0.0 --port 8000

pause
