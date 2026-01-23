@echo off
echo Starting Ticket System...

call .venv\Scripts\activate

set FLASK_APP=app.py
set FLASK_ENV=development
set FLASK_DEBUG=1

flask run

pause
