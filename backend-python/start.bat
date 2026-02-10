@echo off
echo Starting SSTCP Maintenance System Backend (Python)...

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Start the server
echo Starting server on http://localhost:8080
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

pause
