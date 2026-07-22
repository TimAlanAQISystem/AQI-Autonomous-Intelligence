@echo off
setlocal
cd /d C:\Users\signa\OneDrive\Desktop\Agent X

set PYTHON_EXE=C:\Users\signa\OneDrive\Desktop\Agent X\.venv\Scripts\python.exe
set LOG_DIR=C:\Users\signa\OneDrive\Desktop\Agent X\governance_runs\scheduler_logs
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd-HHmmss"') do set TS=%%i
set LOG_FILE=%LOG_DIR%\readiness_cycle_%TS%.log

"%PYTHON_EXE%" tools\run_governance_pipeline.py --append-rrg --operator-notes "Scheduled governance pipeline run" >> "%LOG_FILE%" 2>&1
exit /b %errorlevel%
