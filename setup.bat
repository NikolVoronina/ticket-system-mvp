@echo off
echo ===============================
echo Ticket System - Setup (Windows)
echo ===============================

REM 1. Create virtual environment
if not exist .venv (
    echo Creating virtual environment...
    py -m venv .venv
) else (
    echo Virtual environment already exists.
)

REM 2. Activate venv
call .venv\Scripts\activate

REM 3. Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM 4. Create .env if not exists
if not exist .env (
    echo Creating .env file...
    echo SECRET_KEY=dev-secret> .env
    echo DB_HOST=localhost>> .env
    echo DB_USER=root>> .env
    echo DB_PASSWORD=root>> .env
    echo DB_NAME=ticketsystem>> .env
    echo DB_PORT=3306>> .env
    echo .env created.
) else (
    echo .env already exists.
)

REM 5. Setup database
echo Setting up database...
mysql -u root -p < schema.sql

echo ===============================
echo Setup completed!
echo Run the app with run.bat
echo ===============================
pause
