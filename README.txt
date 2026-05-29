
                  VULNSCAN LITE - USER MANUAL & SETUP GUIDE

VulnScan Lite is an on-demand, passive web vulnerability scanner. This document
provides step-by-step instructions to connect to your databases/servers, start
the scanning backend, and use the application on Windows.

TABLE OF CONTENTS
1. Prerequisites & Installation
2. Connecting to Servers (Redis & Database)
3. Starting the Backend Services
4. How to Use the Application
5. Troubleshooting Common Issues

1. PREREQUISITES & INSTALLATION

Ensure you have Python 3.10+ installed on your Windows system.

Open a command prompt (cmd) or PowerShell, navigate to your project directory:
   cd c:\Users\yashwanth\Desktop\myflaskapp

Install all required Python dependencies:
   pip install flask flask-sqlalchemy flask-login celery redis flask-talisman flask-limiter requests beautifulsoup4

2. CONNECTING TO SERVERS (REDIS & DATABASE)


This application connects to two server backends:
1. SQLite Database: A local database stored in "instance/scans.db" for user accounts 
   and scan history.
2. Redis Server: Used as the Celery message broker and result backend (running on
   localhost, port 6379).

STARTING REDIS ON WINDOWS 
Redis must be running for Celery tasks to process. Choose ONE of these methods:

Method A: Run via WSL (Windows Subsystem for Linux) - Recommended
   If you have WSL/Ubuntu installed, open your WSL terminal and run:
   sudo service redis-server start

Method B: Run via Docker (if installed)
   Open your command prompt and run:
   docker run -d -p 6379:6379 redis:latest

Method C: Run native Windows Redis port (redis-server.exe)
   If you installed Memurai or the archive native redis-server, start it from 
   its installation directory.


3. STARTING THE BACKEND SERVICES

You need to run BOTH the Celery task worker and the Flask web server in separate
terminal windows.

STEP A: Start the Celery Worker (CRITICAL FOR WINDOWS!)
Open a new terminal, navigate to the project directory, and run the following
command:

   python -m celery -A app.celery worker --loglevel=info --pool=solo

* NOTE: The "--pool=solo" parameter is absolutely mandatory on Windows. Without 
  it, Celery will not execute scans and will hang indefinitely.
* IMPORTANT: If you change any scanner Python code, you must stop Celery 
  (Ctrl+C) and restart it for changes to take effect.


STEP B: Initialize the Database (One-time setup)

In a command prompt, run:

   python -c "from app import db; db.create_all()"

If you already have a database but need to apply schema upgrades, run:

   python migrate_db.py


STEP C: Start the Flask Web Server
Open another terminal, navigate to the project directory, and run:

   python -m flask --app app run --debug

The Flask app will start and listen on: http://127.0.0.1:5000/

4. HOW TO USE THE APPLICATION

1. Open your web browser and navigate to:
   http://127.0.0.1:5000/auth

2. Sign Up & Log In:
   - If you do not have an account, enter a username and password, then click 
     "Sign Up".
   - Use the "Login" tab to log in with your credentials.
   - If you forget your password, click "Forgot Password" to reset it.

3. Scanning a Website:
   - On the "New Scan" tab, enter a website URL.
   - You MUST include the protocol (e.g., http:// or https://), for example:
     https://google.com
   - Click "Scan Target".
   - The scanner will initialize, display status updates (e.g., PENDING, 
     SUCCESS), and render the results once finished.

4. Website Not Found Indicator:
   - If you scan a domain that does not exist or is unreachable (e.g., 
     http://doesnotexist.invalid), the system will display a red alert box
     stating: "Website is not found".
   - The overall Grade will drop to "F" and the security score to "0/100".

5. View History & Reports:
   - Under the "Scan History" tab, view your past scans, their final scores, 
     grades, and timestamps.
   - On any active scan report page, click the "Export PDF" button to print or
     save the security report as a clean PDF document.

5. TROUBLESHOOTING COMMON ISSUES

* Issue: Scans get stuck in "PENDING..." or "Status: PENDING..." forever.
  - Solution: Your Celery worker is either not running, or was started without 
    the "--pool=solo" parameter. Open a command prompt and start it:
    python -m celery -A app.celery worker --loglevel=info --pool=solo

* Issue: "ConnectionError: Error 10061 connecting to localhost:6379."
  - Solution: The Redis server is not running or is blocked. Ensure Redis is 
    started (e.g., `sudo service redis-server start` in WSL, or via Docker).

* Issue: "TemplateSyntaxError: expected token 'end of print statement'..."
  - Solution: This happens when Jinja2 syntax collides with React curly braces 
    in HTML. Ensure React blocks in html templates are enclosed within 
    {% raw %} and {% endraw %} tags.

* Issue: Scanner results seem outdated or code changes are not showing up.
  - Solution: Celery caches tasks in memory. Always restart the Celery worker 
    terminal (Ctrl+C and run the command again) whenever you modify Python fill
                             End of User Manual
